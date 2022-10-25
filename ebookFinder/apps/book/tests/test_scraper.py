import asyncio

from django.test import TestCase, Client

from ebookFinder.apps.book.apis import search_books, get_book_info, get_ebooks_info
from ebookFinder.apps.book.services import get_ebook_page_async, get_ebook_info_async
from ebookFinder.apps.book.consts import BOOK_STORES, USER_AGENT
from icecream import ic

SAMPLE_ISBN = '8966262473-9788966262472'


class EbookRequestTestCase(TestCase):
    def setUp(self) -> None:
        self.isbn = SAMPLE_ISBN
        self.isbns = self.isbn.split('-')
        self.headers = {'User-agent': USER_AGENT}
        self.store=BOOK_STORES[0]

    def tearDown(self):
        self.isbn = ''
        self.isbns = []

    def test_get_ebooks_info(self):
        infos = get_ebooks_info(self.isbn)
        ic(infos)
        self.assertTrue(isinstance(infos, list))

    def test_get_ebook_info_async(self):
        asyncio.run(get_ebook_info_async(self.isbns, headers=self.headers, store=self.store))
