# 검색과 필터

[기능 안내](README.md) · [상품 상세](product-detail.md)

## 입력과 페이지

GET `/products/`에서 제품군·조건·페이지 번호로 조회합니다. [products/views.py](../../products/views.py)는 `product_type` 또는 `page`가 없으면 누락된 값만 각각 `REF`, `1`로 채워 redirect합니다.

| 파라미터 | 예 |
|---|---|
| `product_type` | TVT·ACT·REF·VAC·WMT |
| `page` | 1부터 시작하는 페이지 번호 |
| `price__gte`, `price__lte` | 가격 하한·상한 |
| `total_cap__gte` | 냉장고 용량 하한 |
| `screen_size__gte` | TV 크기 하한 |
| `name__icontains` | 상품명 포함 조건 |

## 처리 흐름

반복 GET 값을 정규화 → `common.utils.search_product` → 제품군 모델의 `search` → 공통 `search_model` → 페이지당 12건 → `searchpage.html` 순서입니다. 알 수 없는 제품군은 빈 목록을 반환하고, 무효 필드·변환할 수 없는 값은 검색 함수가 건너뜁니다. 모든 잘못된 조건이 400으로 거부되는 것은 아닙니다.

## 화면 연결

[filter.js](../../static/js/search/filter.js)는 [search_filter_options.json](../../static/data/search_filter_options.json)을 `ApiResponse.fetchJson`으로 읽어 필터를 구성합니다. 옵션 로딩·실패 배너, 범위 값 보정, 중복 submit 가드, 모바일 viewport 높이 조정이 있습니다.

[pagination.js](../../static/js/search/pagination.js)는 페이지 링크를 만들고 [searchpage.js](../../static/js/searchpage.js)가 두 모듈을 초기화합니다. 결과 본문은 서버에서 다시 렌더링합니다.

## 상담 검색과의 관계

LG봇도 같은 ORM 검색을 사용하지만 입력은 구조화된 슬롯입니다. 웹의 `price__lte`와 모델의 `price_lte`가 공통 검색 함수에서 해석됩니다. 필터 UI를 변경할 때 모델 필드와 LLM 슬롯까지 자동 변경되지는 않습니다.

검증에는 복수 값·빈 값·잘못된 타입·0건·페이지 범위와 옵션 JSON 실패를 포함합니다. [스키마 검색 규칙](../05-database/schema-and-erd.md)을 참고합니다.
