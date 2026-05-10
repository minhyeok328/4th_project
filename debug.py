"""
이 파일은 실행하는 파일이 아니라
cmd에서 다음 명령어

python manage.py shell

로 접근할 수 있는 django shell 안쪽에서 실행하는 명령어
"""

# 모든 유저 삭제
from accounts.models import Account
for acnt in Account.objects.all():
    if acnt.profile_picture:
        acnt.profile_picture.delete(save=False)

    acnt.delete()

# 샘플 유저 생성
from django.core.files import File
from accounts.models import Account

with open("static/sampleprofile.png", "rb") as f:
    tup = Account.objects.create_user(
        username = "admin",
        password = "1234",
        nickname = "pickle",
        profile_picture = File(f, name="userinput.png")
    )