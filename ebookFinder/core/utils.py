import httpx

from ebookFinder.apps.book.consts import USER_AGENT


async def get_response(url: str, headers: dict = None, **kwargs) -> httpx.Response:
    headers = headers or {
        "User-agent": USER_AGENT,
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers, **kwargs)
        if res.status_code != 200:
            res.raise_for_status()
    return res
