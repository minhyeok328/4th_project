# LG봇 채팅

[기능 안내](README.md) · [LangGraph](../07-ai-modeling/langgraph-flow.md)

## 화면과 저장

`/chats/`는 로그인 필수입니다. [chats/views.py](../../chats/views.py)가 사용자 방 목록과 `?chat_id=` 메시지를 [chatpage.html](../../templates/chatpage.html)에 전달합니다. 메시지가 있는 방만 목록에 표시하며 POST `delete_id`로 소유한 방을 삭제합니다.

## 한 턴의 처리

1. [chatpage.js](../../static/js/chatpage.js)가 입력을 검사하고 전송 상태를 잠급니다.
2. `POST /api/send_chat/`에 `chat_id`, `user_input` JSON을 보냅니다.
3. API가 사용자 소유 방을 찾아 `common.llm.add_chat`을 호출합니다.
4. 사용자 메시지를 저장하고 그래프가 ORM·매뉴얼을 검색합니다.
5. 방의 상태와 봇 메시지를 저장한 뒤 답변 JSON을 반환합니다.
6. 화면에서 답변을 마크다운으로 표시하고 새 방 목록을 갱신합니다.

`response_tail`은 가능한 조건 등 보조 문자열로, 메시지 기록에 저장하지 않습니다. 외부 오류로 중간 실패하면 사용자 메시지만 저장될 수 있습니다.

## 후속 질문과 찜

`agent_state`에 `state`, `product_type`, `slots`, `manual_results` 등을 보관합니다. 후속 질문은 이전 조건을 사용하고 새 제품군 질문은 분류를 다시 거칩니다. 찜 요청은 `intent_router`에서 사용자 찜 코드를 필터로 만듭니다. 빈 찜·매뉴얼 검색 결과에서 범위가 유지되는지는 [검증 대상](../10-quality/verification-and-limitations.md)입니다.

## 클라이언트 처리

`ApiResponse.fetchJson`과 JSON POST 빌더를 사용합니다. 실패는 말풍선으로 표시하고 `inFlight`로 동시 전송을 막습니다. `renderMarkdown`과 `sanitizeChatHtml`에서 태그·속성·http/https URL을 제한합니다. 서버 히스토리는 textContent에서 복원합니다.

모바일 사이드바는 backdrop·ARIA·ESC와 body 스크롤 잠금을 사용합니다. 이 코드의 존재는 실기기 검증을 대신하지 않습니다. 401 응답에서 자동 로그인 이동이 연결되어 있지 않은 점과 긴 대화 전체 재렌더링을 확인해야 합니다.

[API 명세](../06-api/api-reference.md) · [JavaScript 상세](../03-frontend/client-javascript.md) · [RAG](../07-ai-modeling/rag-pinecone.md)
