# 디렉터리 구조

[← Docs 홈](../README.md) · [시스템 아키텍처](system-architecture.md)

## 루트 트리

```
4th_project/
├── config/                 # settings, urls, wsgi, asgi
├── accounts/               # 회원·찜 (UserFavorite)
├── products/               # 상품 모델·검색 뷰·크롤링 데이터
│   └── data/raw/data_crawling/   # 카테고리별 CSV·노트북
├── chats/                  # 대화방·메시지
├── api/                    # send_chat, favorite REST
├── common/                 # LangGraph, 에이전트, 벡터 검색
├── mainpage/               # 메인 페이지
├── templates/              # 페이지·컴포넌트 HTML
├── static/                 # JS, CSS, 필터 JSON
├── theme/                  # Tailwind (django-tailwind)
├── docs/                   # 본 위키
├── manage.py
├── requirements.txt
├── debug.py                # LangGraph 단독 디버그
└── README.md
```

## 앱별 핵심 파일

| 경로 | 설명 |
|------|------|
| `config/settings.py` | 앱 등록, DB, Tailwind, `.env` |
| `config/urls.py` | 루트 URL include |
| `products/models.py` | 카테고리별 Product*, `search_model()` |
| `products/views.py` | `searchpage`, `productpage` |
| `common/llm.py` | LangGraph 정의·`add_chat()` |
| `common/llm_agent.py` | LLM 프롬프트·structured output |
| `common/vector_search.py` | Pinecone 매뉴얼 검색 |
| `common/utils.py` | `get_product`, `search_product`, `get_favorites` |
| `api/views.py` | `send_chat`, `favorite`, `check_favorite` |

## templates 구조

```
templates/
├── base_page.html
├── mainpage.html
├── searchpage.html
├── productpage.html
├── chatpage.html
├── loginpage.html
├── registerpage.html
├── mypage.html
└── components/
    ├── header.html
    ├── search/          # 필터·그리드·페이지네이션
    ├── product/         # 상세·찜·탭
    ├── chat/            # 사이드바·메인
    ├── account/         # 프로필·찜 목록
    └── auth/            # 로그인·비밀번호 UI
```

상세: [템플릿·컴포넌트](../03-frontend/templates-components.md)

## static 구조

| 경로 | 용도 |
|------|------|
| `static/js/api-response.js` | 공통 `fetch` JSON 파싱·에러 메시지 (`ApiResponse`) |
| `static/js/wishlist-toggle.js` | 찜 토글·in-flight·버튼 busy |
| `static/js/chatpage.js` | 채팅 전송·마크다운 렌더·URL sanitizer |
| `static/js/searchpage.js` | 검색 페이지 초기화 엔트리 |
| `static/js/search/filter.js` | 필터 UI·옵션 JSON 로드 |
| `static/js/search/pagination.js` | 페이지네이션 |
| `static/js/productpage.js` | 상세 탭·뒤로가기 |
| `static/js/loginpage.js` | 로그인 패널 전환 |
| `static/data/search_filter_options.json` | 카테고리별 필터 옵션 |
| `static/css/search_filter.css` | 검색 필터 스타일 |

상세: [클라이언트 JS 모듈](../03-frontend/client-javascript.md)

## 데이터·크롤링

```
products/data/raw/data_crawling/
├── TV/
├── refrigerator/    # REF
├── washing_machine/ # WMT
├── vacuum/          # VAC
├── (에어컨 ACT 관련 디렉터리)
├── selenium_auto_module.py
└── */ *_db.ipynb, *_all_products.csv
```

제품 코드 prefix: `TVT`, `ACT`, `REF`, `VAC`, `WMT` — [DB 스키마](../05-database/schema-and-erd.md)

## 관련 문서

- [데이터 파이프라인](data-pipeline.md)
- [Backend 앱](../04-backend/django-apps.md)
