"""
챗봇 대화방·메시지 ORM.

연결:
- chats.views.chatpage: 목록·?chat_id= 메시지 SSR, POST delete_id
- api.views.send_chat → common.llm.add_chat: agent_state 갱신·메시지 저장
- chatpage.js: data-server-message 복원, insertSidebarRoom

agent_state: LangGraph GraphState 일부(state, slots, product_type 등) JSON 영속화
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

def default_state():
    """신규 Chatroom — llm.GraphState 초기값과 동일한 최소 키."""
    return {"state":"initial", "slots":{}}

class Chatroom(models.Model):
    """사용자별 대화방. account.chatrooms 역참조."""
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chatrooms"
    )
    
    name = models.CharField(max_length=30)
    timestamp = models.DateTimeField(default=timezone.now)
    agent_state = models.JSONField(default=default_state)

    def add_chat(self, is_userchat, content):
        """메시지 1건 추가 후 timestamp 갱신. index는 방 내 순서(0부터)."""
        ind = self.chats.count()

        _ = SingleChat.objects.create(
            chatroom=self,
            index=ind,
            is_userchat=is_userchat,
            content=content
        )

        self.updated()

    def view_chats(self):
        """index 오름차순 SingleChat queryset — 템플릿·add_chat 입력 순서."""
        return self.chats.order_by("index")

    def updated(self):
        """사이드바 '최근 대화' 정렬용 timestamp만 now로 저장."""
        self.timestamp = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.name:<30}:{self.timestamp}"

class SingleChat(models.Model):
    """대화방 내 한 턴. is_userchat True=사용자, False=봇(assistant)."""
    chatroom = models.ForeignKey(
        Chatroom,
        on_delete=models.CASCADE,
        related_name="chats"
    )
    index = models.IntegerField()
    is_userchat = models.BooleanField()
    content = models.TextField()

    def __str__(self):
        role = "user" if self.is_userchat else "agent"
        return f"{self.index:>5}\t{role}\t{self.content}"