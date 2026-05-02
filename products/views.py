from django.shortcuts import render

# Create your views here.
def productpage(request):
    return render(
        request,
        "productpage.html"
    )

def searchpage(request):
    return render(
        request,
        "searchpage.html"
    )
