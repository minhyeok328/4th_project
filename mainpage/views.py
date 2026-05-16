from django.shortcuts import render

CATEGORIES = [
    {"label": "TV", "product_type": "TVT"},
    {"label": "세탁기", "product_type": "WMT"},
    {"label": "냉장고", "product_type": "REF"},
    {"label": "에어컨", "product_type": "ACT"},
    {"label": "청소기", "product_type": "VAC"},
]


def mainpage(request):
    return render(
        request,
        "mainpage.html",
        {
            "test_var": request.user.nickname if request.user.is_authenticated else "비로그인 상태",
            "categories": CATEGORIES,
        },
    )