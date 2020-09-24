import requests
from ebookFinder.celery import app
from ebookFinder.apps.book.views import USER_AGENT
from ebookFinder.apps.book.models import Ebook


@app.task(name='save_ebook_raw')
def save_ebook_raw(url, ebook_id):
    headers = {
        'User-agent': USER_AGENT,
    }
    res = requests.get(url, headers=headers)
    ebook = Ebook.objects.get(id=ebook_id)
    ebook.raw = res.text
    ebook.save()
