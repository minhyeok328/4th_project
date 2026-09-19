# API 명세

[문서 홈](../README.md) · [백엔드](../04-backend/README.md)

기준 구현: [api/urls.py](../../api/urls.py), [api/views.py](../../api/views.py), [accounts/views.py](../../accounts/views.py). 별도 OpenAPI·DRF 스키마는 없습니다.

## 공통 계약

Django 세션 쿠키로 인증합니다. POST에는 `X-CSRFToken` 또는 폼의 `csrfmiddlewaretoken`이 필요합니다. CSRF 실패는 뷰에 도달하기 전에 403으로 처리되며 JSON 응답을 보장하지 않습니다. 클라이언트는 [ApiResponse](../../static/js/api-response.js)로 응답 타입과 실패를 검사합니다.

## 채팅 전송

`POST /api/send_chat/`, Content-Type `application/json`, 로그인 필수.

```json
{"chat_id": null, "user_input": "500L 이상 냉장고 추천해줘"}
```

`user_input`은 공백이 아닌 문자열이며 앞뒤 공백을 제거합니다. `chat_id`가 비어 있거나 정수 변환에 실패하거나 해당 사용자 소유 방이 아니면 새 방을 만듭니다. 새 이름은 입력 앞 30자입니다.

```json
{
  "response": "추천 답변 본문",
  "response_tail": "가능한 조건 안내",
  "chat_id": 3,
  "chatroom_name": "500L 이상 냉장고 추천해줘"
}
```

`response_tail`은 보조 표시이며 대화 메시지로 저장하지 않습니다. 응답은 그래프가 끝난 뒤 한 번 반환하며 스트리밍하지 않습니다.

| 상태 | 처리 |
|---|---|
| 200 | 그래프 완료 |
| 400 | JSON 문법 오류, 누락·공백·문자열이 아닌 `user_input` |
| 401 | 비로그인 |
| 405 | POST 외 메서드 |
| 403 | CSRF 검사 실패 |
| 500 가능 | 외부 모델·DB·벡터 서비스 예외, JSON 최상위 배열·null 등 비객체 입력 |

뷰가 반환하는 400·401·405 본문은 `response=""`, `response_tail=""`, `chat_id=null`이며 별도 `error` 코드는 없습니다. 모든 JSON 타입을 검증하는 계약으로 해석하면 안 됩니다.

## 화면에서 사용하는 찜 토글

`POST /accounts/mypage/`, 세션과 CSRF 필수, 폼 데이터:

```text
action=toggle_favorite&product_code=TVT_EXAMPLE
```

`TVT_EXAMPLE`은 형식 설명용이며 실제 동작 확인에는 로컬 DB의 상품 코드를 사용합니다.

| 상태 | 응답 |
|---|---|
| 200 추가 | `{"ok": true, "favorited": true}` |
| 200 해제 | `{"ok": true, "favorited": false}` |
| 400 코드 누락 | `{"ok": false, "error": "missing_product_code"}` |
| 비로그인 | 로그인 페이지로 redirect |

이 경로는 비어 있지 않은 상품 코드의 실재 여부를 검사하지 않습니다. 기존 찜이 있으면 해당 코드의 행을 삭제하고 없으면 생성합니다. 동일 페이지의 `action=update_profile`은 닉네임·사진을 저장 후 redirect, `action=logout`은 세션을 종료 후 메인으로 redirect합니다.

## 레거시 찜 API

| 경로 | 동작 | `is_favorite` 의미 |
|---|---|---|
| `POST /api/favorite/<product_code>/` | 추가·해제 토글; 추가 시 상품 존재 검사 | true는 추가됨, false는 해제·실패·비로그인 |
| `POST /api/check_favorite/<product_code>/` | 상태 변경 없음 | true는 아직 찜하지 않음, false는 이미 찜함·비로그인 |

두 API의 같은 응답 키가 같은 의미를 나타내지 않습니다. `check_favorite`는 상품 존재를 검사하지 않습니다. 두 뷰 모두 POST 외 메서드의 응답이 구현되어 있지 않아 정상 405 계약을 제공하지 않습니다. 현재 상세·마이페이지 UI는 위의 마이페이지 토글을 사용합니다.

## 화면용 폼과 GET

| 요청 | 처리 |
|---|---|
| GET `/products/?product_type=REF&page=1` | 조건 검색 HTML |
| GET `/products/<product_code>/` | 상품 상세 HTML; 미존재 항목은 빈 데이터로 렌더 |
| POST `/accounts/` | 로그인 폼 `username`, `password` |
| POST `/accounts/register/` | 가입 폼 `username`, `password`, `nickname`, 선택 `profile_picture` |
| POST `/accounts/logout/` | 로그아웃 |
| POST `/chats/` | 폼 `delete_id`로 사용자 소유 방 삭제 |

[검색 파라미터](../08-features/search-and-filter.md) · [채팅 흐름](../08-features/chat-lgneer.md)
