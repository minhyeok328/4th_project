# LG Home

LG 가전의 조건 검색과 사용설명서 기반 AI 상담을 연결한 Django 웹 프로젝트입니다.

## 프로젝트 소개

LG Home은 TV, 냉장고, 세탁기, 에어컨, 청소기를 탐색하고 제품 정보를 확인하는 서비스입니다. 사용자는 가격과 사양을 직접 선택하거나 LG봇(LGneer)에게 자연어로 조건을 설명할 수 있습니다.

상품 검색에는 카테고리별 데이터베이스를 사용하고, 사용 방법에 관한 질문에는 사용설명서 검색 결과를 답변 근거로 전달합니다. 검색부터 상세 정보 확인, 관심 제품 저장, 후속 상담으로 이어지는 흐름을 구현했습니다.

## 주요 기능

| 기능 | 설명 |
|---|---|
| 카테고리 탐색 | 다섯 가지 가전 제품군으로 검색 진입 |
| 조건 검색 | 가격·용량·화면 크기 등 제품군별 필터와 페이지네이션 |
| 상품 상세 | 제품 이미지, 가격, 사양, 사용설명서 링크 확인 |
| AI 상담 | 자연어 조건 추출, 상품 추천, 후속 질문 처리 |
| 매뉴얼 검색 | Pinecone에서 사용설명서 페이지를 찾아 답변에 활용 |
| 계정과 관심 제품 | 회원가입·로그인, 프로필 수정, 찜 목록 저장 |
| 대화 관리 | 사용자별 대화방, 메시지 기록, 대화방 삭제 |

구매·결제와 비밀번호 재설정은 서버 기능으로 연결되어 있지 않으며, 상품 리뷰와 Q&A에는 화면 예시가 포함되어 있습니다.

## 사용 흐름

1. 메인 화면에서 원하는 가전 카테고리를 선택합니다.
2. 가격과 사양을 설정하고 검색 결과에서 상품 상세로 이동합니다.
3. 로그인 후 관심 제품을 찜 목록에 저장합니다.
4. LG봇에서 “500L 이상 냉장고를 추천해 줘”처럼 조건을 입력합니다.
5. 추천 결과를 좁히거나 사용설명서에 관한 후속 질문을 이어갑니다.

상품 검색·상세는 로그인 없이 볼 수 있습니다. 찜 목록과 채팅은 로그인한 사용자의 계정에 연결됩니다.

## 기술 구성

| 구분 | 기술 |
|---|---|
| 웹 서버 | Python, Django, Django ORM |
| 화면 | Django Templates, Tailwind CSS, DaisyUI, JavaScript |
| 관계형 데이터 | SQLite |
| AI 흐름 | LangGraph, LangChain, OpenAI |
| 매뉴얼 검색 | OpenAI 임베딩, Pinecone |
| 데이터 준비 | Selenium, BeautifulSoup, pandas, PyMuPDF, Jupyter 노트북 |

## 프로젝트 구조

```text
4th_project/
├── config/          # Django 설정과 URL
├── accounts/        # 계정과 찜
├── products/        # 상품 모델·검색
├── chats/           # 대화방과 메시지
├── api/             # 채팅·찜 JSON API
├── common/          # 상품 조회·LangGraph·매뉴얼 검색
├── data/products/   # 수집·전처리·상품 CSV·매뉴얼 준비
├── notebooks/       # DB 적재·모델 평가
├── templates/       # 페이지와 공통 컴포넌트
├── static/          # JavaScript·CSS·필터 옵션
├── theme/           # Tailwind 빌드
└── docs/            # 개발 문서
```

## 문서 안내

개발 환경 준비부터 실행, 구조, API와 검증 범위까지 [개발 문서](docs/README.md)에서 확인할 수 있습니다.

| 문서 | 내용 |
|---|---|
| [개발 환경](docs/01-getting-started/development-environment.md) | 의존성, 환경변수, 데이터 준비 |
| [실행과 운영](docs/01-getting-started/run-and-operations.md) | 로컬 서버와 오류 확인 |
| [시스템 구조](docs/02-architecture/system-architecture.md) | 웹·데이터·AI 연결 |
| [API 명세](docs/06-api/api-reference.md) | 세션 인증과 요청·응답 |
| [검증과 한계](docs/10-quality/verification-and-limitations.md) | 검증 방법과 기록의 범위 |

## 원본 저장소

[SKN26-4th-1st/4th_project](https://github.com/SKN26-4th-1st/4th_project)
