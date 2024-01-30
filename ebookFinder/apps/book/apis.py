from ninja import Router
from django.core.exceptions import ObjectDoesNotExist

from ebookFinder.apps.book.services import get_ebooks_info
from ebookFinder.apps.book import models, schemas

router = Router()

@router.get("/{book_id}/ebooks", response={200: list[schemas.Ebook]}, url_name="get_ebooks")
async def get_ebooks(request, book_id: int):
    try:
        book = await models.Book.objects.aget(id=book_id)
    except ObjectDoesNotExist:
        return []
    
    if book.need_ebook_update():
        data = []
        data = await get_ebooks_info(isbn=book.isbn, title=book.title)
        await book.update_scrap_data(data=data)
    
    res = []
    async for ebook in book.ebooks.all():
        res.append(schemas.Ebook(**ebook.to_dict()))
    return res
