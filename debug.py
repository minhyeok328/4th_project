"""
이 파일은 실행하는 파일이 아니라
cmd에서 다음 명령어

python manage.py shell

로 접근할 수 있는 django shell 안쪽에서 실행하는 명령어

안쪽에서 from debug import * 하면 아래 모든 함수를 사용 가능
"""

# 모든 유저 삭제
def delete_users():
    from accounts.models import Account
    from accounts.models import UserFavorite

    for acnt in Account.objects.all():
        if acnt.profile_picture:
            acnt.profile_picture.delete(save=False)

        acnt.delete()

    print(len(UserFavorite.objects.all()))

    for fav in UserFavorite.objects.all():
        fav.delete()

# 샘플 유저 생성
def create_sample_user():
    from django.core.files import File
    from accounts.models import Account

    with open("static/sampleprofile.png", "rb") as f:
        usr = Account.objects.create_user(
            username = "admin",
            password = "1234",
            nickname = "pickle",
            profile_picture = File(f, name="userinput.png")
        )

    favorites = ["ACT000", "TVT003", "VAC010"]
    for f in favorites:
        usr.add_favorite(f)

    return usr

def add_chatrooms(user):
    ls = ["room1", "room2", "room3", "room4"]

    for l in ls:
        user.add_chatroom(l)

def add_chats(chatroom):
    ls = [
        (True, "chat1"),
        (False, "chat2"),
        (True, "chat3"),
        (False, "chat4"),
        (True, "chat5")
    ]

    for l in ls:
        chatroom.add_chat(l[0], l[1])

def print_chats(chatroom):
    cs = chatroom.view_chats()

    for c in cs:
        print(f"{c.id}\t{c.index}\t{"user" if c.is_userchat else "agent"}\t{c.content}")

def search_test(code, ls, dct):
    from common.utils import get_model
    mod = get_model(code)

    res = mod.search(ls, **dct)
    for r in res:
        print(r)

    return res

"""
from dotenv import load_dotenv
from debug import *
from common import llm
from pprint import pprint

load_dotenv()
state = mockup_state()
"""
def mockup_state():
    return {
        # 사용자 id
        "user_id": 11,

        # 현재 대화 상태
        "state": "initial",

        # 제품군 / 슬롯
        "product_type": "ACT",
        "slots": {"price_gte": 1000000},

        # DB 검색 결과
        "result_count": 3,
        "search_results": ["ACT010", "ACT015", "ACT020"]
    }

def invoke_test():
    from common import llm
    from pprint import pprint

    state = {"state":"initial", "slots":{}}
    chats = []

    while True:
        userinput = input("사용자 입력: ")
        if userinput == "0":
            break
        
        chats.append(userinput)
        state["chats"] = chats

        res = llm.graph_instance.invoke(state)
        print(f"ai 답변: {res["response"]}")
        chats.append(res["response"])

        print("="*30)
        pprint(res)
        print("="*30)

        state = {}
        state["state"] = res["next_state"]
        state["product_type"] = res.get("product_type", "")
        state["slots"] = res["slots"]
        state["manual_results"] = res.get("manual_results", [])

def add_chat_test(chat_id:int):
    from chats.models import Chatroom
    from common import llm

    room = Chatroom.objects.filter(id=chat_id).first()

    if room is None:
        print("Chatroom ID 오류")
        return
    
    while True:
        userinput = input("사용자 입력: ")
        if userinput == "0":
            break

        head, tail = llm.add_chat(room, userinput)

        print("ai 답변:", head)
        print("답변 tail:", tail)