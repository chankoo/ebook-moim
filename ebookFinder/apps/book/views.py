# -*- coding:utf-8 -*-

import requests
import json
import urllib.parse

from django.shortcuts import render_to_response
from django.views.generic.base import TemplateView, View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from ebookFinder.apps.book.models import Book, Ebook
from bs4 import BeautifulSoup


class MainView(TemplateView):
    template_name = 'book/main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)

    def post(self, request, *args, **kwargs):
        api_key = '68fa5e7aa69b0d975f53e6eee037a76a'
        url = 'https://dapi.kakao.com/v3/search/book?target=title'
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'

        headers = {
            'User-agent': user_agent,
            'referer': None,
            'Authorization': 'KakaoAK {api_key}'.format(api_key=api_key)
        }

        q = request.POST.get('query', '')
        params = {"page": 1, "size": 50, "query": q}
        query = urllib.parse.urlencode(params)
        api_url = url + "?" + query

        res = requests.get(api_url, headers=headers).json()
        books_meta = res['meta']
        books = res['documents']
        return self.render_to_response(context={
            'books_meta': books_meta,
            'books': books,
        })


class BookDetail(TemplateView):
    template_name = 'book/detail.html'

    def get(self, request, *args, **kwargs):
        isbn_slug = kwargs.get('isbn_slug', '')
        book, created = Book.objects.get_or_create(isbn=isbn_slug)

        if created:
            try:
                info = get_book_info(isbn_slug.split('-')[0])
            except ValueError:
                raise Http404()
            for k, v in info.items():
                if k == 'isbn':
                    setattr(book, k, v.replace(' ', '-'))
                elif k == 'authors':
                    setattr(book, k, '|'.join(v))
                elif k == 'datetime':
                    setattr(book, 'date_publish', v.split('T')[0])
                elif k == 'translators':
                    setattr(book, k, '|'.join(v))
                elif k == 'status':
                    setattr(book, 'sell_status', v)
                else:
                    setattr(book, k, v)
            book.save()

        if not book.ebooks.exists():
            infos = get_ebooks_info(book.isbn)
            for info in infos:
                ebook = Ebook(**info)
                ebook.book = book
                ebook.save()

        context = self.get_context_data(**kwargs)
        context['book'] = book
        context['ebooks'] = book.ebooks.all()
        return self.render_to_response(context=context)

    def post(self, request, *args, **kwargs):
        pass

def get_book_info(isbn) -> dict:
    api_key = '68fa5e7aa69b0d975f53e6eee037a76a'
    url = 'https://dapi.kakao.com/v3/search/book?target=title'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'

    headers = {
        'User-agent': user_agent,
        'referer': None,
        'Authorization': 'KakaoAK {api_key}'.format(api_key=api_key)
    }

    params = {"page": 1, "size": 1, "query": isbn}
    query = urllib.parse.urlencode(params)
    api_url = url + "?" + query
    res = requests.get(api_url, headers=headers).json()['documents']
    if not res:
        raise ValueError('Can not find isbn')
    return res[0]

import time
import re
def get_ebooks_info(isbn) -> list:
    result = []

    if '-' in isbn:
        isbns = isbn.split('-')
    else:
        raise ValueError('Invalid isbn!')

    base = 'http://www.yes24.com/searchcorner/Search'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'

    headers = {
        'User-agent': user_agent,
    }

    for isbn in isbns:
        params = {"query": isbn}
        query = urllib.parse.urlencode(params)
        url = "?".join([base, query])
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        good = soup.select_one(
            '#schMid_wrap div.goodsList.goodsList_list table tr'
            # '#schMid_wrap > div:nth-child(4) > div.goodsList.goodsList_list > table > tbody > tr:nth-child(1) > td.goods_infogrp > p.goods_linkage.goods_icon > a'
        )
        if good:
            break
    links = good.select(
        'a'
    )

    res = None
    for a in links:
        if a.string is None:
            for s in a.stripped_strings:
                if s == 'eBook':
                    res = a
    if res:
        href = res.get('href', '') if res else ''
        store_url = 'http://www.yes24.com'
        info = {}
        info['book_store'] = 'yes24'
        info['url'] = store_url + href
        res = requests.get(info['url'], headers=headers)
        info['raw'] = res.text
        result.append(info)
    return result
