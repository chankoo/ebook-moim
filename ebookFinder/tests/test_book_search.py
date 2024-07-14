import pytest
import faker
import datetime

from ebookFinder.apps.book.services import search_books, get_book_info
from ebookFinder.apps.book.schemas import KakaoBook
from ebookFinder.apps.book.utils import get_valid_isbn
from ebookFinder.apps.book.models import Book

fake = faker.Faker("ko-KR")


VALID_ISBN = "8968484694-9788968484698"


@pytest.mark.asyncio
async def test_search_books():
    q = "파이썬"
    res = await search_books(q)
    assert type(res) == dict
    assert type(res["books_meta"]) == dict
    assert type(res["books"]) == list
    assert len(res["books"]) > 0


@pytest.mark.asyncio
async def test_get_book_info_valid():
    isbn = get_valid_isbn(VALID_ISBN)
    info = await get_book_info(isbn)
    assert type(info) == dict
    KakaoBook(**info)


@pytest.mark.asyncio
async def test_arrage_book_data():
    isbn = get_valid_isbn(VALID_ISBN)
    info = await get_book_info(isbn)
    assert type(info) == dict
    kakao_book = KakaoBook(**info)
    book_data = await Book.arrage_book_data(kakao_book)
    assert " " not in book_data["isbn"]
    assert type(book_data) == dict
    assert isinstance(book_data["date_publish"], datetime.date)
    assert "datetime" not in book_data
    assert isinstance(book_data["sell_status"], str)
    assert "status" not in book_data
