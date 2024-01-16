import configparser
import datetime
from collections import defaultdict
from typing import Union

from src.api import request_data
from src.cache import CacheData
from src.stats import average_dt_difference


class EventsTracker:
    def __init__(self, config: configparser.ConfigParser):
        self.event_page_limit = config.getint('Limits', 'max_pages')
        self.event_age_limit = config.getint('Limits', 'max_days')
        self.repos = config.get('Github', 'repos', fallback='').split(',')
        self.cache = CacheData(config.get('General', 'cache_dir_path'))
        self.data = {repo: self.cache.data.get(repo, []) for repo in self.repos}

    def handle_request(self) -> dict[str, dict[str, float]]:
        self.update_data()
        return self.create_response()

    def create_response(self) -> dict[str, dict[str, float]]:
        ret = dict()
        for repo, events in self.data.items():
            event_times = defaultdict(list)
            for event in events:
                event_times[event['type']].append(event['created_at'])

            ret[repo] = {event_type: average_dt_difference(times)
                         for event_type, times in event_times.items()
                         if len(times) > 1}
        return ret

    def update_data(self):
        event_count_limit = self.event_page_limit * 100
        event_age_limit = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=self.event_age_limit)
        for repo in self.repos:
            old_repo_data = self.data[repo]
            latest_cached = max((event_data['created_at'] for event_data in old_repo_data), default=None)
            new_data_cutoff_time = max(latest_cached, event_age_limit) if latest_cached else event_age_limit
            new_repo_data = self._get_repo_event_data(repo, new_data_cutoff_time)
            combined_repo_data = [*new_repo_data, *old_repo_data]
            self.data[repo] = [event for event in combined_repo_data[:event_count_limit]
                               if event['created_at'] >= event_age_limit]
        self.cache.store(self.data)

    def _get_repo_event_data(self,
                             repo: str,
                             min_created_at: datetime.datetime,
                             ) -> list[dict[str, Union[str, datetime.datetime]]]:
        ret = list()
        request_url = f'https://api.github.com/repos/{repo}/events?page=1&per_page=100'
        for page in range(self.event_page_limit):
            data_page, request_url = request_data(request_url)
            for event in data_page:
                event_time = datetime.datetime.fromisoformat(event['created_at'])
                if event_time <= min_created_at:
                    return ret
                ret.append({'id': event['id'],
                            'type': event['type'],
                            'created_at': datetime.datetime.fromisoformat(event['created_at'])})
            if not request_url:
                break

        return ret
