from django.shortcuts import render, redirect
from urllib.parse import urlencode

# Create your views here.
def chatpage(request):
    if not request.user.is_authenticated:
        return redirect("accounts:loginpage")

    chatrooms = request.user.view_chatrooms()

    if request.method == "POST":
        target = request.POST.get("delete_id", None)
        if target is not None:
            target = int(target)
            if target in [c.id for c in chatrooms]:
                request.user.delete_chatroom(target)
        
        return redirect("chats:chatpage")

    chats = []
    if "chat_id" in request.GET.keys():
        chat_id = int(request.GET.get("chat_id"))
        for c in chatrooms:
            if c.id == chat_id:
                chats = c.view_chats()

    return render(
        request,
        "chatpage.html",
        {
            "chatrooms": chatrooms,
            "chats": chats
        }
    )