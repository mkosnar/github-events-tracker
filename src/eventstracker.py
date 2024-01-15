import configparser
import datetime
from collections import defaultdict
from typing import Optional

from src.api import request_data
from src.stats import average_dt_difference


class EventsTracker:
    def __init__(self, config: configparser.ConfigParser):
        self.event_page_limit = config.getint('Limits', 'max_pages')
        self.event_age_limit = config.getint('Limits', 'max_days')
        self.repos = config.get('Github', 'repos', fallback='').split(',')

    def _get_repo_event_times(self,
                              repo: str,
                              from_time: Optional[datetime.datetime] = None,
                              ) -> dict[str, list[datetime.datetime]]:
        event_time_limit = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=self.event_age_limit)
        data = defaultdict(list)
        request_url = f'https://api.github.com/repos/{repo}/events?page=1&per_page=100'
        for page in range(1, self.event_page_limit+1):
            data_page, request_url = request_data(request_url)
            for event in data_page:
                event_time = datetime.datetime.fromisoformat(event['created_at'])
                if (from_time and event_time < from_time) or event_time < event_time_limit:
                    return dict(data)
                data[event['type']].append(event_time)
            if not request_url:
                break
        return dict(data)

    def get_average_event_times(self,
                                from_time: Optional[datetime.datetime] = None,
                                ) -> dict[str, dict[str, float]]:
        ret = dict()
        for repo in self.repos:
            event_times = self._get_repo_event_times(repo, from_time)
            repo_averages = {event: average_dt_difference(times) for event, times in event_times.items()
                             if len(times) > 1}
            ret[repo] = repo_averages
        return ret
