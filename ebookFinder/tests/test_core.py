import pytest
import faker

from django.core.exceptions import ObjectDoesNotExist

from ebookFinder.apps.book.apis import search_books, get_book_info, get_ebooks_info
from ebookFinder.apps.book.consts import KAKAO_API_KEY, SEARCH_API_ENDPOINT, USER_AGENT, \
    BOOK_STORES, AFFILIATE_API_ENDPOINT, AFFILIATE_ID
from ebookFinder.apps.book.schemas import KakaoBook
from ebookFinder.apps.book.utils import get_valid_isbn

fake = faker.Faker('ko-KR')


VALID_ISBN = '8968484694-9788968484698'


@pytest.mark.asyncio
async def test_search_books():
    q = '파이썬'
    res = await search_books(q)
    assert type(res) == dict
    assert type(res['books_meta']) == dict
    assert type(res['books']) == list
    assert len(res['books']) > 0


@pytest.mark.asyncio
async def test_get_book_info_valid():
    isbn = get_valid_isbn(VALID_ISBN)
    info = await get_book_info(isbn)
    assert type(info) == dict
    KakaoBook(**info)

