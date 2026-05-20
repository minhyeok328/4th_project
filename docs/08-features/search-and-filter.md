# 필터 검색

[← 기능 인덱스](README.md) · [DB 스키마](../05-database/schema-and-erd.md)

## 개요

카테고리 탭과 스펙·가격 필터로 상품 목록을 조회합니다. 페이지당 **12건** 페이지네이션.

## URL · 파라미터

| 항목 | 값 |
|------|-----|
| URL | `/products/` |
| View | `products.views.searchpage` |
| Template | `searchpage.html` |
| JS | `search/filter.js`, `search/pagination.js`, `searchpage.js` |
| 필터 데이터 | `static/data/search_filter_options.json` |

### 필수 쿼리

`product_type`, `page`가 없으면 `?product_type=REF&page=1`로 리다이렉트.

### 카테고리 코드

| product_type | 모델 |
|--------------|------|
| TVT | ProductTV |
| REF | ProductFridge |
| WMT | ProductWash |
| ACT | ProductAC |
| VAC | ProductVAC |

### 필터 키 예시

| 파라미터 | 의미 |
|----------|------|
| `price__gte`, `price__lte` | 가격 범위 |
| `total_cap__gte` | 냉장고 용량 (REF) |
| `screen_size__gte` | TV 인치 (TVT) |
| `name__icontains` | 이름 포함 |

## 처리 흐름

```mermaid
flowchart TD
    GET[GET /products/] --> Check{product_type & page?}
    Check -->|No| Redirect[기본값 리다이렉트]
    Check -->|Yes| Parse[GET → conditions dict]
    Parse --> Search[search_product type, [], conditions]
    Search --> Page[Paginator 12건]
    Page --> Render[searchpage.html]
```

`search_product` → `common.utils` → `Model.search()` (`products/models.py`)

## UI 컴포넌트

- `category_tabs.html` — 카테고리 전환
- `search_filter.html` + `filters/category_filters.html` — 동적 필터
- `product_grid.html` / `product_card.html`
- `pagination.html`

## 챗봇과의 차이

| | 필터 검색 | LG봇 |
|--|-----------|------|
| 입력 | 폼·쿼리스트링 | 자연어 |
| 조건 | 사용자가 직접 선택 | LLM 슬롯 추출 |
| 엔진 | 동일 `search_model()` | LangGraph + 동일 ORM |

## 클라이언트 (2차 개선)

- **옵션 로드:** `filter.js` — `ApiResponse.fetchJson`, 로딩/에러 배너 (`search_filter.html`)
- **submit:** `filterSubmitInFlight`, range `clamp`, 모바일 `visualViewport` 높이 조정
- **스타일:** `search_filter.css`, `mobile-viewport.css` — `searchpage.html`에서 로드

→ [client-javascript.md](../03-frontend/client-javascript.md) · [2차 QA 평가서](../03-frontend/frontend-final-report.md)

## 관련 문서

- [상품 상세](product-detail.md)
- [클라이언트 JS](../03-frontend/client-javascript.md)
- [템플릿 구조](../03-frontend/templates-components.md)
- [데이터 파이프라인](../02-architecture/data-pipeline.md)
