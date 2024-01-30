from ninja import Router
from django.core.exceptions import ObjectDoesNotExist

from ebookFinder.apps.book import models, schemas

router = Router()

@router.get("/{book_id}/ebooks", response={200: list[schemas.Ebook]}, url_name="get_ebooks")
async def get_ebooks(request, book_id: int):
    try:
        book = await models.Book.objects.aget(id=book_id)
    except ObjectDoesNotExist:
        return []
    
    res = []
    async for ebook in book.ebooks.all():
        res.append(schemas.Ebook.from_orm(ebook))
    return res
