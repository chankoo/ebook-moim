import pytest

from bs4 import Tag
from ebookFinder.apps.book.services import (
    ScrapEbook,
)
from ebookFinder.apps.book.consts import BOOK_STORES
from ebookFinder.apps.book.schemas import Ebook
from ebookFinder.apps.book.operations import JsonFromTitleScraper, HtmlFromISBNScraper
from ebookFinder.apps.book.exceptions import NotMatchingTitleException

ISBN = "8901235153-9788901235158"
ISBN10 = "8901235153"
ISBN13 = "9788901235158"
TITLE = "희망 버리기 기술"
RIDI, MILLIE, YES24, KYOBO, ALADIN = BOOK_STORES


async def run_ebook_info_test(store: dict, scraper: ScrapEbook):
    isbns = [ISBN10, ISBN13]

    good = await scraper.get_valid_good(store, isbns=isbns, title=TITLE)
    assert isinstance(good, Tag)

    link_element = await scraper.get_ebook_link(good, store)
    assert isinstance(link_element, Tag)

    detail = await scraper.get_ebook_detail(link_element, store)
    assert isinstance(detail, Ebook)

    assert detail.price >= 0


@pytest.mark.asyncio
async def test_get_ebook_info_ridi():
    await run_ebook_info_test(RIDI, ScrapEbook(operator=JsonFromTitleScraper()))


@pytest.mark.asyncio
async def test_get_ebook_info_millie():
    await run_ebook_info_test(MILLIE, ScrapEbook(operator=JsonFromTitleScraper()))


@pytest.mark.asyncio
async def test_get_ebook_info_yes24():
    await run_ebook_info_test(YES24, ScrapEbook(operator=HtmlFromISBNScraper()))


@pytest.mark.asyncio
async def test_get_ebook_info_kyobo():
    await run_ebook_info_test(KYOBO, ScrapEbook(operator=HtmlFromISBNScraper()))


@pytest.mark.asyncio
async def test_get_ebook_info_aladin():
    await run_ebook_info_test(ALADIN, ScrapEbook(operator=HtmlFromISBNScraper()))


@pytest.mark.asyncio
async def test_get_invalid_good_by_title():
    error_case_title = "그렇게 붕괴가 시작되었다"
    scraper = ScrapEbook(operator=JsonFromTitleScraper())

    with pytest.raises(
        NotMatchingTitleException,
        match="약혼 파기를 노리고 기억 상실인 척했더니, 냉담하던 약혼자가 '기억을 잃기 전의 넌 나에게 완전히 푹 빠져 있었다'는 말도 안 되는 거짓말을 하기 시작했다",
    ):
        await scraper.get_valid_good(RIDI, title=error_case_title)
