# 디렉터리 구조

[문서 홈](../README.md) · [시스템 구조](system-architecture.md)

## 애플리케이션

| 경로 | 내용 | 수정 시 함께 볼 파일 |
|---|---|---|
| [config](../../config/) | Django 설정, 루트 URL, WSGI·ASGI 진입점 | `settings.py`, `urls.py` |
| [mainpage](../../mainpage/) | 메인 SSR | `templates/mainpage.html` |
| [accounts](../../accounts/) | 사용자·찜 모델, 인증·마이페이지 | `static/js/wishlist-toggle.js` |
| [products](../../products/) | 상품 모델, 필터·상세 뷰 | `common/utils.py`, 필터 JSON |
| [chats](../../chats/) | 대화방·메시지·상태 | `api/views.py`, `common/llm.py` |
| [api](../../api/) | 채팅·찜 JSON 엔드포인트 | `static/js/api-response.js` |
| [common](../../common/) | 공유 검색 함수·LangGraph·LLM·RAG | `llm.py`, `llm_agent.py`, `vector_search.py`, `utils.py` |

앱별 `migrations/`는 스키마 변경 기록입니다. `tests.py`는 현재 테스트 케이스가 작성되지 않은 기본 파일입니다.

## 화면과 정적 자산

```text
templates/
├── base_page.html
├── mainpage.html / searchpage.html / productpage.html
├── chatpage.html / loginpage.html / registerpage.html / mypage.html
└── components/
    ├── search/     # 카테고리·필터·카드·페이지네이션
    ├── product/    # 요약·사양·탭·찜 액션
    ├── chat/       # 사이드바·메시지 입력
    ├── account/    # 프로필·메뉴·관심 제품
    └── auth/       # 로그인·비밀번호 찾기 화면
```

[static/js](../../static/js/)에는 공통 API 응답 파서, 찜, 채팅, 검색, 로그인 모듈이 있습니다. [static/css](../../static/css/)는 검색 필터·모바일 보조 스타일, [static/data](../../static/data/)는 필터 옵션입니다. [theme/static_src](../../theme/static_src/)에서 Tailwind를 빌드합니다.

## 데이터와 실험

Django 앱 `products/`는 모델·뷰·마이그레이션을 유지합니다. 오프라인 데이터와 그 안의 수집·전처리 노트북은 `data/products/`, 별도 적재·평가 노트북은 `notebooks/`에 둡니다. `debug.py`는 기존 루트 위치를 유지합니다.

| 경로 | 용도 |
|---|---|
| [data/products/raw/data_crawling](../../data/products/raw/data_crawling/) | 제품군별 수집 노트북·원본 CSV·HTML |
| [data/products/preprocessing](../../data/products/preprocessing/) | 제품군별 정제 노트북 |
| [data/products/database](../../data/products/database/) | 상품·해상도 적재용 CSV |
| [notebooks/data/loaddata.ipynb](../../notebooks/data/loaddata.ipynb) | CSV를 SQLite에 적재 |
| [data/products/embedding](../../data/products/embedding/) | PDF 다운로드·텍스트 처리·임베딩·업로드 |
| [notebooks/evaluation/llm_frame.ipynb](../../notebooks/evaluation/llm_frame.ipynb) | LLM 노드 평가 |
| [debug.py](../../debug.py) | 그래프 직접 호출 실험 |

`db.sqlite3`는 실행·마이그레이션 후 생성하는 로컬 DB이며 저장소 배포본으로 가정하지 않습니다. `media/profiles/`는 프로필 업로드 경로입니다. 이 실행 데이터는 소스 코드와 별도로 관리합니다.

[데이터 흐름](data-flow.md) · [템플릿 상세](../03-frontend/templates-components.md)
