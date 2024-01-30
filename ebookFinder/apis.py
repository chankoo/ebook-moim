from ninja import NinjaAPI
from ebookFinder.apps.book.apis import router as books_router

import orjson
from ninja import NinjaAPI
from ninja.renderers import BaseRenderer


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)

api = NinjaAPI(renderer=ORJSONRenderer(), urls_namespace='api')

api.add_router("books/", books_router)
