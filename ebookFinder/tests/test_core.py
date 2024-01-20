import pytest
import faker

from ebookFinder.apps.book.apis import search_books, get_book_info, get_ebooks_info
from ebookFinder.apps.book.consts import KAKAO_API_KEY, SEARCH_API_ENDPOINT, USER_AGENT, \
    BOOK_STORES, AFFILIATE_API_ENDPOINT, AFFILIATE_ID

fake = faker.Faker('ko-KR')


@pytest.mark.asyncio
async def test_search_books():
    q = '파이썬'
    print(q)
    res = await search_books(q)
    assert type(res) == dict
    assert type(res['books_meta']) == dict
    assert type(res['books']) == list
    assert len(res['books']) > 0
