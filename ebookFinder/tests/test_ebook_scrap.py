import pytest

from bs4 import Tag
from ebookFinder.apps.book.services import (
    ScrapEbook,
    ScrapEbookByISBN,
    ScrapEbookByTitle,
)
from ebookFinder.apps.book.consts import BOOK_STORES
from ebookFinder.apps.book.schemas import Ebook

ISBN = "1162241632-9791162241639"
ISBN10 = "1162241632"
ISBN13 = "9791162241639"
TITLE = "파이썬으로 웹 크롤러 만들기"
RIDI, YES24, KYOBO, ALADIN = BOOK_STORES


async def run_ebook_info_test(store: dict, scrap_service: ScrapEbook):
    scraper = scrap_service()
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
    await run_ebook_info_test(RIDI, ScrapEbookByTitle)


@pytest.mark.asyncio
async def test_get_ebook_info_yes24():
    await run_ebook_info_test(YES24, ScrapEbookByISBN)


@pytest.mark.asyncio
async def test_get_ebook_info_kyobo():
    await run_ebook_info_test(KYOBO, ScrapEbookByISBN)


@pytest.mark.asyncio
async def test_get_ebook_info_aladin():
    await run_ebook_info_test(ALADIN, ScrapEbookByISBN)
