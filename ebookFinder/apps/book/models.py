import datetime
import asyncio

from django.db import models
from django.conf import settings
from django.db import DataError

from ebookFinder.apps.utils.eb_datetime import tz_now
from ebookFinder.apps.book import schemas
from ebookFinder.apps.book.consts import LOGOS, STORE_NAME_REPR


class Book(models.Model):
    title = models.CharField(max_length=50, default="")

    isbn = models.CharField(max_length=30, default="")

    publisher = models.CharField(max_length=30, default="")

    authors = models.CharField(max_length=100, default="")

    date_publish = models.DateField(null=True, blank=True)

    translators = models.CharField(max_length=100, default="")

    price = models.IntegerField(null=True, blank=True)

    thumbnail = models.CharField(max_length=500, default="")

    url = models.CharField(max_length=500, default="")

    contents = models.TextField(default="")

    sell_status = models.CharField(max_length=20, default="")

    date_searched = models.DateField(null=True, blank=True)

    dt_created = models.DateTimeField(auto_now_add=True, editable=False)

    dt_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def need_ebook_update(self):
        if settings.DEBUG:
            return True
        if self.date_searched is None:
            return True
        return self.date_searched + datetime.timedelta(days=30) < tz_now().date()

    def get_absolute_url(self):
        domain = settings.SERVICE_DOMAIN
        return "{domain}/book/{isbn}".format(domain=domain, isbn=self.isbn)

    async def update_from_api(self, book: schemas.KakaoBook):
        book_dict = await self.arrage_book_data(book)
        for field_name, val in book_dict.items():
            setattr(self, field_name, val)

        try:
            await self.asave()
        except DataError as e:
            await self.adelete()
            raise e

    @staticmethod
    async def arrage_book_data(book: schemas.KakaoBook) -> dict:
        book_dict = book.model_dump()
        book_dict["isbn"] = book_dict["isbn"].replace(" ", "-")
        book_dict["authors"] = ", ".join(book_dict["authors"])
        book_dict["translators"] = ", ".join(book_dict["translators"])
        book_dict["date_publish"] = book_dict.pop("datetime").date()
        book_dict["sell_status"] = book_dict.pop("status")
        return book_dict

    async def update_scrap_data(self, data: list[schemas.Ebook]):
        await self.update_ebooks(data=data)
        self.date_searched = tz_now().date()
        await self.asave()

    async def update_ebooks(self, data: list[schemas.Ebook]):
        tasks = [asyncio.create_task(self.update_ebook(info)) for info in data]
        await asyncio.gather(*tasks)

    async def update_ebook(self, info: schemas.Ebook):
        """
        Ebook 객체를 생성하거나 업데이트
        """
        ebook, _ = await Ebook.objects.aget_or_create(
            book=self,
            book_store=info.book_store,
        )
        ebook.url = info.url
        ebook.deeplink = info.deeplink
        ebook.price = info.price
        await ebook.asave()
        # Ebook 상품 상세페이지 데이터 비동기로 저장
        # save_ebook_raw.apply_async((info['url'], ebook.id), countdown=1)

    async def get_lowest_ebook_price(self) -> int:
        """
        가장 낮은 Ebook 가격
        """
        lowest_price = (
            await Ebook.objects.filter(book=self, price__gt=0)
            .order_by("price")
            .values_list("price", flat=True)
            .afirst()
        )
        return lowest_price or 0


class Ebook(models.Model):
    book = models.ForeignKey(
        "Book", on_delete=models.CASCADE, related_name="ebooks", null=True, blank=True
    )

    book_store = models.CharField(max_length=20, default="")

    url = models.CharField(max_length=500, default="")

    deeplink = models.CharField(max_length=700, default="")

    price = models.IntegerField(null=True, blank=True)

    raw = models.TextField(default="")

    dt_created = models.DateTimeField(auto_now_add=True, editable=False)

    dt_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}/{}".format(self.book.title, self.book_store)

    def get_title(self) -> str:
        return self.book.title

    def get_logo(self) -> str:
        return LOGOS.get(self.book_store, "")

    def get_repr(self) -> str:
        return STORE_NAME_REPR.get(self.book_store, "")

    def to_dict(self) -> dict:
        return {
            "title": self.get_title(),
            "book_store": self.book_store,
            "url": self.url,
            "deeplink": self.deeplink,
            "price": self.price,
            "logo": self.get_logo(),
            "repr": self.get_repr(),
        }
