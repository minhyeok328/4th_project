# main-page 1차 수정 요약

## 카테고리
- **문제:** `mainpage.html`은 `categories`를 도는데 뷰에서 안 넘겨서 버튼이 안 보임. `?category=`는 `searchpage`가 안 씀.
- **조치:** `mainpage/views.py`에 5개 카테고리(`label` + `product_type`) 상수 후 컨텍스트로 전달. 카드 링크는 `searchpage?product_type=…&page=1`.

## 로그아웃
- **문제:** 헤더가 `accounts:logout`을 쓰는데 URL에 `logout` 라우트가 없어 `NoReverseMatch`.
- **조치:** `accounts/urls.py`에 `logout/` 추가, `logout_view`에서 POST 시 `logout()` 후 메인으로 리다이렉트.

# search-page 1차 수정 요약

## 검색 결과 이미지
- **문제:** `product_card.html`이 mock 데이터 필드 `image_url`을 참조. DB 모델은 `img_link`만 있어 검색 카드에 이미지가 안 보임. 상세(`product_summary.html`)는 `img_link` 사용으로 정상.
- **조치:** `product_card.html`에서 `product.img_link`로 변경.

## 카테고리 라벨 (검색 카드)
- **문제:** `product.category` 필드는 모델에 없음. `{% include %}`를 두 줄로 나누거나 `with category=product.category`를 쓰면 태그가 그대로 노출되거나 라벨이 비어 보임. `uppercase` 클래스로 경로 문자열이 대문자로 보이기도 함.
- **조치:** `category_label_fragment.html`을 한 줄 `{% include %}`로 포함. `request.GET.product_type` 기준으로 TV·냉장고 등 표시. 카테고리 줄 `uppercase` 제거.

## 페이지네이션
- **문제:** `products/views.py`의 `Paginator`(12개/페이지)와 URL `page=`는 있으나 UI 없음.
- **조치:** `templates/components/common/pagination.html` + `static/js/pagination.js`. `page_obj`의 `data-*`만 템플릿에 두고, 링크·페이지 번호·`…`는 JS가 현재 URL 쿼리(`product_type`, 필터 등)를 유지한 채 `page`만 변경. `searchpage.html`에서 `product_grid` 아래 include. (뷰 헬퍼 `pagination_query` / `pagination_items`는 사용하지 않음.)

## 가격 표시 (품절)
- **문제:** `price`가 `null`이면 `{{ product.price|floatformat:0 }}원`이 `원`만 표시됨.
- **조치:** `product_card.html`에서 `{% if product.price %}` 분기 — 있으면 가격, 없으면 **품절**(회색).

## 가격 천 단위 콤마
- **문제:** `floatformat:0`만 사용해 `16500000원`처럼 콤마 없이 표시됨.
- **조치:** `config/settings.py`에 `django.contrib.humanize` 추가. 검색·상세·스펙 탭 템플릿에 `{% load humanize %}` 후 `{{ …|floatformat:0|intcomma }}원` 적용 (`product_card.html`, `product_summary.html`, `product_tabs.html`).

## 검색 필터 UI
- **문제:** `search_filter.html`이 체크박스·정렬 UI만 있고 `name`/`price__gte` 등 실제 쿼리와 연결되지 않음. 카테고리별 스펙 필드도 없음.
- **조치:** `products/models.py`의 `search_model`·`LOOKUPS`(`gte`, `lte`, `icontains`, `exact` 등)에 맞춰 GET 폼 구성.
  - `templates/components/search/search_filter.html` — `product_type`·`page=1` hidden, 필터 적용·초기화
  - `templates/components/search/filters/common.html` — 상품명, 가격(최소/최대), 가격대 프리셋, 추천 난이도, 소비전력
  - `filters/ref.html`, `tvt.html`, `act.html`, `vac.html`, `wmt.html` — 카테고리별 스펙 필드
  - `filters/_field_text.html`, `_field_range.html` — 입력 partial
  - `static/js/search_filter.js` — URL 쿼리로 입력값 복원, 가격 프리셋 연동, 빈 값·`price_preset`은 submit 시 제외
  - `products/views.py` `searchpage`는 `product_type`·`page` 제외한 `request.GET`를 `search_product()`에 그대로 전달 (기존 로직 유지).

## 필터 미적용 (전체 상품만 조회)
- **문제:** 필터 적용 후에도 조건과 무관하게 전체 상품이 나옴. `price__gte`·`price__lte` 등 range 조건이 동작하지 않음.
- **원인:** `products/models.py` `_split_condition_key`가 lookup 접미사를 `_{lookup}`(단일 `_`)로 파싱. `price__gte`가 필드명 `price_`로 잘못 분리되어 조건이 전부 무시됨.
- **조치:** 접미사를 Django ORM과 동일하게 `__{lookup}`으로 수정. 긴 lookup(`icontains` 등) 우선 매칭(`sorted(..., reverse=True)`).

## 검색 리다이렉트 시 필터 유실
- **문제:** `product_type` 또는 `page`가 없을 때 `searchpage`가 `product_type`·`page`만 담긴 URL로 redirect → `price__gte`, `name` 등 필터 쿼리가 사라짐.
- **조치:** `products/views.py`에서 `request.GET.copy()` 후 `product_type`·`page`만 보완해 `query.urlencode()`로 redirect (기존 필터 파라미터 유지).

---