# -*- coding:utf-8 -*-

from django.db import models
from django.urls import reverse


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
        max_length=300,
        default=''
    )

    url = models.CharField(
        max_length=300,
        default=''
    )

    contents = models.TextField(
        default=''
    )

    sell_status = models.CharField(
        max_length=20,
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
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id])


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
        max_length=300,
        default=''
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
