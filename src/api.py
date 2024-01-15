import logging

import requests


def request_data(repo: str, page: int) -> list[dict]:
    try:
        resp = requests.get(f'https://api.github.com/repos/{repo}/events?page={page}&per_page=100', timeout=5)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logging.error(f'{exc}')
        return list()
    else:
        return resp.json()


