import logging
import re
from typing import Optional

import requests


def request_data(url: str, auth_token: Optional[str] = None) -> tuple[list[dict], Optional[str]]:
    headers = {'Authorization': f'Bearer {auth_token}'} if auth_token else {}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logging.error(f'{exc}')
        return list(), None
    else:
        return resp.json(), get_next_page_url(resp)


def get_next_page_url(response: requests.Response) -> Optional[str]:
    if match := re.search(r'<([^<>]+)>; rel="next"', response.headers['Link']):
        return match.group(1)
    else:
        return None
