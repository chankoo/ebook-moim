import requests
import urllib.parse
from bs4 import BeautifulSoup
from ebookFinder.apps.book.consts import KAKAO_API_KEY, SEARCH_API_ENDPOINT, USER_AGENT, BOOK_STORES


def search_books(data) -> dict:
    headers = {
        'User-agent': USER_AGENT,
        'referer': None,
        'Authorization': 'KakaoAK {api_key}'.format(api_key=KAKAO_API_KEY)
    }

    q = data.get('query', '')
    params = {"page": 1, "size": 50, "query": q}
    query = urllib.parse.urlencode(params)
    api_url = SEARCH_API_ENDPOINT + "?" + query

    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        raise Exception('Search API Failed')
    res = res.json()
    books_meta = res.get('meta', {})
    books = res.get('documents', [])

    return {
        'books_meta': books_meta,
        'books': books,
    }


def get_book_info(isbn) -> dict:
    headers = {
        'User-agent': USER_AGENT,
        'referer': None,
        'Authorization': 'KakaoAK {api_key}'.format(api_key=KAKAO_API_KEY)
    }

    params = {"page": 1, "size": 1, "query": isbn}
    query = urllib.parse.urlencode(params)
    api_url = SEARCH_API_ENDPOINT + "?" + query
    res = requests.get(api_url, headers=headers).json().get('documents')
    if res is None:
        raise ValueError('Search API not working')
    elif not res:
        raise ValueError('Can not find isbn')
    return res[0]


def get_ebooks_info(isbn) -> list:
    if '-' in isbn:
        isbns = isbn.split('-')
    else:
        raise ValueError('Invalid isbn!')

    headers = {
        'User-agent': USER_AGENT,
    }

    result = []
    good = None
    for STORE in BOOK_STORES:
        base = STORE['domain'] + STORE['base']

        for isbn in isbns:
            params = {STORE['param_key']: isbn}
            query = urllib.parse.urlencode(params)
            url = "?".join([base, query])
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            good = soup.select_one(
                STORE['good_selector']
            )
            if good:
                break

        if good is None:
            raise ValueError('The good not exist!')
        links = good.select('a')

        res = None
        for a in links:
            if a.string is None:
                for s in a.stripped_strings:
                    if s == STORE['keyword']:
                        res = a

        if res is None:
            res = good.find('a', {'title': STORE['keyword']})

        if res:
            href = res.get('href', '') if res else ''
            store_url = STORE['domain']
            info = {}
            info['book_store'] = STORE['name']
            info['url'] = store_url + href if 'http' not in href else href
            result.append(info)
    return result
