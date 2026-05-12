from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

# Create your views here.
def accountpage(request):
    if not request.user.is_authenticated:
        return redirect("accounts:loginpage")

    if request.method == "POST":
        if request.POST.get("action") == "logout":
            logout(request)
            return redirect("mainpage:mainpage")
        else:
            return redirect("accounts:accountpage")

    return render(
        request,
        "accountpage.html",
        {
            "username": request.user.username,
            "nickname": request.user.nickname
        }
    )

def loginpage(request):
    if request.user.is_authenticated:
        return redirect("accounts:accountpage")

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