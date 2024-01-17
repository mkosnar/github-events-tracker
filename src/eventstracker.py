import configparser
import datetime
from collections import defaultdict
from typing import Union

from src.api import request_data
from src.cache import CacheData
from src.stats import average_dt_difference


class EventsTracker:
    def __init__(self, config: configparser.ConfigParser):
        """

        Args:
            config: parsed config file
        """
        self.event_page_limit = config.getint('Limits', 'max_pages')
        self.event_age_limit = config.getint('Limits', 'max_days')
        self.repos = config.get('Github', 'repos', fallback='').split(',')
        self.auth_token = config.get('Github', 'auth_token')

        self.cache = CacheData(config.get('General', 'cache_dir_path'))
        self.data = {repo: self.cache.data.get(repo, []) for repo in self.repos}

    def handle_request(self) -> list[dict]:
        """
        Updates data, creates and returns the response body.

        Returns:
            output json list
        """
        self.update_data()
        return self.create_response()

    def create_response(self) -> list[dict]:
        """
        Calculates average event delay and creates a json-y response from stored data.

        Returns:
            output json list
            [
                {
                    'repo': str,
                    'average_event_delays': [
                        {
                            'event_type': str,
                            'average_delay': float
                        },
                        ...
                    ]
                },
                ...
            ]
        """
        ret = list()
        for repo, events in self.data.items():
            event_times = defaultdict(list)
            for event in events:
                event_times[event['event_type']].append(event['created_at'])

            repo_dict = {'repo': repo,
                         'average_event_delays': [{'type': event_type, 'average_delay': average_dt_difference(times)}
                                                  for event_type, times in event_times.items()
                                                  if len(times) > 1],
                         }
            ret.append(repo_dict)
        return ret

    def update_data(self):
        """
        Updates data stored in memory with new events retrieved from Github API considering event count + age limits.
        """
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
        """
        Retrieves event data for given repo from Github API.
        Only returns data for events created after the given time.

        Args:
            repo: in {user}/{repo} format
            min_created_at: minimal created_at time limit

        Returns:
            list of useful event data (id, type, created_at)
        """
        ret = list()
        request_url = f'https://api.github.com/repos/{repo}/events?page=1&per_page=100'
        for page in range(self.event_page_limit):
            data_page, request_url = request_data(request_url, self.auth_token)
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
