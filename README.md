# github-events-tracker

The application generates statistics based on a rolling window of either 7 days or 500 events (customizable in config), whichever is less.
Specifically, the API will show the average time between consecutive events, separately for each combination of event type and repository name.

Data is cached in memory to minimize the amount of requests to Github API and also in a file to retain data through application restarts.

* Installation
  1. Requirements
     * using pipenv (https://pypi.org/project/pipenv/)
       1. install pipenv
       2. run `pipenv sync` in project root directory
     * else
       * project uses `requests` and `Flask`
  2. Configuration
     * cache_dir_path - where the cache file will be created
     * max_pages - limits the floating window event count, 100 events per page
     * max_days - limits the floating window event age
     * auth_token - optional Github authorization token, provides private repo access and bigger rate limits
     * repos - tracked repos, `{owner}/{repo}` format, `,` separated list
  3. Run
     * `flask run` in project root directory to start server
     * output is provided at http://127.0.0.1:5000/averages


* output JSON example
```json
[
    {
        "repo": "owner1/repo1",
        "average_event_delays": [
            {
                "event_type": "ForkEvent",
                "average_delay": 1.5
            },
            {
                "event_type": "WatchEvent",
                "average_delay": 100.3
            }
        ]
    },
    {
        "repo": "owner2/repo2",
        "average_event_delays": [
            {
                "event_type": "IssueCommentEvent",
                "average_delay": 0.5
            },
            {
                "event_type": "WatchEvent",
                "average_delay": 1000.45
            }
        ]
    }
]
```

* possible future work
  * asynchronous caching
  * currently, events are checked for uniqueness using the created_at time. it would be better to use event IDs