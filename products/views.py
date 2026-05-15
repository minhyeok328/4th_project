from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from common.utils import get_product, search_product
from urllib.parse import urlencode

# Create your views here.
def productpage(request, product_code):
    product_type, product_data = get_product(product_code)

    return render(
        request,
        "productpage.html",
        {
            "product_type": product_type,
            "product_data": product_data
        }
    )

def searchpage(request):
    default_type = "REF"

    if "product_type" not in request.GET or "page" not in request.GET:
        query = urlencode({
            "product_type": request.GET.get("product_type", default_type),
            "page": request.GET.get("page", 1),
        })

        return redirect(f"{request.path}?{query}")
    
    product_type = request.GET.get("product_type", default_type)
    page_num = request.GET.get("page", 1)

    # key in request.GET
    conditions = {k: v for k, v in request.GET.items() if k not in ["product_type", "page"]}

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
