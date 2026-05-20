# REST API 명세

[← Docs 홈](../README.md) · [Backend api 앱](../04-backend/django-apps.md#api)

Base URL: `/api/` (`api.urls`, `app_name = "api"`)

## 공통

| 항목 | 값 |
|------|-----|
| 인증 | Django 세션 (`sessionid` 쿠키) |
| CSRF | POST 시 `X-CSRFToken` 또는 폼 `csrfmiddlewaretoken` |
| Content-Type | `application/json` (JSON API), `multipart/form-data` (마이페이지) |

---

## POST `/api/send_chat/`

LG봇 메시지 전송·LangGraph 실행.

### Request

```json
{
  "chat_id": null,
  "user_input": "500L 이상 냉장고 추천해줘"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `chat_id` | int \| null | 기존 방 ID. null/0이면 새 방 생성 |
| `user_input` | string | 사용자 메시지 (필수, 공백 불가) |

### Response `200`

```json
{
  "response": "추천 답변 본문...",
  "response_tail": "가능한 조건: 가격, 용량, ...",
  "chat_id": 3,
  "chatroom_name": "500L 이상 냉장고 추천해줘"
}
```

`response_tail`은 UI 보조 문자열(예: 조건 안내·링크 문구)이며, 채팅 로그에는 저장되지 않습니다.

### Errors

| Status | 조건 |
|--------|------|
| 401 | 비로그인 |
| 400 | JSON 파싱 실패, `user_input` 누락/빈 문자열 |
| 405 | GET 등 비-POST |

### 처리 흐름

1. `chat_id`로 사용자 소유 `Chatroom` 조회
2. 없으면 `user_input[:30]`으로 새 `Chatroom` 생성
3. `llm.add_chat(root_url, room, user_input)` 호출
4. 사용자·봇 메시지를 `SingleChat`에 저장, `agent_state` 갱신

→ [채팅 기능](../08-features/chat-lgneer.md) · [LangGraph](../07-ai-modeling/langgraph-flow.md)

---

## POST `/api/favorite/<product_code>/`

찜 토글.

### Response `200`

```json
{ "is_favorite": true }
```

| `is_favorite` | 의미 |
|---------------|------|
| `true` | 찜 **추가됨** (응답 시점에 찜 상태) |
| `false` | 찜 **해제됨** 또는 실패 |

- 비로그인: `{ "is_favorite": false }`
- 존재하지 않는 `product_code`: 추가 실패 → `false`

### 구현 참고

상품 상세·마이페이지 UI는 주로 `POST /accounts/mypage/` (`action=toggle_favorite`)를 사용합니다. API 엔드포인트는 동일 도메인 로직의 REST 대안입니다.

---

## POST `/api/check_favorite/<product_code>/`

찜 여부 확인 (토글 없음).

### Response

```json
{ "is_favorite": true }
```

- `true`: 현재 **찜 안 됨** → 추가 가능
- `false`: 이미 찜됨 또는 비로그인

> 응답 의미가 `favorite` 토글과 반대 부호처럼 보일 수 있어, 신규 연동 시 [accounts-and-favorites](../08-features/accounts-and-favorites.md)의 마이페이지 API 사용을 권장합니다.

---

## 마이페이지 비-REST (관련)

`POST /accounts/mypage/`

| action | 응답 |
|--------|------|
| `toggle_favorite` | `{ "ok": true, "favorited": bool }` |
| `update_profile` | redirect |
| `logout` | redirect |

---

## URL reverse (Django)

```python
reverse("api:send_chat")
reverse("api:favorite", kwargs={"product_code": "REFF123"})
```

템플릿: `{% url 'api:send_chat' %}` (`chat_main.html` data 속성)

## 관련 문서

- [실행·로컬 테스트](../01-getting-started/run-and-operations.md#채팅-api-로컬-테스트)
- [계정·찜](../08-features/accounts-and-favorites.md)
