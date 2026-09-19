# 메인 페이지

[기능 안내](README.md)

## 진입점

GET `/`에서 [mainpage/views.py](../../mainpage/views.py)가 [mainpage.html](../../templates/mainpage.html)을 렌더링합니다. 카테고리 탐색과 LG봇 진입을 연결하는 화면입니다.

## 구성과 이동

- 공통 [header.html](../../templates/components/header.html)에서 검색·채팅·계정 화면으로 이동합니다.
- [category_card.html](../../templates/components/category_card.html)로 5개 제품군 진입점을 표시합니다.
- 카테고리 링크는 `/products/`에 `product_type`을 전달합니다. 누락된 페이지 값은 검색 뷰가 보완합니다.
- LG봇은 `/chats/`로 연결되며 비로그인은 서버 가드에 따라 로그인 화면으로 이동합니다.

메인 캐러셀 등 일부 상호작용은 템플릿 인라인 스크립트에 있습니다. 공통 헤더나 카드 수정 시 키보드 접근·모바일 레이아웃·정적 이미지 경로를 함께 확인합니다.

[검색](search-and-filter.md) · [채팅](chat-lgneer.md) · [페이지 매핑](../03-frontend/pages-and-routes.md)
