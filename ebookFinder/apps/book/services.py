import asyncio
import urllib.parse
from bs4 import BeautifulSoup, Tag
import httpx
import logging
from tenacity import retry, stop_after_attempt, retry_if_exception_type, after_log

from django.core.exceptions import ObjectDoesNotExist

from ebookFinder.apps.book.consts import KAKAO_API_KEY, SEARCH_API_ENDPOINT, USER_AGENT, \
    BOOK_STORES, AFFILIATE_API_ENDPOINT, AFFILIATE_ID
from ebookFinder.apps.book import schemas
from ebookFinder.apps.utils.eb_datetime import tz_now

logger = logging.getLogger('django')

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


async def get_ebooks_info(isbn: str, title: str) -> list[schemas.Ebook]:
    if '-' in isbn:
        isbns = isbn.split('-')
    else:
        isbns = [isbn]

    result = []
    tasks = [asyncio.create_task(
        (ScrapEbookByTitle() if STORE['name'] == 'ridi' else ScrapEbookByISBN()).get_ebook_info(isbns, title, STORE)) for STORE in BOOK_STORES
    ]
    result = [res for res in await asyncio.gather(*tasks) if res]
    return result


async def get_deeplink(url: str) -> str:
    """
    스토어 url을 받아서 제휴 사이트 딥링크를 생성
    """
    params = {'a_id': AFFILIATE_ID, 'url': url, 'mode': 'json'}
    query = urllib.parse.urlencode(params)
    api_url = AFFILIATE_API_ENDPOINT + "?" + query

    deeplink = ''
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(api_url)
            if res.status_code == 200:
                deeplink = res.json()['url']
        except (httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            logger.error(f"{tz_now().isoformat()} msg:{f'{e.__class__} on get_deeplink'} url:{api_url}")
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

    async def _get_response(self, params: dict, headers: dict = None, endpoint: str = SEARCH_API_ENDPOINT, **kwargs) -> httpx.Response:
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

    async def _get_response(self, url: str, headers: dict = None, **kwargs) -> httpx.Response:
        if headers is None:
            headers = self.headers
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, **kwargs)
            if res.status_code != 200:
                res.raise_for_status()
        return res
    
    async def get_ebook_info(self, isbns: list, title:str, store: dict) -> schemas.Ebook:
        """
        스토어 상품에서 ebook 정보를 가져옴
        """
        good = await self.get_valid_good(store, isbns=isbns, title=title)
        link_element = await self.get_ebook_link(good, store)
        if not link_element:
            return {}

        res = await self.get_ebook_detail(link_element, store)
        return res
    
    async def get_valid_good(self, store: dict, **kwargs) -> Tag | None:
        """
        스토어 리스트에서 검색 가능한 첫번째 상품 정보를 가져옴
        """
        raise NotImplementedError
        
    
    async def get_ebook_link(self, good: Tag | None, store: dict) -> Tag | None:
        """
        스토어 상품 태그에서 ebook 링크를 가져옴
        """
        if not good:
            return None
        
        link_element = good.select_one(store['link_selector']) if 'link_selector' in store else good.find('a', string=store['keyword'])
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
    
    async def get_ebook_detail(self, link_element: Tag, store: dict) -> schemas.Ebook:
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
        return schemas.Ebook(**res)

    @retry(retry=retry_if_exception_type(httpx.ConnectTimeout), stop=stop_after_attempt(2), retry_error_callback=lambda *args:None, reraise=False, after=after_log(logger, logging.ERROR))
    async def get_good(self, url: str, store: dict) -> Tag | None:
        """
        스토어 리스트에서 검색하여 첫번째 상품 정보를 가져옴
        """
        try:
            res = await self._get_response(url, timeout=10 if store['name'] == 'aladin' else 5)
        except httpx.ReadTimeout as e:
            logger.error(f"{tz_now().isoformat()} msg:{f'{e.__class__} on get_good'} url:{url}")
            return None
 
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
    async def create_dummy_bs_tag(good: dict, store: dict) -> Tag:
        """
        json 형태의 상품 정보를 BeautifulSoup 태그로 변환
        """
        good["b_id"]
        good = BeautifulSoup(f"<li><a href={store['link_format'] % good[store['link_id_name']]}>{good['price']}</li>", 'html.parser')
        return good
    

class ScrapEbookByISBN(ScrapEbook):
    async def get_valid_good(self, store: dict, isbns: list = None, **kwargs) -> Tag | None:
        base = store['domain'] + store['base']
        params_list = [{store['param_key']: isbn} for isbn in isbns]
        query_list = [urllib.parse.urlencode(params) for params in params_list]
        url_list = ["?".join([base, query]) for query in query_list]

        tasks = [asyncio.create_task(self.get_good(url, store)) for url in url_list]
        goods = await asyncio.gather(*tasks)
        
        while goods:
            good = goods.pop()
            if good:
                break
        return good


class ScrapEbookByTitle(ScrapEbook):
    async def get_valid_good(self, store: dict, title: str = '', **kwargs) -> Tag | None:
        base = store['domain'] + store['base']
        params = {store['param_key']: title}
        query = urllib.parse.urlencode(params)
        url = "?".join([base, query])
        good = await self.get_good(url, store)
        return good