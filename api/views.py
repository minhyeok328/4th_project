import json
from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import UserFavorite
from common.utils import get_product
from common import llm

# Create your views here.
def check_favorite(request, product_code):
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

