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