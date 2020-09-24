# -*- coding:utf-8 -*-

import requests
import json
import urllib.parse
import traceback

from django.views.generic.base import TemplateView, View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db import DataError

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

        res = requests.get(api_url, headers=headers)
        print(res.status_code)
        res = res.json()
        books_meta = res.get('meta', {})
        books = res.get('documents', [])
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
            except ValueError as e:
                raise Http404(str(e))
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
            try:
                book.save()
            except DataError as e:
                book.delete()
                raise Http404(str(e))
            except Exception as e:
                raise Http404(str(e))

        if not book.ebooks.exists():
            infos = get_ebooks_info(book.isbn)
            for info in infos:
                ebook = Ebook(**info)
                ebook.book = book
                ebook.save()
                save_ebook_raw.apply_async((info['url'], ebook.id), countdown=1)

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
    res = requests.get(api_url, headers=headers).json().get('documents')
    if res is None:
        raise ValueError('Search API not working')
    elif not res:
        raise ValueError('Can not find isbn')
    return res[0]


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
BOOK_STORES = [
    {
        'name': 'yes24',
        'domain': 'http://www.yes24.com',
        'base': '/searchcorner/Search',
        'good_selector': '#schMid_wrap div.goodsList.goodsList_list table tr',
        'param_key': 'query',
        'keyword': 'eBook',
    },
    {
        'name': 'interpark',
        'domain': 'http://bsearch.interpark.com',
        'base': '/dsearch/book.jsp',
        'good_selector': '#bookresult > form > div.list_wrap',
        'param_key': 'query',
        'keyword': 'eBook',
    },
    {
        'name': 'kyobobook',
        'domain': 'https://search.kyobobook.co.kr',
        'base': '/web/search',
        'good_selector': 'td.info',
        'param_key': 'vPstrKeyWord',
        'keyword': 'eBook',
    },
    {
        'name': 'aladin',
        'domain': 'https://www.aladin.co.kr',
        'base': '/search/wsearchresult.aspx',
        'good_selector': '#Search3_Result table tr',
        'param_key': 'SearchWord',
        'keyword': '전자책 보기',
    },
]

from ebookFinder.apps.book.tasks import save_ebook_raw
def get_ebooks_info(isbn) -> list:
    if '-' in isbn:
        isbns = isbn.split('-')
    else:
        raise ValueError('Invalid isbn!')

    headers = {
        'User-agent': USER_AGENT,
    }

    result = []
    for STORE in BOOK_STORES:
        base = STORE['domain'] + STORE['base']

        for isbn in isbns:
            params = {STORE['param_key']: isbn}
            query = urllib.parse.urlencode(params)
            url = "?".join([base, query])
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            good = soup.select_one(
                STORE['good_selector']
            )
            if good:
                break
        links = good.select('a')

        res = None
        for a in links:
            if a.string is None:
                for s in a.stripped_strings:
                    if s == STORE['keyword']:
                        res = a

        if res is None:
            res = good.find('a', {'title': STORE['keyword']})

        if res:
            href = res.get('href', '') if res else ''
            store_url = STORE['domain']
            info = {}
            info['book_store'] = STORE['name']
            info['url'] = store_url + href if 'http' not in href else href
            result.append(info)
    return result
