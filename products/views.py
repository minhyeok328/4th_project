"""
상품 검색·상세 SSR 뷰.

- searchpage: GET 쿼리 → common.utils.search_product → Paginator
- productpage: product_code 경로 → get_product, 찜 여부
"""

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from common.utils import get_product, search_product

LIST_CONDITION_SUFFIXES = ("_in", "_icontains", "__in", "__icontains")


def _is_list_condition(key):
    """필터 키가 다중값(콤마·getlist) 조건인지 접미사로 판별."""
    return key.endswith(LIST_CONDITION_SUFFIXES)


def _get_condition_values(key, values):
    """request.GET.getlist 값을 단일값 또는 리스트 조건으로 정규화."""
    clean_values = [value for value in values if value is not None and value != ""]

    if not _is_list_condition(key):
        return clean_values[-1] if clean_values else None

    if key.endswith(("_in", "__in")):
        return [
            item.strip()
            for value in clean_values
            for item in value.split(",")
            if item.strip()
        ]

    return clean_values


def productpage(request, product_code):
    """상품 상세 템플릿 — 로그인 시 찜 여부 is_favorite."""
    product_type, product_data = get_product(product_code)
    is_favorite = False
    if request.user.is_authenticated and product_data is not None:
        is_favorite = request.user.favorites.filter(
            product_code=product_data.product_code
        ).exists()

    return render(
        request,
        "productpage.html",
        {
            "product_type": product_type,
            "product_data": product_data,
            "is_favorite": is_favorite
        }
    )

def searchpage(request):
    """
    검색 결과 페이지 — product_type·page 기본값 리다이렉트 후 필터 GET → 페이지네이션.

    프론트 filter.js는 동일 쿼리 키로 GET submit, pagination.js가 page 링크 생성.
    """
    default_type = "REF"

    # 북마크·첫 진입 시 product_type=REF, page=1 보장
    if "product_type" not in request.GET or "page" not in request.GET:
        query = request.GET.copy()
        query.setdefault("product_type", default_type)
        query.setdefault("page", "1")
        return redirect(f"{request.path}?{query.urlencode()}")

    product_type = request.GET.get("product_type", default_type)
    page_num = request.GET.get("page", 1)

    conditions = {}
    for key in request.GET:
        if key in ["product_type", "page"]:
            continue
        # 나머지 키는 search/filter.js 필터 name과 1:1 대응

        values = _get_condition_values(key, request.GET.getlist(key))
        if values is not None and values != []:
            conditions[key] = values

    products = search_product(product_type, [], conditions)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(page_num)

    return render(
        request,
        "searchpage.html",
        {
            "page_obj": page_obj,
            "start_index": page_obj.start_index(),
            "end_index": page_obj.end_index()
        }
    )
