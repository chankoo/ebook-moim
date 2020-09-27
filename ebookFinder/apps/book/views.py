# -*- coding:utf-8 -*-

from django.views.generic.base import TemplateView, View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db import DataError

from ebookFinder.apps.book.models import Book, Ebook
from ebookFinder.apps.book.tasks import save_ebook_raw
from ebookFinder.apps.book.apis import search_books, get_book_info, get_ebooks_info


class MainView(TemplateView):
    template_name = 'book/main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)

    def post(self, request, *args, **kwargs):
        try:
            result = search_books(request.POST)
        except Exception as e:
            result = {}
            print(e)
        return self.render_to_response(context=result)


class BookDetail(TemplateView):
    template_name = 'book/detail.html'

    def get(self, request, *args, **kwargs):
        isbn_slug = kwargs.get('isbn_slug', '')
        book, created = Book.objects.get_or_create(isbn=isbn_slug)

        if created:
            # 상세 페이지 처음 조회시 Book 객체 생성해 저장
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
            # Ebook 정보 없을 경우 웹상에서 정보 조회
            infos = get_ebooks_info(book.isbn)
            for info in infos:
                ebook = Ebook(**info)
                ebook.book = book
                ebook.save()
                # Ebook 상품 상세페이지 데이터 비동기로 저장
                save_ebook_raw.apply_async((info['url'], ebook.id), countdown=1)

        context = self.get_context_data(**kwargs)
        context['book'] = book
        context['ebooks'] = book.ebooks.all()
        return self.render_to_response(context=context)

    def post(self, request, *args, **kwargs):
        try:
            result = search_books(request.POST)
        except Exception as e:
            result = {}
            print(e)
        return self.render_to_response(context=result)
