# 배포 조건

[문서 홈](../README.md) · [실행과 운영](../01-getting-started/run-and-operations.md)

## 현재 구성

저장소는 Django 로컬 개발 구성을 제공합니다. [wsgi.py](../../config/wsgi.py)와 [asgi.py](../../config/asgi.py)는 진입점이며, Dockerfile·배포 파이프라인·운영 서버 실행 설정·공개 배포 주소는 제공하지 않습니다. 아래 항목은 배포 완료 기록이 아닌 준비 기준입니다.

## 공개 배포 전에 필요한 설정

| 항목 | 현재 상태와 필요한 작업 |
|---|---|
| Django 비밀키 | 개발용 값이 소스에 지정됨; 운영 비밀키를 별도 환경 설정으로 분리 |
| DEBUG·호스트 | `DEBUG=True`, `ALLOWED_HOSTS=[]`; 운영 모드와 실제 호스트 설정 필요 |
| 서버 | `runserver`는 로컬 개발용; WSGI·ASGI 서버와 프로세스 관리 선택 필요 |
| 정적 파일 | Tailwind 빌드 후 수집 경로 `STATIC_ROOT`와 서빙 구성 필요 |
| 미디어 | 프로필 업로드 저장소·접근 경로·백업 필요 |
| DB | SQLite 파일 영속성·동시 쓰기·백업 정책 결정; 다른 DB 설정은 미제공 |
| 외부 서비스 | OpenAI·Pinecone 비밀값 주입, 인덱스 준비, 비용·오류 모니터링 |
| HTTPS·쿠키 | TLS 종료 지점과 세션·CSRF 쿠키 정책 설정 필요 |

`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `STATIC_ROOT`는 현재 환경변수 인터페이스가 아니라 Django 설정 항목입니다. 같은 이름의 환경변수를 추가하는 것만으로 설정이 바뀌지 않습니다.

## 배포 작업 순서

1. 운영 설정과 서버·DB·정적·미디어 저장소 구성을 결정합니다.
2. Python 의존성을 설치하고 `theme/static_src`에서 Tailwind를 빌드합니다.
3. 비밀값·외부 인덱스를 연결한 뒤 DB를 백업하고 마이그레이션합니다.
4. 정적 파일 수집 경로를 구성한 뒤 `python manage.py collectstatic`을 실행합니다.
5. 선택한 운영 설정으로 `python manage.py check --deploy` 결과를 검토합니다.
6. 새 환경에서 로그인·찜·채팅·이미지 업로드·재시작 후 데이터 보존을 확인합니다.

기본 설정은 `STATIC_ROOT`가 없어 정적 수집을 완성된 배포 명령처럼 바로 사용할 수 없습니다. 개발용 미디어 URL 연결도 운영 파일 서버를 대체하지 않습니다.

## 복구와 검증

상품 재적재 노트북은 행 삭제를 포함하므로 운영 DB에 바로 실행하지 않습니다. 복구 시 SQLite 또는 운영 DB, 업로드 파일, 상품 CSV 버전, Pinecone metadata 연결을 함께 확인합니다. 자동 롤백·백업 복구 검증은 현재 제공되지 않습니다.

[검증과 한계](../10-quality/verification-and-limitations.md)에 정리된 런타임 확인을 배포 환경에서도 수행해야 합니다.
