import asyncio
import urllib.parse

from bs4 import BeautifulSoup, Tag
import httpx
import logging
from tenacity import retry, stop_after_attempt, retry_if_exception_type, after_log

from ebookFinder.core.utils import get_response
from ebookFinder.apps.utils.eb_datetime import tz_now
from ebookFinder.apps.book.exceptions import NotMatchingTitleException

logger = logging.getLogger(__name__)


class ScrapOperator:
    def __init__(
        self,
        headers: dict = None,
    ) -> None:
        super().__init__()
        self.headers = headers

    async def get_valid_good(self, store: dict, **kwargs) -> Tag | None:
        """
        스토어 리스트에서 검색 가능한 첫번째 상품 정보를 가져옴
        """
        raise NotImplementedError


class JsonFromTitleScraper(ScrapOperator):
    async def get_valid_good(
        self, store: dict, title: str = "", **kwargs
    ) -> Tag | None:
        base = store["domain"] + store["base"]
        params = {store["param_key"]: title}
        query = urllib.parse.urlencode(params)
        url = "?".join([base, query])
        good = await self.get_good(url, store)
        self.is_valid_title(good, title)
        good = await self._create_dummy_bs_tag(good, store)
        return good

    @retry(
        retry=retry_if_exception_type(httpx.ConnectTimeout),
        stop=stop_after_attempt(2),
        retry_error_callback=lambda *args: None,
        reraise=False,
        after=after_log(logger, logging.ERROR),
    )
    async def get_good(self, url: str, store: dict) -> dict | None:
        """
        스토어 리스트에서 검색하여 첫번째 상품 정보를 가져옴
        """
        try:
            res = await get_response(
                url,
                headers=self.headers,
                timeout=10 if store["name"] == "aladin" else 5,
            )
        except httpx.ReadTimeout as e:
            logger.error(
                f"{tz_now().isoformat()} msg:{f'{e.__class__} on get_good'} url:{url}"
            )
            return None

        return await self._get_good_from_json(content=res.json(), store=store)

    async def _get_good_from_json(self, content: dict, store: dict) -> Tag | None:
        good = (
            content[store["good_selector"]][0]
            if content[store["good_selector"]]
            else None
        )
        return good

    @staticmethod
    async def _create_dummy_bs_tag(good: dict, store: dict) -> Tag:
        """
        json 형태의 상품 정보를 BeautifulSoup 태그로 변환
        """
        good = BeautifulSoup(
            f"<li><a href={store['link_format'] % good[store['link_id_name']]}>{good['price']}</li>",
            "html.parser",
        )
        return good

    def is_valid_title(self, good: dict, expected: str):
        if not good:
            return None
        if "title" in good and good["title"][:5] != expected[:5]:
            raise NotMatchingTitleException(good["title"])


class HtmlFromISBNScraper(ScrapOperator):
    async def get_valid_good(
        self, store: dict, isbns: list = None, **kwargs
    ) -> Tag | None:
        base = store["domain"] + store["base"]
        params_list = [{store["param_key"]: isbn} for isbn in isbns]
        query_list = [urllib.parse.urlencode(params) for params in params_list]
        url_list = ["?".join([base, query]) for query in query_list]

        tasks = [asyncio.create_task(self.get_good(url, store)) for url in url_list]
        goods = await asyncio.gather(*tasks)

        while goods:
            good = goods.pop()
            if good:
                break
        return good

    @retry(
        retry=retry_if_exception_type(httpx.ConnectTimeout),
        stop=stop_after_attempt(2),
        retry_error_callback=lambda *args: None,
        reraise=False,
        after=after_log(logger, logging.ERROR),
    )
    async def get_good(self, url: str, store: dict) -> Tag | None:
        """
        스토어 리스트에서 검색하여 첫번째 상품 정보를 가져옴
        """
        try:
            res = await get_response(
                url,
                headers=self.headers,
                timeout=10 if store["name"] == "aladin" else 5,
            )
        except httpx.ReadTimeout as e:
            logger.error(
                f"{tz_now().isoformat()} msg:{f'{e.__class__} on get_good'} url:{url}"
            )
            return None

        return await self._get_good_from_html(content=res.text, store=store)

    async def _get_good_from_html(self, content: str, store: dict) -> Tag | None:
        soup = BeautifulSoup(content, "html.parser")
        good = soup.select_one(store["good_selector"])
        return good
