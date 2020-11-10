USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
KAKAO_API_KEY = '68fa5e7aa69b0d975f53e6eee037a76a'
SEARCH_API_ENDPOINT = 'https://dapi.kakao.com/v3/search/book?target=title'
AFFILIATE_API_ENDPOINT = 'https://api.linkprice.com/ci/service/custom_link_xml'
AFFILIATE_ID = 'A100670817'
BOOK_STORES = [
    {
        'name': 'yes24',
        'name_repr': 'YES24',
        'domain': 'http://www.yes24.com',
        'base': '/searchcorner/Search',
        'good_selector': '#schMid_wrap div.goodsList.goodsList_list table tr',
        'param_key': 'query',
        'keyword': 'eBook',
        'logo': '/static/img/logo_yes24.png',
    },
    {
        'name': 'interpark',
        'name_repr': '인터파크 도서',
        'domain': 'http://bsearch.interpark.com',
        'base': '/dsearch/book.jsp',
        'good_selector': '#bookresult > form > div.list_wrap',
        'param_key': 'query',
        'keyword': 'eBook',
    },
    {
        'name': 'kyobobook',
        'name_repr': '교보문고',
        'domain': 'https://search.kyobobook.co.kr',
        'base': '/web/search',
        'good_selector': 'td.info',
        'param_key': 'vPstrKeyWord',
        'keyword': 'eBook',
    },
    {
        'name': 'aladin',
        'name_repr': '알라딘',
        'domain': 'https://www.aladin.co.kr',
        'base': '/search/wsearchresult.aspx',
        'good_selector': '#Search3_Result table tr',
        'param_key': 'SearchWord',
        'keyword': '전자책 보기',
    },
]

LOGOS = {
    'yes24': '/static/img/logo_yes24.png',
    'interpark': '/static/img/logo_interpark.jpg',
    'kyobobook': '/static/img/logo_kyobobook.png',
    'aladin': '/static/img/logo_aladin.png',
}

STORE_NAME_REPR = {
    'yes24': 'YES24',
    'interpark': '인터파크 도서',
    'kyobobook': '교보문고',
    'aladin': '알라딘',
}
