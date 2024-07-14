def get_valid_isbn(isbn_slug: str) -> str:
    if not isinstance(isbn_slug, str):
        raise ValueError("isbn_slug must be str")

    if "-" in isbn_slug:
        isbn10, isbn13 = isbn_slug.split("-")
        if is_valid_isbn10(isbn10):
            return isbn10
        if is_valid_isbn13(isbn13):
            return isbn13

    if len(isbn_slug) == 10 and is_valid_isbn10(isbn_slug):
        return isbn_slug
    elif len(isbn_slug) == 13 and is_valid_isbn13(isbn_slug):
        return isbn_slug
    raise ValueError("Invalid isbn_slug")


def is_valid_isbn10(isbn):
    if not isinstance(isbn, str):
        return False

    # ISBN-10은 숫자와 마지막에 'x'로 이루어짐
    if not isbn[:-1].isdigit() or (isbn[-1] != "x" and not isbn[-1].isdigit()):
        return False

    # ISBN-10의 길이는 10
    if len(isbn) != 10:
        return False

    # ISBN-10 체크 디지트 계산
    total = sum((i + 1) * int(digit) for i, digit in enumerate(isbn[:-1]))
    check_digit = total % 11

    # 마지막 자리 검사
    if isbn[-1] == "x":
        return check_digit == 10
    else:
        return check_digit == int(isbn[-1])


def is_valid_isbn13(isbn):
    if not isinstance(isbn, str):
        return False

    # ISBN-13은 13자리 숫자로 이루어짐
    if not isbn.isdigit() or len(isbn) != 13:
        return False

    # ISBN-13 체크 디지트 계산
    total = sum(
        int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(isbn[:-1])
    )
    check_digit = (10 - (total % 10)) % 10

    # 마지막 자리 검사
    return check_digit == int(isbn[-1])
