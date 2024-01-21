import asyncio
import httpx
import urllib.parse
from bs4 import BeautifulSoup
import urllib.parse

from django.core.exceptions import ObjectDoesNotExist

from ebookFinder.apps.book.consts import KAKAO_API_KEY, SEARCH_API_ENDPOINT, USER_AGENT, \
    BOOK_STORES, AFFILIATE_API_ENDPOINT, AFFILIATE_ID

async def search_books(q) -> dict:
    kakao = SearchBookKakao()
    res = await kakao.get_search(q)
    res = res.json()
    return {
        'books_meta': res.get('meta', {}),
        'books': res.get('documents', []),
    }


async def get_book_info(isbn: str) -> dict:
    kakao = SearchBookKakao()
    res = await kakao.get_book(isbn)
    res = res.json().get('documents')
    
    if res is None:
        raise Exception('Search API not working')
    elif not res:
        raise ObjectDoesNotExist('Can not find isbn')
    return res[0]


async def get_ebooks_info(isbn: str, title: str) -> list:
    if '-' in isbn:
        isbns = isbn.split('-')
    else:
        raise ValueError('Invalid isbn!')

    result = []
    tasks = [asyncio.create_task(ScrapEbook().get_ebook_info(isbns, title, STORE)) for STORE in BOOK_STORES]
    result = [res for res in await asyncio.gather(*tasks) if res]
    return result


async def get_deeplink(url: str) -> str:
    """
    스토어 url을 받아서 제휴 사이트 딥링크를 생성
    """
    params = {'a_id': AFFILIATE_ID, 'url': url, 'mode': 'json'}
    query = urllib.parse.urlencode(params)
    api_url = AFFILIATE_API_ENDPOINT + "?" + query

    async with httpx.AsyncClient() as client:
        res = await client.get(api_url)
        try:
            deeplink = res.json()['url']
        except Exception:
            deeplink = None
    return deeplink or ''


class SearchBook(object):
    def __init__(self, headers: dict):
        self.headers = headers

    async def get_search(self, *args, **kwargs):
        raise NotImplementedError
    
    async def get_book(self, *args, **kwargs):
        raise NotImplementedError


class SearchBookKakao(SearchBook):
    def __init__(self, headers: dict = None):
        headers = headers or {
            'User-agent': USER_AGENT,
            'referer': '',
            'Authorization': 'KakaoAK {api_key}'.format(api_key=KAKAO_API_KEY)
        }
        super().__init__(headers)

    async def _get_response(self, params: dict, headers: dict = None, endpoint: str = SEARCH_API_ENDPOINT, **kwargs):
        if headers is None:
            headers = self.headers
        query = urllib.parse.urlencode(params)
        api_url = endpoint + "?" + query
        
        async with httpx.AsyncClient() as client:
            res = await client.get(api_url, headers=headers, **kwargs)
            if res.status_code != 200:
                res.raise_for_status()
        return res
    
    async def get_search(self, q) -> httpx.Response:
        res = await self._get_response(params={"page": 1, "size": 50, "query": q})
        return res
    
    async def get_book(self, isbn: str) -> httpx.Response:
        res = await self._get_response(params={"page": 1, "size": 1, "query": isbn})
        return res
    

class ScrapEbook(object):
    def __init__(self, headers: dict = None):
        self.headers = headers or {
            'User-agent': USER_AGENT,
        }

    async def _get_response(self, url: str, headers: dict = None, **kwargs):
        if headers is None:
            headers = self.headers

        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, **kwargs)
            if res.status_code != 200:
                res.raise_for_status()
        return res
    
    async def get_ebook_info(self, isbns: list, title:str, store: dict) -> dict:
        """
        스토어 상품에서 ebook 정보를 가져옴
        """
        good = await self.get_valid_good(isbns, title, store)
        link_element = await self.get_ebook_link(good, store)
        if not link_element:
            return {}

        res = await self.get_ebook_detail(link_element, store)
        return res
    
    async def get_valid_good(self, isbns: list, title:str, store: dict) -> BeautifulSoup | None:
        """
        스토어 리스트에서 검색 가능한 첫번째 상품 정보를 가져옴
        """
        base = store['domain'] + store['base']
        params_list = [{store['param_key']: isbn} for isbn in isbns + [title]]
        query_list = [urllib.parse.urlencode(params) for params in params_list]
        url_list = ["?".join([base, query]) for query in query_list]

        tasks = [asyncio.create_task(self.get_good(url, store)) for url in url_list]
        goods = await asyncio.gather(*tasks)
        
        while goods:
            good = goods.pop()
            if good:
                break
        return good
    
    async def get_ebook_link(self, good: BeautifulSoup, store: dict) -> BeautifulSoup | None:
        """
        스토어 상품 태그에서 ebook 링크를 가져옴
        """
        if not good:
            return None
        
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
        return link_element
    
    async def get_ebook_detail(self, link_element: BeautifulSoup, store: dict):
        """
        ebook 링크 태그에서 상세 정보를 추출
        """
        res = {}
        href = link_element.get('href', '') if link_element else ''
        store_url = store['domain']
        res['book_store'] = store['name']
        url = store_url + href if 'http' not in href else href
        res['url'] = url
        res['deeplink'] = await get_deeplink(url)

        price_element = link_element.parent
        price_str = price_element.text.split('원')[0].split(' ')[-1].replace(',', '').strip()
        try:
            res['price'] = int(price_str) if price_str else 0
        except ValueError:
            res['price'] = 0
        return res

    async def get_good(self, url: str, store: dict) -> BeautifulSoup | None:
        """
        스토어 리스트에서 검색하여 첫번째 상품 정보를 가져옴
        """
        
        # timeout 으로 인한 cancellation 우회
        res = await self._get_response(url, timeout=20 if store['name'] == 'aladin' else 10)
 
        if 'json' in res.headers['content-type']:
            data = res.json()
            good = data[store['good_selector']][0] if data[store['good_selector']] else None
            if good:
                good = await self.create_dummy_bs_tag(good, store)
        else:
            soup = BeautifulSoup(res.text, 'html.parser')
            good = soup.select_one(
                store['good_selector']
            )
        return good

    @staticmethod
    async def create_dummy_bs_tag(good: dict, store: dict) -> BeautifulSoup:
        """
        json 형태의 상품 정보를 BeautifulSoup 태그로 변환
        """
        good["b_id"]
        good = BeautifulSoup(f"<li><a href={store['link_format'] % good[store['link_id_name']]}>{good['price']}</li>", 'html.parser')
        return good
    