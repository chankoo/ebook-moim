# -*- coding:utf-8 -*-

import datetime

from django.db import models
from django.conf import settings
from django.db import DataError

from ebookFinder.apps.utils.eb_datetime import tz_now
from ebookFinder.settings.base import SERVICE_DOMAIN
from ebookFinder.apps.book.schemas import KakaoBook


class Book(models.Model):
    title = models.CharField(
        max_length=50,
        default=''
    )

    isbn = models.CharField(
        max_length=30,
        default=''
    )

    publisher = models.CharField(
        max_length=30,
        default=''
    )

    authors = models.CharField(
        max_length=100,
        default=''
    )

    date_publish = models.DateField(
        null=True,
        blank=True
    )

    translators = models.CharField(
        max_length=100,
        default=''
    )

    price = models.IntegerField(
        null=True,
        blank=True
    )

    thumbnail = models.CharField(
        max_length=500,
        default=''
    )

    url = models.CharField(
        max_length=500,
        default=''
    )

    contents = models.TextField(
        default=''
    )

    sell_status = models.CharField(
        max_length=20,
        default=''
    )

    date_searched = models.DateField(
        null=True,
        blank=True
    )

    dt_created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    dt_modified = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

    @property
    def need_ebook_update(self):
        if settings.DEBUG:
            return True
        if self.date_searched is None:
            return True
        return self.date_searched + datetime.timedelta(days=30) < tz_now().date()

    @property
    def absolute_url(self):
        domain = '' if settings.DEBUG else settings.SERVICE_DOMAIN
        return '{domain}/book/{isbn}'.format(domain=domain, isbn=self.isbn)
    
    async def update_from_api(self, book: KakaoBook):
        fields_to_update = [field.name for field in self._meta.fields if field.name in book.model_dump()]
        for field_name in fields_to_update:
            setattr(self, field_name, getattr(book, field_name))
        
        self.isbn = book.isbn.replace(' ', '-')
        self.authors = ', '.join(book.authors)
        self.date_publish = book.datetime.split('T')[0]
        self.translators = ', '.join(book.translators)
        self.sell_status = book.status
    
        try:
            await self.asave()
        except DataError as e:
            await self.adelete()
            raise e


class Ebook(models.Model):
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='ebooks',
        null=True,
        blank=True
    )

    book_store = models.CharField(
        max_length=20,
        default=''
    )

    url = models.CharField(
        max_length=500,
        default=''
    )

    deeplink = models.CharField(
        max_length=700,
        default=''
    )

    price = models.IntegerField(
        null=True,
        blank=True
    )

    raw = models.TextField(
        default=''
    )

    dt_created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    dt_modified = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return '{}/{}'.format(self.book.title, self.book_store)
