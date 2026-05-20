from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from common.utils import get_product, search_product

LIST_CONDITION_SUFFIXES = ("_in", "_icontains", "__in", "__icontains")


def _is_list_condition(key):
    return key.endswith(LIST_CONDITION_SUFFIXES)


def _get_condition_values(key, values):
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


# Create your views here.
def productpage(request, product_code):
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
    default_type = "REF"

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
