from pydantic import ValidationError
from asgiref.sync import sync_to_async
import logging

from django.views.generic.base import TemplateView
from django.http import Http404, HttpResponseBadRequest, HttpResponseServerError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from ebookFinder.apps.book.models import Book
from ebookFinder.apps.book.services import search_books, get_book_info, get_ebooks_info
from ebookFinder.apps.book.consts import LOGOS, STORE_NAME_REPR
from ebookFinder.apps.log.models import SearchHistory
from ebookFinder.apps.book.schemas import KakaoBook
from ebookFinder.apps.book.utils import get_valid_isbn
from ebookFinder.apps.utils.eb_datetime import tz_now

class IndexView(TemplateView):
    template_name = 'book/index.html'

    async def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)


class BookListView(TemplateView):
    template_name = 'book/list.html'

    async def get(self, request, *args, **kwargs):
        context = {}
        q = request.GET.get('q', '')
        try:
            if request.session.session_key is None:
                await sync_to_async(request.session.save)()
            session_id = request.session.session_key
            if q:
                await SearchHistory.objects.acreate(q=q, user_identifier=session_id)
        except Exception as e:
            logger = logging.getLogger('django')
            logger.error(f"{tz_now().isoformat()} msg:{e} q:{q}")

        context['q'] = q
        try:
            result = await search_books(q)
            context.update(result)
        except Exception as e:
            messages.error(request, '책검색 API가 일시적으로 동작하지 않습니다.\n'
                                    '잠시 후에 다시 시도해주세요.\n{msg} :('.format(msg=str(e)))
            return HttpResponseServerError(e)
        return self.render_to_response(context=context)


class BookListAPIView(TemplateView):
    """
    Ajax search의 결과를 보여주기 위한 뷰
    """
    template_name = 'book/list.html'

    async def get(self, request, *args, **kwargs):
        context = {}
        return self.render_to_response(context=context)


class BookDetailView(TemplateView):
    template_name = 'book/detail.html'

    async def get(self, request, *args, **kwargs):
        isbn_slug = kwargs.get('isbn_slug', '')
        try:
            isbn = get_valid_isbn(isbn_slug)
        except ValueError:
            raise Http404('isbn_slug is not valid')

        # 상세 페이지 처음 조회시 Book 객체 생성해 저장
        book, created = await Book.objects.aget_or_create(isbn=isbn_slug)

        if created:
            try:
                info = await get_book_info(isbn)
            except ObjectDoesNotExist as e:
                raise Http404(str(e))
            
            try:
                kakao_book = KakaoBook(**info)
            except (TypeError, ValidationError) as e:
                raise HttpResponseBadRequest(e)
            
            try:
                await book.update_from_api(book=kakao_book)
            except Exception as e:
                raise HttpResponseServerError(e)

        if book.need_ebook_update():
            data = []
            data = await get_ebooks_info(isbn=book.isbn, title=book.title)
            await book.update_scrap_data(data=data)

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
