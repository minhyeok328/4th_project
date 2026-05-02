from django.shortcuts import render

# Create your views here.
def accountpage(request):
    return render(
        request,
        "accountpage.html"
    )

def loginpage(request):
    return render(
        request,
        "loginpage.html"
    )