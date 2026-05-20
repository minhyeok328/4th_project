# LG Home — 프로젝트 Docs 위키

> SKN26 4th Project · 파트별·기능별 기술 문서 허브  
> 저장소 루트 개요는 [README.md](../README.md)를 참고하세요.

---

## 문서 구성 (파트별 카테고리)

| 파트 | 담당 역할 | 문서 홈 |
|------|-----------|---------|
| **공통** | 전체 개요·아키텍처 | [00-overview](00-overview/project-overview.md) · [02-architecture](02-architecture/system-architecture.md) |
| **시작하기** | 환경·실행 | [01-getting-started](01-getting-started/development-environment.md) |
| **Frontend** | 박기은, 서민혁 | [03-frontend](03-frontend/README.md) |
| **Backend** | 유동현 | [04-backend](04-backend/README.md) |
| **Database** | 이레 | [05-database](05-database/schema-and-erd.md) |
| **API** | Backend 연동 | [06-api](06-api/rest-api.md) |
| **AI / Modeling** | 윤정연, 정영일 | [07-ai-modeling](07-ai-modeling/README.md) |
| **기능 단위** | 기능 흐름 | [08-features](08-features/README.md) |

---

## 기능별 문서 (주제 인덱스)

| 기능 | 설명 | 문서 |
|------|------|------|
| 메인 페이지 | 카테고리 탐색·LG봇 CTA | [main-page](08-features/main-page.md) |
| 필터 검색 | 카테고리·스펙·페이지네이션 | [search-and-filter](08-features/search-and-filter.md) |
| 상품 상세 | 스펙·찜·매뉴얼 링크 | [product-detail](08-features/product-detail.md) |
| LG봇 (LGneer) | LangGraph 채팅·히스토리 | [chat-lgneer](08-features/chat-lgneer.md) |
| 계정·찜 | 회원·마이페이지·개인화 | [accounts-and-favorites](08-features/accounts-and-favorites.md) |

---

## 빠른 링크

### 개발·운영
- [개발 환경 설정](01-getting-started/development-environment.md)
- [실행 및 일상 운영](01-getting-started/run-and-operations.md)

### 구조·데이터
- [디렉터리 구조](02-architecture/directory-structure.md)
- [시스템 아키텍처](02-architecture/system-architecture.md)
- [데이터 파이프라인](02-architecture/data-pipeline.md)
- [DB 스키마·ERD](05-database/schema-and-erd.md)

### 연동
- [REST API 명세](06-api/rest-api.md)
- [LangGraph 플로우](07-ai-modeling/langgraph-flow.md)
- [RAG · Pinecone](07-ai-modeling/rag-pinecone.md)

### 프론트
- [화면설계·체크리스트](03-frontend/frontend.md)
- [페이지·URL 매핑](03-frontend/pages-and-routes.md)
- [템플릿·컴포넌트](03-frontend/templates-components.md)

---

## 문서 트리

```
docs/
├── README.md                          ← 이 파일 (위키 허브)
├── 00-overview/
│   └── project-overview.md
├── 01-getting-started/
│   ├── development-environment.md
│   └── run-and-operations.md
├── 02-architecture/
│   ├── system-architecture.md
│   ├── directory-structure.md
│   └── data-pipeline.md
├── 03-frontend/
│   ├── README.md
│   ├── frontend.md
│   ├── pages-and-routes.md
│   └── templates-components.md
├── 04-backend/
│   ├── README.md
│   └── django-apps.md
├── 05-database/
│   └── schema-and-erd.md
├── 06-api/
│   └── rest-api.md
├── 07-ai-modeling/
│   ├── README.md
│   ├── langgraph-flow.md
│   └── rag-pinecone.md
└── 08-features/
    ├── README.md
    ├── main-page.md
    ├── search-and-filter.md
    ├── product-detail.md
    ├── chat-lgneer.md
    └── accounts-and-favorites.md
```

---

## 문서 작성·갱신 가이드

1. **기능 추가 시**: `08-features/`에 주제 문서를 추가하고, 이 README의 기능 인덱스와 파트 홈 README를 갱신합니다.
2. **API 변경 시**: [rest-api.md](06-api/rest-api.md)와 해당 기능 문서의「연동」절을 함께 수정합니다.
3. **교차 참조**: 상대 경로 링크 사용 (예: `../06-api/rest-api.md`).
4. **중복 최소화**: 상세 설치·평가·회고는 루트 [README.md](../README.md)에 두고, Docs는 **구현·운영 관점**에 집중합니다.
