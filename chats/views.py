"""
챗봇 페이지 SSR 뷰.

- GET: 사이드바 대화 목록·선택 chat_id의 메시지를 템플릿에 전달
- POST: delete_id로 대화방 삭제 후 리다이렉트
- 실시간 LLM 응답은 api.views.send_chat(JSON) — chatpage.js가 호출
"""

from django.db.models import Count
from django.shortcuts import render, redirect


def chatpage(request):
    """LG봇 화면 렌더. 비로그인 시 로그인 페이지로 리다이렉트."""
    if not request.user.is_authenticated:
        return redirect("accounts:loginpage")

    chatrooms = (
        request.user.chatrooms
        .annotate(chat_count=Count("chats"))
        .filter(chat_count__gt=0)
        .order_by("-timestamp")
    )

    # 사이드바 삭제 폼: CSRF POST → 해당 chatroom 제거
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

    # ?chat_id= — 열린 대화의 메시지 목록(chats)을 템플릿에 넘김
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
