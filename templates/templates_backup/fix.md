# main-page 1차 수정 요약

## 카테고리
- **문제:** `mainpage.html`은 `categories`를 도는데 뷰에서 안 넘겨서 버튼이 안 보임. `?category=`는 `searchpage`가 안 씀.
- **조치:** `mainpage/views.py`에 5개 카테고리(`label` + `product_type`) 상수 후 컨텍스트로 전달. 카드 링크는 `searchpage?product_type=…&page=1`.

## 로그아웃
- **문제:** 헤더가 `accounts:logout`을 쓰는데 URL에 `logout` 라우트가 없어 `NoReverseMatch`.
- **조치:** `accounts/urls.py`에 `logout/` 추가, `logout_view`에서 POST 시 `logout()` 후 메인으로 리다이렉트.