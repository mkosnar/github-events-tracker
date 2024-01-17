import logging
import re
from typing import Optional

import requests


def request_data(url: str, auth_token: Optional[str] = None) -> tuple[list[dict], Optional[str]]:
    """
    Request data from given URL, optionally adding an authorization header.

    Args:
        url:
        auth_token: optional authorization token

    Returns:
        requested data, next data page url
    """
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
    """
    Parses URL for the next page of data from response headers.

    Args:
        response: response object from latest request

    Returns:
        next page url
    """
    if match := re.search(r'<([^<>]+)>; rel="next"', response.headers['Link']):
        return match.group(1)
    else:
        return None
