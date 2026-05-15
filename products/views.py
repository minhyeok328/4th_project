from django.shortcuts import render, redirect
from common.utils import get_product
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

    if request.method != "GET":
        query = urlencode({
            "product_type": default_type,
            "page": 1
        })

        return redirect(f"{request.path}?{query}")
    
    product_type = request.GET.get("product_type", default_type)
    page_num = request.GET.get("page", 1)

    # key in request.GET

    return render(
        request,
        "searchpage.html"
    )
