# Django 앱 상세

[← Backend 홈](README.md)

## INSTALLED_APPS (`config/settings.py`)

`mainpage`, `accounts`, `products`, `chats`, `tailwind`, `theme`, `django.contrib.humanize` + Django 기본 앱

`AUTH_USER_MODEL = "accounts.Account"`

## mainpage

| 항목 | 내용 |
|------|------|
| URL | `''` → `mainpage` |
| View | `views.mainpage` |
| 역할 | 카테고리 진입·LG봇 CTA |

→ [메인 기능](../08-features/main-page.md)

## products

| 항목 | 내용 |
|------|------|
| Models | `ProductTV`, `ProductFridge`, `ProductWash`, `ProductAC`, `ProductVAC`, `ScreenResolution` |
| 검색 | `search_model()` 클래스 메서드 — lookup: `gte`, `lte`, `in`, `icontains`, `exact` |
| Views | `searchpage`, `productpage` |
| URLs | `''`, `'<product_code>/'` |

→ [검색](../08-features/search-and-filter.md) · [상세](../08-features/product-detail.md)

## accounts

| Model | 필드·관계 |
|-------|-----------|
| `Account` | `nickname`, `profile_picture`, `AbstractUser` |
| `UserFavorite` | FK `account`, `product_code` |

| View | 메서드 | 설명 |
|------|--------|------|
| `loginpage` | GET/POST | 세션 로그인 |
| `registerpage` | POST | `create_user` |
| `mypage` | GET/POST | 프로필·찜 토글(JSON) |
| `logout_view` | — | 세션 종료 |

→ [계정·찜](../08-features/accounts-and-favorites.md)

## chats

| Model | 설명 |
|-------|------|
| `Chatroom` | `name`, `timestamp`, `agent_state` (JSON) |
| `SingleChat` | `index`, `is_userchat`, `content` |

| View | 설명 |
|------|------|
| `chatpage` | 로그인 필수, 방 목록·히스토리·삭제 |

→ [채팅 기능](../08-features/chat-lgneer.md)

## api

JSON 전용. `app_name = "api"`

| View | 경로 |
|------|------|
| `send_chat` | `send_chat/` |
| `favorite` | `favorite/<product_code>/` |
| `check_favorite` | `check_favorite/<product_code>/` |

→ [REST API](../06-api/rest-api.md)

## common (공유 패키지)

| 파일 | 역할 |
|------|------|
| `llm.py` | LangGraph, `add_chat()` |
| `llm_agent.py` | 노드별 LLM 호출 |
| `vector_search.py` | Pinecone |
| `utils.py` | 제품 조회·검색·찜 목록 |

앱으로 등록되지 않으며 `products`, `chats`, `api`에서 import합니다.

## 미들웨어·보안 (개발 기준)

- CSRF: 폼·`fetch`에 `X-CSRFToken`
- `DEBUG=True` — 배포 시 변경 필요

## 관련 문서

- [시스템 아키텍처](../02-architecture/system-architecture.md)
- [디렉터리 구조](../02-architecture/directory-structure.md)
