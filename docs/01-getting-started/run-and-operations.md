# 실행과 운영

[문서 홈](../README.md) · [개발 환경](development-environment.md)

## 로컬 실행

Python 환경, `.env`, DB 스키마·상품 데이터, Tailwind 빌드가 준비된 상태에서 실행합니다.

```powershell
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000/`에 접속합니다. 스타일 수정 시 별도 터미널의 `theme/static_src`에서 `npm run dev`를 실행합니다.

| 경로 | 용도 | 로그인 |
|---|---|---|
| `/` | 메인 | 불필요 |
| `/products/` | 검색 | 불필요 |
| `/products/<product_code>/` | 상세 | 불필요 |
| `/accounts/` | 로그인 | 불필요 |
| `/accounts/register/` | 회원가입 | 불필요 |
| `/accounts/mypage/` | 프로필·찜 | 필요 |
| `/chats/` | 채팅 | 필요 |

## 실행 확인

1. 메인과 검색을 열고 카테고리별 상품 데이터 유무를 확인합니다.
2. 유효한 상품 코드로 상세 화면을 열어 사양을 확인합니다.
3. 로그인 후 찜을 추가·해제하고 마이페이지를 다시 조회합니다.
4. 외부 서비스 사용이 가능한 환경에서 채팅을 보내고 대화방 재진입 시 메시지를 확인합니다.

채팅과 `debug.py`, 모델 평가 노트북은 외부 API를 호출하고 비용이 발생할 수 있습니다. JSON 호출의 세션·CSRF 요구사항은 [API 명세](../06-api/api-reference.md)를 참고합니다.

## 오류 확인

| 현상 | 확인할 위치 |
|---|---|
| 시작 시 키·host 오류 | 환경변수와 `common/vector_search.py`의 import 시 초기화 |
| `no such table` | 실행 DB 경로와 마이그레이션 상태 |
| 검색 결과 없음 | 상품 CSV 적재 여부, 제품군 코드, 필터 조건 |
| 스타일 없음 | Tailwind 빌드 산출물과 정적 파일 경로 |
| 채팅 403 | 세션 쿠키와 CSRF 토큰 |
| 채팅 401 | 로그인 세션 만료 |
| 채팅 500 | 서버 예외, 외부 API 응답, Pinecone metadata 구조 |
| 매뉴얼 검색 없음 | `user_manual` namespace와 `product_code_header` 값 |

LLM 실패에 대한 자동 롤백이나 작업 재개 기능은 없습니다. 사용자 메시지를 저장한 뒤 그래프를 실행하므로, 실패한 요청은 사용자 메시지만 남길 수 있습니다. 재전송 전 대화 기록을 확인합니다.

## 보관과 복구

SQLite의 계정·대화 데이터와 `media/profiles/`의 업로드 파일은 별도입니다. 서버 쓰기를 멈춘 상태에서 일관된 DB 복사본과 미디어를 함께 보관하고, 상품 CSV 및 Pinecone 적재 원본도 버전을 맞춥니다. 복구는 별도 로컬 복사본에서 마이그레이션 상태·상품 수·대화·프로필을 확인한 후 진행합니다. 자동 백업 스크립트는 제공하지 않습니다.

공개 서버 실행 조건은 [배포 문서](../09-deployment/deployment.md), 재검증 범위는 [검증과 한계](../10-quality/verification-and-limitations.md)에 있습니다.
