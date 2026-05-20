"""
메인(홈) 페이지 — 카테고리 카드·캐러셀(템플릿 인라인 JS).
"""

from django.shortcuts import render

# 검색 페이지 product_type 쿼리와 동일 코드
CATEGORIES = [
    {"label": "TV", "product_type": "TVT"},
    {"label": "세탁기", "product_type": "WMT"},
    {"label": "냉장고", "product_type": "REF"},
    {"label": "에어컨", "product_type": "ACT"},
    {"label": "청소기", "product_type": "VAC"},
]


def mainpage(request):
    """홈 SSR — 로그인 닉네임·카테고리 목록만 컨텍스트로 전달."""
    return render(
        request,
        "mainpage.html",
        {
            "test_var": request.user.nickname if request.user.is_authenticated else "비로그인 상태",
            "categories": CATEGORIES,
        },
    )