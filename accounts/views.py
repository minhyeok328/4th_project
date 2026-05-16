from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from common.utils import get_product
from .models import Account

# Create your views here.
def registerpage(request):
    if request.user.is_authenticated:
        return redirect("accounts:mypage")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        nickname = request.POST.get("nickname")
        pic = request.FILES.get("profile_picture", None)

        Account.objects.create_user(
            username=username,
            password=password,
            nickname=nickname,
            profile_picture=pic
        )

        return redirect("accounts:loginpage")


    return render(
        request,
        "registerpage.html"
    )


def mypage(request):
    if not request.user.is_authenticated:
        return redirect("accounts:loginpage")

    if request.method == "POST":
        if request.POST.get("action") == "logout":
            logout(request)
            return redirect("mainpage:mainpage")
        else:
            return redirect("accounts:mypage")

    favorites = [get_product(f.product_code)[1] for f in request.user.favorites.all()]

    return render(
        request,
        "mypage.html",
        {
            "favorites": favorites
        }
    )

def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("mainpage:mainpage")


def loginpage(request):
    if request.user.is_authenticated:
        return redirect("accounts:mypage")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            request.session.pop("login_fail", None)
            return redirect("mainpage:mainpage")

        request.session["login_fail"] = True
        return redirect("accounts:loginpage")

    login_fail = request.session.pop("login_fail", False)

    return render(
        request,
        "loginpage.html",
        {
            "login_fail": login_fail
        }
    )