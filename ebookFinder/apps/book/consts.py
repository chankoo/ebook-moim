USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
KAKAO_API_KEY = "68fa5e7aa69b0d975f53e6eee037a76a"
SEARCH_API_ENDPOINT = "https://dapi.kakao.com/v3/search/book?target=title"
AFFILIATE_API_ENDPOINT = "https://api.linkprice.com/ci/service/custom_link_xml"
AFFILIATE_ID = "A100670817"
BOOK_STORES = [
    {
        "name": "ridi",
        "name_repr": "RIDI",
        "domain": "https://ridibooks.com",
        "base": "/api/search-api/search",
        "good_selector": "books",
        "param_key": "keyword",
        "keyword": "",
        "logo": "/static/img/logo_ridi.png",
        "link_format": "https://ridibooks.com/books/%s",
        "link_id_name": "b_id",
    },
    {
        "name": "millie",
        "name_repr": "MILLIE",
        "domain": "https://live-api.millie.co.kr",
        "base": "/v3/search/content",
        "good_selector": "RESP_DATA",
        "good_selector2": "list",
        "param_key": "keyword",
        "keyword": "",
        "logo": "/static/img/logo_millie.png",
        "link_format": "https://www.millie.co.kr/v3/bookDetail/%s",
        "link_id_name": "book_id",
        # param setting 필요 ?debug=1&filter[condition]=published&limitCount=10&category=&searchType=total&contentCode=245&orderBy=accuracy&keyword=%EB%B6%95%EA%B4%B4%EA%B0%80&startPage=1
    },
    {
        "name": "yes24",
        "name_repr": "YES24",
        "domain": "https://www.yes24.com",
        "base": "/Product/Search",
        "good_selector": "#yesSchList div.itemUnit",
        "param_key": "query",
        "keyword": "eBook",
        "logo": "/static/img/logo_yes24.png",
    },
    # {
    #     'name': 'interpark',
    #     'name_repr': '인터파크 도서',
    #     'domain': 'http://bsearch.interpark.com',
    #     'base': '/dsearch/book.jsp',
    #     'good_selector': '#bookresult > form > div.list_wrap',
    #     'param_key': 'query',
    #     'keyword': 'eBook',
    # },
    {
        "name": "kyobobook",
        "name_repr": "교보문고",
        "domain": "https://search.kyobobook.co.kr",
        "base": "/search",
        "good_selector": "li.prod_item",
        "param_key": "keyword",
        "keyword": "eBook",
        "link_selector": 'a.btn_xxs.btn_pill.btn_line_gray:-soup-contains("eBook")',
    },
    {
        "name": "aladin",
        "name_repr": "알라딘",
        "domain": "https://www.aladin.co.kr",
        "base": "/search/wsearchresult.aspx",
        "good_selector": "#Search3_Result table tr",
        "param_key": "SearchWord",
        "keyword": "전자책 보기",
    },
]

LOGOS = {
    "ridi": "/static/img/logo_ridi.png",
    "millie": "/static/img/logo_millie.png",
    "yes24": "/static/img/logo_yes24.png",
    "interpark": "/static/img/logo_interpark.jpg",
    "kyobobook": "/static/img/logo_kyobobook.png",
    "aladin": "/static/img/logo_aladin.png",
}

STORE_NAME_REPR = {
    "ridi": "리디",
    "millie": "밀리의 서재",
    "yes24": "YES24",
    "interpark": "인터파크 도서",
    "kyobobook": "교보문고",
    "aladin": "알라딘",
}
