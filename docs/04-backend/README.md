# Backend 파트 문서

[← Docs 홈](../README.md)

**담당**: 유동현  
**스택**: Django 6.0, Django ORM, JSON API views

## 문서 목록

| 문서 | 내용 |
|------|------|
| [django-apps.md](django-apps.md) | 앱별 책임·뷰·모델 |

## 핵심 모듈

| 모듈 | 역할 |
|------|------|
| `config/` | 설정·루트 URL |
| `api/` | AJAX JSON 엔드포인트 |
| `accounts/` | 인증·찜 |
| `products/` | 상품 CRUD·검색 페이지 |
| `chats/` | 채팅방 SSR |
| `common/` | AI·검색 유틸 (앱 아님, 공유 라이브러리) |

## 연관 문서

- [REST API](../06-api/rest-api.md)
- [DB 스키마](../05-database/schema-and-erd.md)
- [LangGraph](../07-ai-modeling/langgraph-flow.md)
