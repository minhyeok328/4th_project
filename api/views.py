import json
from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import UserFavorite
from common.utils import get_product

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
        return
    
    if not request.user.is_authenticated:
        return JsonResponse({"response": ""})
        
    data = json.loads(request.body)
    chat_id = data.get("chat_id", None)
    user_input = data.get("user_input", None)

    if chat_id is None or user_input is None:
        return JsonResponse({"response": ""})
    
    chat_id = int(chat_id)

    for c in request.user.view_chatrooms():
        if c.id != chat_id:
            continue
        
        c.add_chat(True, user_input)

        response = "안녕"

        return JsonResponse({"response":f"사용자 입력: {user_input} > ai 답변: {response}"})

    return JsonResponse({"response": ""})

