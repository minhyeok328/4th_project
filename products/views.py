from django.shortcuts import render
from common.utils import get_product

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
    return render(
        request,
        "searchpage.html"
    )
