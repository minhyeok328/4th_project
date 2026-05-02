from django.shortcuts import render

# Create your views here.
def chatpage(request):
    return render(
        request,
        "chatpage.html"
    )