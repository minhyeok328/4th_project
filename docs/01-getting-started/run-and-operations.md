# 실행 및 일상 운영

[← Docs 홈](../README.md) · [개발 환경](development-environment.md)

## 웹 서버 실행

```powershell
# 4th_project 루트, venv 활성화 후
python manage.py runserver
```

브라우저: `http://127.0.0.1:8000/`

## URL·페이지 빠른 참조

| 경로 | 화면 | 로그인 |
|------|------|--------|
| `/` | 메인 | 불필요 |
| `/products/` | 필터 검색 | 불필요 |
| `/products/<product_code>/` | 상품 상세 | 불필요 (찜은 필요) |
| `/chats/` | LG봇 | **필요** |
| `/accounts/` | 로그인 | — |
| `/accounts/register/` | 회원가입 | — |
| `/accounts/mypage/` | 마이페이지 | **필요** |

상세 라우팅: [페이지·URL 매핑](../03-frontend/pages-and-routes.md)

## 개발 시 자주 쓰는 명령

| 작업 | 명령 |
|------|------|
| 마이그레이션 | `python manage.py migrate` |
| 슈퍼유저 | `python manage.py createsuperuser` |
| Tailwind watch | `cd theme/static_src && npm run dev` |
| 정적 수집 (배포) | `python manage.py collectstatic` |

## 채팅 API 로컬 테스트

```http
POST http://127.0.0.1:8000/api/send_chat/
Content-Type: application/json
Cookie: sessionid=...   # 로그인 세션 필요

{
  "chat_id": null,
  "user_input": "500L 이상 냉장고 추천해줘"
}
```

명세: [REST API](../06-api/rest-api.md)

## 알려진 제한 (운영 시)

- 비밀번호 찾기·결제 버튼: UI만 존재, 서버 미연동
- 상품 상세 리뷰/Q&A: 일부 목업
- `DEBUG=True`, `ALLOWED_HOSTS=[]` — 로컬 개발 기준

전체 제한사항: [루트 README §11](../../README.md#11-limitations)

## 관련 문서

- [채팅 기능 흐름](../08-features/chat-lgneer.md)
- [LangGraph 플로우](../07-ai-modeling/langgraph-flow.md)
