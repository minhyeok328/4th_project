# 백엔드

[문서 홈](../README.md)

## 요청 처리

Django 뷰가 SSR 화면과 일부 JSON API를 제공합니다. [config/urls.py](../../config/urls.py)에서 `mainpage`, `products`, `accounts`, `chats`, `api`의 URL을 연결합니다. Django REST Framework는 사용하지 않습니다.

| 영역 | 구현 | 주요 계약 |
|---|---|---|
| 인증 | [accounts/views.py](../../accounts/views.py) | `authenticate`, `login`, `logout`, `create_user` |
| 상품 | [products/views.py](../../products/views.py) | GET 조건 정규화·페이지네이션·상세 조회 |
| 찜 | `accounts.views.mypage` | 폼 POST `action=toggle_favorite` |
| 채팅 화면 | [chats/views.py](../../chats/views.py) | 사용자 소유 방 조회·삭제 |
| 채팅 API | [api/views.py](../../api/views.py) | JSON 입력 → 동기 LangGraph 실행 |
| 공유 함수 | [common/utils.py](../../common/utils.py) | 제품 코드 접두에 따른 모델 조회 |

## 인증과 데이터 저장

`AUTH_USER_MODEL`은 `accounts.Account`이며 Django 세션과 CSRF 미들웨어를 사용합니다. 채팅 페이지와 마이페이지는 비로그인 시 로그인 페이지로 이동하고, 채팅 API는 401 JSON을 반환합니다.

`Chatroom`은 사용자, `SingleChat`은 방에 연결됩니다. `add_chat`은 사용자 메시지를 먼저 저장하고 AI 답변을 나중에 저장합니다. 전체 요청을 감싼 트랜잭션이나 요청 ID 기반 중복 방지는 없으므로 AI 실패·동시 전송을 별도로 고려해야 합니다.

## 현재 제약

회원가입 뷰는 `create_user`를 직접 호출하며 폼 검증·중복 사용자 예외를 사용자 오류 화면으로 통합하지 않습니다. 마이페이지 찜 경로는 상품 존재를 검사하지 않고 코드를 저장합니다. 레거시 찜 API와의 차이를 [API 명세](../06-api/api-reference.md)에 기록했습니다.

[Django 앱 상세](django-apps.md) · [스키마와 ERD](../05-database/schema-and-erd.md) · [배포 조건](../09-deployment/deployment.md)
