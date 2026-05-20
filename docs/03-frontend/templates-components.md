# 템플릿 · 컴포넌트 구조

[← Frontend 홈](README.md) · [화면설계](frontend.md)

## 베이스 레이아웃

- `base_page.html` — 공통 `<head>`, Tailwind, `{% block content %}`, `{% block extra_js %}`
- 모든 페이지는 `{% extends "base_page.html" %}`

## 컴포넌트 트리

```
base_page.html
├── header.html                    # 전역 네비·로그인 상태
│
├── mainpage.html
│   └── category_card.html
│
├── searchpage.html
│   ├── search/category_tabs.html
│   ├── search/search_filter.html
│   │   └── filters/category_filters.html
│   ├── search/product_grid.html
│   │   └── product_card.html
│   └── search/pagination.html
│
├── productpage.html
│   ├── product/product_summary.html
│   ├── product/product_detail_specs.html
│   ├── product/product_tabs.html
│   └── product/product_actions.html
│
├── chatpage.html
│   ├── chat/chat_sidebar.html
│   └── chat/chat_main.html
│
├── mypage.html
│   ├── account/account_profile.html
│   ├── account/account_menu.html
│   └── account/recent_products.html
│
└── loginpage.html / registerpage.html
    └── auth/login_form.html, reset_password_form.html
```

## 정적 자산 매핑

| 페이지 | JS (로드 순서) |
|--------|----------------|
| `searchpage.html` | `search/filter.js` → `search/pagination.js` → `searchpage.js` |
| `productpage.html` | `api-response.js` → `wishlist-toggle.js` → `productpage.js` |
| `chatpage.html` | `api-response.js` → `chatpage.js` |
| `mypage.html` | `api-response.js` → `wishlist-toggle.js` |
| `loginpage.html` | `loginpage.js` |

`product_actions.html`·`recent_products.html`은 **인라인 fetch 없음** — `onclick`이 `wishlist-toggle.js` 전역 함수를 호출합니다.  
data 속성: [client-javascript.md](client-javascript.md)

## 필터 데이터

`static/data/search_filter_options.json` — 카테고리별 필터 필드·옵션 정의.  
`search/filter.js`의 `loadOptions()`가 DOM과 동기화합니다.

## 관련 문서

- [클라이언트 JS 모듈](client-javascript.md)
- [디렉터리 구조](../02-architecture/directory-structure.md)
- [검색 기능](../08-features/search-and-filter.md)
