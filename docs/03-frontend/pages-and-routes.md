# 페이지 · URL 매핑

[← Frontend 홈](README.md) · [Backend URL](../04-backend/django-apps.md)

## 루트 URL (`config/urls.py`)

| include | prefix |
|---------|--------|
| `mainpage.urls` | `/` |
| `accounts.urls` | `/accounts/` |
| `products.urls` | `/products/` |
| `chats.urls` | `/chats/` |
| `api.urls` | `/api/` |

## 페이지 매핑

| URL | name | View | Template |
|-----|------|------|----------|
| `/` | `mainpage:mainpage` | `mainpage.views.mainpage` | `mainpage.html` |
| `/products/` | `products:searchpage` | `products.views.searchpage` | `searchpage.html` |
| `/products/<code>/` | `products:productpage` | `products.views.productpage` | `productpage.html` |
| `/chats/` | `chats:chatpage` | `chats.views.chatpage` | `chatpage.html` |
| `/accounts/` | `accounts:loginpage` | `accounts.views.loginpage` | `loginpage.html` |
| `/accounts/register/` | `accounts:registerpage` | `accounts.views.registerpage` | `registerpage.html` |
| `/accounts/mypage/` | `accounts:mypage` | `accounts.views.mypage` | `mypage.html` |
| `/accounts/logout/` | `accounts:logout` | `accounts.views.logout_view` | redirect |

## 검색 쿼리 파라미터

`searchpage`는 `product_type`, `page`가 없으면 기본값으로 리다이렉트합니다.

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `product_type` | `REF` | TVT / REF / WMT / ACT / VAC |
| `page` | `1` | 페이지 번호 |
| `price__gte` 등 | — | Django lookup 형식 필터 |

기능 상세: [검색·필터](../08-features/search-and-filter.md)

## 채팅 쿼리

| 파라미터 | 설명 |
|----------|------|
| `chat_id` | 선택한 대화방 ID (`chatpage` GET) |

## 관련 문서

- [실행·URL 빠른 참조](../01-getting-started/run-and-operations.md)
- [REST API](../06-api/rest-api.md)
