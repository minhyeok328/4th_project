from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from common.utils import get_product
from .models import Account, UserFavorite

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
        action = request.POST.get("action")

        if action == "logout":
            logout(request)
            return redirect("mainpage:mainpage")

        if action == "toggle_favorite":
            product_code = request.POST.get("product_code", "").strip()
            if not product_code:
                return JsonResponse({"ok": False, "error": "missing_product_code"}, status=400)

            favorites = request.user.favorites.filter(product_code=product_code)
            if favorites.exists():
                favorites.delete()
                return JsonResponse({"ok": True, "favorited": False})

            UserFavorite.objects.create(account=request.user, product_code=product_code)
            return JsonResponse({"ok": True, "favorited": True})

        if action == "update_profile":
            nickname = request.POST.get("nickname", "").strip()
            profile_picture = request.FILES.get("profile_picture")

            if nickname:
                request.user.nickname = nickname
            if profile_picture:
                request.user.profile_picture = profile_picture
            request.user.save()
            return redirect("accounts:mypage")

        return redirect("accounts:mypage")

    favorites = [
        product
        for favorite in request.user.favorites.all()
        if (product := get_product(favorite.product_code)[1]) is not None
    ]

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
