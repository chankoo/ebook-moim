# -*- coding:utf-8 -*-
#
# from django import template
#
# register = template.Library()
#
#
# DEFAULT = u'<meta property="title" content="위시켓! IT 아웃소싱을 빠르고 안전하게"/>' \
#           u'<meta property="og:title" content="위시켓! IT 아웃소싱을 빠르고 안전하게"/>' \
#           u'<meta name="description" content="위시켓은 기업의 프로젝트와 IT프리랜서를 이어주는 온라인 아웃소싱 플랫폼입니다. 위시켓만의 지원 시스템을 통해 빠른 모집이 가능해집니다."/>' \
#           u'<meta property="og:description" content="위시켓은 기업의 프로젝트와 IT프리랜서를 이어주는 온라인 아웃소싱 플랫폼입니다. 위시켓만의 지원 시스템을 통해 빠른 모집이 가능해집니다."/>' \
#           u'<meta property="og:image" content="https://www.wishket.com/static/img/ogimage_new.png"/>' \
#           u'<meta property="keyword" content="프리랜서,디자인외주,외주,디자인프리랜서,어플제작,앱개발업체,프로그램개발,프리랜서디자이너,개발자프리랜서,어플제작비용,앱개발,어플개발,어플개발비용,프리랜서사이트,개발자,앱개발자,웹개발자,홈페이지제작,어플리케이션">'
#
#
# @register.simple_tag
# def export_meta_tags(request):
#     loc = request.path.split('?')[0]
#     try:
#         tag = MetaTag.objects.get(location='https://www.wishket.com' + loc, is_delete=False)
#     except:
#         return DEFAULT
#     row = u'<meta property="title" content="%s"/>' \
#           u'<meta property="og:title" content="%s"/>' \
#           u'<meta name="description" content="%s"/>' \
#           u'<meta property="og:description" content="%s"/>' \
#           u'<meta property="og:image" content="https://www.wishket.com/static/img/ogimage_new.png"/>' \
#           u'<meta property="keyword" content="%s">'
#     row = row % (
#         tag.title,
#         tag.title,
#         tag.description,
#         tag.description,
#         tag.keyword
#     )
#     return row


from django import template

register = template.Library()


@register.filter
def split(value, separator=" "):
    return value.split(separator)
