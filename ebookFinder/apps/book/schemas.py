from datetime import datetime
from pydantic import HttpUrl, field_validator, TypeAdapter
from ninja import Schema


class KakaoBook(Schema):
    """
    카카오 책 검색 API의 정보를 담는 모델
    """

    title: str
    isbn: str
    publisher: str
    authors: list[str]
    datetime: datetime
    translators: list[str]
    price: int
    thumbnail: str
    url: str
    contents: str
    status: str


class Ebook(Schema):
    """
    Ebook 상품의 정보를 담는 모델
    """

    title: str = ""  # Required in Response
    book_store: str
    url: str
    deeplink: str = ""
    price: int
    logo: str = ""
    repr: str = ""

    @field_validator("url")
    def validate_url(cls, value):
        if value != "" and not TypeAdapter(HttpUrl).validate_python(value):
            raise ValueError("Invalid URL")
        return value

    @field_validator("deeplink")
    def validate_deeplink(cls, value):
        if value != "" and not TypeAdapter(HttpUrl).validate_python(value):
            raise ValueError("Invalid URL")
        return value
