# 계정 · 찜 (개인화)

[← 기능 인덱스](README.md) · [DB 스키마](../05-database/schema-and-erd.md)

## 개요

닉네임·프로필 사진 기반 회원 기능과 `product_code` 단위 찜 목록. 챗봇의 **찜 범위 검색**(`from_favorites`)에 사용됩니다.

## URL

| 경로 | 기능 |
|------|------|
| `/accounts/` | 로그인 |
| `/accounts/register/` | 회원가입 |
| `/accounts/mypage/` | 프로필·찜 목록 |
| `/accounts/logout/` | 로그아웃 |

## 모델

- `Account` — `AUTH_USER_MODEL`, `nickname`, `profile_picture`
- `UserFavorite` — `(account, product_code)` 다대일

헬퍼: `Account.add_favorite`, `view_chatrooms`, `add_chatroom` 등

## 마이페이지 POST 액션

| action | 설명 |
|--------|------|
| `toggle_favorite` | 찜 추가/삭제 → JSON |
| `update_profile` | 닉네임·사진 수정 |
| `logout` | 세션 종료 → 메인 |

### toggle_favorite 예시

```http
POST /accounts/mypage/
Content-Type: multipart/form-data
X-CSRFToken: ...

action=toggle_favorite&product_code=REFF12345678
```

```json
{ "ok": true, "favorited": true }
```

## 찜 ↔ 챗봇

LangGraph `db_search`에서 `from_favorites` 슬롯이 true이면:

```python
get_favorites(user_id)  # → product_code 리스트
# → search_model(..., range=favorites)
```

예: 「찜한 제품 중 에너지 1등급 냉장고」

## 프론트엔드 찜 UI (1차 개선)

| 화면 | 구현 |
|------|------|
| 상품 상세 | `wishlist-toggle.js` — `productPageWishlistToggle`, `#product-actions` data 속성 |
| 마이페이지 | `wishlist-toggle.js` — `mypageWishlistToggle`, 카드 제거·빈 목록 시 reload |
| 공통 | `wishlistInFlight`, 요청 중 버튼 disable, `ApiResponse` 파싱·실패 `alert` |

스크립트: `productpage.html`·`mypage.html`에서 `api-response.js` → `wishlist-toggle.js` 순 로드.

→ [client-javascript.md](../03-frontend/client-javascript.md)

## 로그인 가드

| 기능 | 비로그인 |
|------|----------|
| `/chats/` | 로그인 페이지 리다이렉트 |
| `send_chat` API | 401 |
| 상품 찜 | `wishlist-toggle.js`에서 로그인 페이지 이동 |
| 마이페이지 | 로그인 페이지 리다이렉트 |

> 검색 결과 등 비로그인 찜 진입 경로는 UI별로 상이할 수 있음 — [제한사항](../../README.md#11-limitations)

## REST 대안

- `POST /api/favorite/<code>/`
- `POST /api/check_favorite/<code>/`

→ [API 명세](../06-api/rest-api.md)

## 관련 문서

- [상품 상세 찜](product-detail.md#찜-연동)
- [채팅 from_favorites](chat-lgneer.md#찜-범위-검색)
- [Backend accounts](../04-backend/django-apps.md#accounts)
