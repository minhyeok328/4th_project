"""
REST JSON API (챗봇·찜).

- send_chat: chatpage.js → LangGraph
- favorite / check_favorite: REST 대안(현재 UI는 accounts:mypage toggle_favorite 주로 사용)
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import UserFavorite
from common.utils import get_product
from common import llm

def check_favorite(request, product_code):
    """
    찜 **가능 여부**만 조회(토글하지 않음).

    POST, 로그인 시: 이미 찜이면 is_favorite=False, 아니면 True.
    wishlist-toggle.js는 mypage POST를 쓰며, 이 엔드포인트는 레거시/외부 연동용.
    """
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"is_favorite": False})

        userfav = request.user.favorites.filter(product_code=product_code).first()

        if userfav:
            res = False
        else:
            res = True
        
        return JsonResponse({"is_favorite": res})

def favorite(request, product_code):
    """
    찜 on/off 토글 REST API.

    POST: 기존 UserFavorite 있으면 삭제 후 is_favorite=False, 없으면 상품 존재 시 생성.
    응답 키는 check_favorite와 동일하게 is_favorite (wishlist의 favorited와 다름).
    """
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"is_favorite": False})

        userfav = request.user.favorites.filter(product_code=product_code).first()

        if userfav:
            res = False
            userfav.delete()
        else:
            _, p = get_product(product_code)

            if p is not None:
                res = True
                _ = UserFavorite.objects.create(
                    account=request.user,
                    product_code=product_code
                )
            else:
                res = False

        return JsonResponse({"is_favorite":res})
    
def send_chat(request):
    """
    챗봇 AJAX 엔드포인트 — chatpage.js가 JSON POST.

    Body: { chat_id?, user_input }
    - chat_id 없/무효 시 새 Chatroom 생성
    - common.llm.add_chat으로 LangGraph 실행 후 response·response_tail 반환
    """
    if request.method != "POST":
        return JsonResponse({"response": "", "response_tail": "", "chat_id": None}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"response": "", "response_tail": "", "chat_id": None}, status=401)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"response": "", "response_tail": "", "chat_id": None}, status=400)

    raw_chat_id = data.get("chat_id", None)
    user_input = data.get("user_input", None)

    if not isinstance(user_input, str) or not user_input.strip():
        return JsonResponse({"response": "", "response_tail": "", "chat_id": None}, status=400)

    user_input = user_input.strip()

    chat_id = None
    if raw_chat_id not in (None, "", 0, "0"):
        try:
            chat_id = int(raw_chat_id)
        except (TypeError, ValueError):
            chat_id = None

    # 기존 대화방이 없으면 user_input 앞 30자로 방 이름을 만들어 신규 생성
    target_room = None
    if chat_id is not None:
        for c in request.user.view_chatrooms():
            if c.id == chat_id:
                target_room = c
                break

    if target_room is None:
        name = user_input[:30] or "새 대화"
        target_room = request.user.add_chatroom(name)

    root_url = f"{request.scheme}://{request.get_host()}"
    response, response_tail = llm.add_chat(root_url, target_room, user_input)

    return JsonResponse({
        "response": response,
        "response_tail": response_tail,
        "chat_id": target_room.id,
        "chatroom_name": target_room.name,
    })

