import asyncio
import httpx
import urllib.parse
from bs4 import BeautifulSoup
from ebookFinder.apps.book.consts import KAKAO_API_KEY, SEARCH_API_ENDPOINT, USER_AGENT, \
    BOOK_STORES, AFFILIATE_API_ENDPOINT, AFFILIATE_ID

async def search_books(q) -> dict:
    headers = {
        'User-agent': USER_AGENT,
        'referer': '',
        'Authorization': 'KakaoAK {api_key}'.format(api_key=KAKAO_API_KEY)
    }

    params = {"page": 1, "size": 50, "query": q}
    query = urllib.parse.urlencode(params)
    api_url = SEARCH_API_ENDPOINT + "?" + query

    async with httpx.AsyncClient() as client:
        res = await client.get(api_url, headers=headers)
        if res.status_code != 200:
            res.raise_for_status()
        res = res.json()
        books_meta = res.get('meta', {})
        books = res.get('documents', [])

    return {
        'books_meta': books_meta,
        'books': books,
    }


async def get_book_info(isbn) -> dict:
    headers = {
        'User-agent': USER_AGENT,
        'referer': '',
        'Authorization': 'KakaoAK {api_key}'.format(api_key=KAKAO_API_KEY)
    }

    params = {"page": 1, "size": 1, "query": isbn}
    query = urllib.parse.urlencode(params)
    api_url = SEARCH_API_ENDPOINT + "?" + query
    
    async with httpx.AsyncClient() as client:
        res = await client.get(api_url, headers=headers)
        if res.status_code != 200:
            res.raise_for_status()

        res = res.json().get('documents')
        if res is None:
            raise ValueError('Search API not working')
        elif not res:
            raise ValueError('Can not find isbn')
    return res[0]


async def get_ebooks_info(isbn: str) -> list:
    if '-' in isbn:
        isbns = isbn.split('-')
    else:
        raise ValueError('Invalid isbn!')

    headers = {
        'User-agent': USER_AGENT,
    }

    result = []
    tasks = [asyncio.create_task(get_ebook_info(isbns, headers, STORE)) for STORE in BOOK_STORES]
    result = [res for res in await asyncio.gather(*tasks) if res]
    return result


async def get_ebook_info(isbns: list, headers: dict, store: dict) -> dict:
    result = {}
    base = store['domain'] + store['base']

    params_list = [{store['param_key']: isbn} for isbn in isbns]
    query_list = [urllib.parse.urlencode(params) for params in params_list]
    url_list = ["?".join([base, query]) for query in query_list]

    tasks = [asyncio.create_task(get_good(url, store, headers)) for url in url_list]
    goods = await asyncio.gather(*tasks)
    
    if not any(goods):
        return result
    
    good = goods[0] or goods[1] or None

    link_element = good.select_one(store['link_selector']) if 'link_selector' in store else good.find('a', text=store['keyword'])

    if link_element is None:
        links = good.select('a')
        for a in links:
            if a.string is None:
                for s in a.stripped_strings:
                    if s == store['keyword']:
                        link_element = a
    
    if link_element is None:
        link_element = good.find('a', {'title': store['keyword']})

    if link_element:
        href = link_element.get('href', '') if link_element else ''
        store_url = store['domain']
        result['book_store'] = store['name']
        url = store_url + href if 'http' not in href else href
        result['url'] = url
        result['deeplink'] = await get_deeplink(url)

        price_element = link_element.parent
        price_str = price_element.text.split('원')[0].split(' ')[-1].replace(',', '').strip()
        try:
            result['price'] = int(price_str) if price_str else 0
        except ValueError:
            result['price'] = 0
    return result

async def get_good(url: str, store: dict, headers: dict = None):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        good = soup.select_one(
                store['good_selector']
            )
    return good


async def get_deeplink(url) -> str:
    params = {'a_id': AFFILIATE_ID, 'url': url, 'mode': 'json'}
    query = urllib.parse.urlencode(params)
    api_url = AFFILIATE_API_ENDPOINT + "?" + query

    async with httpx.AsyncClient() as client:
        res = await client.get(api_url)
        try:
            deeplink = res.json()['url']
            if deeplink is None:
                deeplink = ''
        except Exception:
            deeplink = ''
    return deeplink