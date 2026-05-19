from django.db.models import Count
from django.shortcuts import render, redirect


def chatpage(request):
    if not request.user.is_authenticated:
        return redirect("accounts:loginpage")

    chatrooms = (
        request.user.chatrooms
        .annotate(chat_count=Count("chats"))
        .filter(chat_count__gt=0)
        .order_by("-timestamp")
    )

    if request.method == "POST":
        target = request.POST.get("delete_id", None)
        if target is not None:
            try:
                target = int(target)
            except (TypeError, ValueError):
                target = None
            if target is not None and request.user.chatrooms.filter(id=target).exists():
                request.user.remove_chatroom(target)

        return redirect("chats:chatpage")

    chats = []
    current_chatroom = None

    raw_chat_id = request.GET.get("chat_id")
    if raw_chat_id is not None:
        try:
            chat_id = int(raw_chat_id)
        except (TypeError, ValueError):
            chat_id = None

        if chat_id is not None:
            for c in chatrooms:
                if c.id == chat_id:
                    current_chatroom = c
                    chats = c.view_chats()
                    break

    return render(
        request,
        "chatpage.html",
        {
            "chatrooms": chatrooms,
            "chats": chats,
            "current_chatroom": current_chatroom,
        }
    )
