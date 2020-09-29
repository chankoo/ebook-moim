# -*- coding:utf-8 -*-

from django.views.generic.base import TemplateView, View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db import DataError

from ebookFinder.apps.book.models import Book, Ebook
from ebookFinder.apps.book.tasks import save_ebook_raw
from ebookFinder.apps.book.apis import search_books, get_book_info, get_ebooks_info
from ebookFinder.apps.book.consts import LOGOS, STORE_NAME_REPR


class IndexView(TemplateView):
    template_name = 'book/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)


class BookListView(TemplateView):
    template_name = 'book/list.html'

    def get(self, request, *args, **kwargs):
        try:
            context = {}
            context['query'] = request.GET.get('query', '')
            result = search_books(request.GET)
            context.update(result)
        except Exception as e:
            print(e)
        return self.render_to_response(context=context)


class BookListAPIView(TemplateView):
    """
    Ajax search의 결과를 보여주기 위한 뷰
    """
    template_name = 'book/list.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return self.render_to_response(context=context)


class BookDetailView(TemplateView):
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
                    setattr(book, k, ', '.join(v))
                elif k == 'datetime':
                    setattr(book, 'date_publish', v.split('T')[0])
                elif k == 'translators':
                    setattr(book, k, ', '.join(v))
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
            try:
                infos = get_ebooks_info(book.isbn)
            except ValueError as e:
                infos = []
                print(e)
            for info in infos:
                ebook = Ebook(**info)
                ebook.book = book
                ebook.save()
                # Ebook 상품 상세페이지 데이터 비동기로 저장
                save_ebook_raw.apply_async((info['url'], ebook.id), countdown=1)

        context = self.get_context_data(**kwargs)
        context['book'] = book
        ebooks = []
        for ebook in book.ebooks.all():
            ebook.logo = LOGOS[ebook.book_store]
            ebook.repr = STORE_NAME_REPR[ebook.book_store]
            ebooks.append(ebook)
        context['ebooks'] = ebooks
        return self.render_to_response(context=context)
