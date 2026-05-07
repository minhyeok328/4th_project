from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

# Create your views here.
def accountpage(request):
    return render(
        request,
        "accountpage.html"
    )

def loginpage(request):
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