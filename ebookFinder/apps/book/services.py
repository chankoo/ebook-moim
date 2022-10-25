import asyncio

import requests
import urllib.parse
from bs4 import BeautifulSoup
from icecream import ic


async def get_ebook_page_async(isbn: str, headers: dict, store: dict):
    base = store['domain'] + store['base']
    params = {store['param_key']: isbn}
    query = urllib.parse.urlencode(params)
    url = "?".join([base, query])
    res = requests.get(url, headers=headers)
    ic(res)
    return res


async def parse_ebook_page_async(res, store: dict):
    soup = BeautifulSoup(res.text, 'html.parser')
    ic(len(soup))
    good = soup.select_one(
        store['good_selector']
    )


async def get_ebook_info_async(isbns: list, headers: dict, store: dict):
    done, pending = await asyncio.wait(
        [get_ebook_page_async(isbn, headers, store) for isbn in isbns]
    )
    ic(done)
    ic(pending)
