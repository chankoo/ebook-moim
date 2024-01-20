from datetime import datetime
from pydantic import BaseModel, Field


class KakaoBook(BaseModel):
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
