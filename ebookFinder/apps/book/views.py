from django.views.generic.base import TemplateView, View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db import DataError
from django.contrib import messages

from ebookFinder.apps.book.models import Book, Ebook
from ebookFinder.apps.book.tasks import save_ebook_raw
from ebookFinder.apps.book.apis import search_books, get_book_info, get_ebooks_info
from ebookFinder.apps.book.consts import LOGOS, STORE_NAME_REPR
from ebookFinder.apps.utils.eb_datetime import tz_now
from ebookFinder.apps.log.models import SearchHistory


class IndexView(TemplateView):
    template_name = 'book/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)


class BookListView(TemplateView):
    template_name = 'book/list.html'

    async def get(self, request, *args, **kwargs):
        try:
            context = {}
            q = request.GET.get('q', '')
            if request.session.session_key is None:
                request.session.save()
            session_id = request.session.session_key
            if q:
                await SearchHistory.objects.acreate(q=q, user_identifier=session_id)

            context['q'] = q
            result = await search_books(q)
            context.update(result)
        except Exception as e:
            raise e
            messages.error(request, '책검색 API가 일시적으로 동작하지 않습니다.\n'
                                    '잠시 후에 다시 시도해주세요.\n{msg} :('.format(msg=str(e)))
            return HttpResponseRedirect('/book/')
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

    async def get(self, request, *args, **kwargs):
        isbn_slug = kwargs.get('isbn_slug', '')
        book, created = await Book.objects.aget_or_create(isbn=isbn_slug)

        if created:
            # 상세 페이지 처음 조회시 Book 객체 생성해 저장
            try:
                info = await get_book_info(isbn_slug.split('-')[0])
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
                await book.asave()
            except DataError as e:
                book.delete()
                raise Http404(str(e))
            except Exception as e:
                raise Http404(str(e))

        if book.need_ebook_update:
            try:
                infos = await get_ebooks_info(book.isbn)
            except ValueError:
                infos = []
            finally:
                for info in infos:
                    ebook, created = await Ebook.objects.aget_or_create(book=book,
                                                                 book_store=info.get('book_store', ''))
                    ebook.url = info.get('url', '')
                    ebook.deeplink = info.get('deeplink', '')
                    ebook.price = info.get('price', 0)
                    await ebook.asave()
                    # Ebook 상품 상세페이지 데이터 비동기로 저장
                    save_ebook_raw.apply_async((info['url'], ebook.id), countdown=1)
                book.date_searched = tz_now().date()
                await book.asave()

        context = self.get_context_data(**kwargs)
        context['book'] = book
        ebooks = []
        lowest_price = None
        async for ebook in book.ebooks.all():
            ebook.logo = LOGOS.get(ebook.book_store, '')
            ebook.repr = STORE_NAME_REPR.get(ebook.book_store, '')
            if lowest_price is None or 0 < ebook.price < lowest_price:
                lowest_price = ebook.price
            ebooks.append(ebook)
        context['ebooks'] = ebooks
        context['lowest_price'] = lowest_price
        return self.render_to_response(context=context)
