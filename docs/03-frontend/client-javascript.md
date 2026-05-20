# 클라이언트 JavaScript 모듈

[← Frontend 홈](README.md) · [화면설계](frontend.md) · [1차 테스트 평가서](frontend-test-report.md) · [2차 QA 평가서](frontend-final-report.md)

## 개요

Django 템플릿(SSR) 위에서 페이지별·공통 바닐라 JS 모듈로 상호작용을 처리합니다.

| 단계 | 내용 | 문서 |
|------|------|------|
| 1차 (#93) | 챗봇 마크다운 보안, 찜 in-flight, `ApiResponse` 파싱·알림 | [frontend-test-report.md §0](frontend-test-report.md#0-1차-수정-반영-요약-재평가-전제) |
| 2차 (#100) | `fetchJson` 통합, 검색 필터 로딩/에러 UI, 마이페이지 찜 카운트, 로그인 검증, 모바일 보완 | [frontend-final-report.md](frontend-final-report.md) |

## 모듈 구조

```
static/js/
├── api-response.js          # 공통 fetch JSON·에러 메시지·fetchJson
├── wishlist-toggle.js       # 찜 토글 (상품 상세·마이페이지)
├── chatpage.js              # LG봇 UI·전송·마크다운 렌더·모바일 사이드바
├── searchpage.js            # 검색 페이지 초기화 엔트리
├── search/
│   ├── filter.js            # 필터 UI·옵션 JSON·submit 가드·모바일 viewport
│   └── pagination.js        # 페이지네이션 컨트롤
├── productpage.js           # 상품 탭·뒤로가기
└── loginpage.js             # 로그인 패널 전환·클라이언트 검증

static/css/
├── search_filter.css
└── mobile-viewport.css      # 모바일 터치·입력 zoom 방지·safe-area
```

## 공통: `api-response.js`

전역 `window.ApiResponse`를 노출합니다.

| API | 역할 |
|-----|------|
| `parseFetchJsonResponse(response, { loginUrl })` | 리다이렉트·`content-type`·JSON 파싱 실패 통합 처리 |
| `fetchJson(url, init, options)` | `fetch` + 파싱 + 네트워크 실패를 동일 `result` 형태로 반환 |
| `buildFormPostInit({ body, csrfToken })` | FormData POST용 `credentials`·CSRF 헤더 |
| `buildJsonPostInit({ body, csrfToken })` | JSON POST용 헤더·`X-Requested-With` |
| `notifyJsonFetchError(result, options)` | HTTP·파싱·네트워크 실패 문구 공통 매핑 (옵션으로 alert 생략) |
| `notifyApiError(code, options)` | 기본 `alert` (코드 → `MESSAGES` 매핑) |
| `getErrorMessage(errorCode, fallback)` | 인라인 표시용 문구 (챗봇 말풍선 등) |
| `logApiError(context, error)` | `console.error` 형식 통일 |
| `MESSAGES` / `ERROR_CODES` | NETWORK, SERVER, PARSE, WISHLIST, CHAT_EMPTY 등 |

**사용 페이지:** `chatpage.html`, `productpage.html`, `mypage.html`, `searchpage.html` — 의존 모듈보다 **먼저** 로드합니다.

## 찜: `wishlist-toggle.js`

템플릿 인라인 `fetch` 로직을 모듈로 이전했습니다.

| 전역 함수 | 호출 위치 |
|-----------|-----------|
| `productPageWishlistToggle(button, productCode)` | `product_actions.html` `onclick` |
| `mypageWishlistToggle(button, productCode)` | `recent_products.html` `onclick` |

### 동작 요약

- `wishlistInFlight`(`Set`)으로 동일 `product_code` 동시 POST 차단
- `ApiResponse.fetchJson` + `buildFormPostInit` (네트워크 실패 시 `WISHLIST` alert)
- `POST /accounts/mypage/` — `action=toggle_favorite`
- 마이페이지: 카드 제거 후 `syncMypageWishlistCount()` — `data-wishlist-count-badge` 갱신
- 상품 상세: `loginUrl`로 세션 만료 시 로그인 이동

### 템플릿 data 속성

| 요소 | 속성 |
|------|------|
| `#product-actions` | `data-wishlist-post-url`, `data-csrf-token`, `data-login-url`, `data-is-authenticated` |
| `#mypage-wishlist-section` | `data-wishlist-post-url`, `data-csrf-token` |
| `[data-wishlist-count-badge]` | 마이페이지 찜 개수 뱃지 (2차) |

## 챗봇: `chatpage.js`

| 기능 | 구현 |
|------|------|
| 중복 초기화 방지 | `window.__lgChatPageInitialized` |
| 전송 중 잠금 | `inFlight`, `setBusy` (입력·전송 버튼) |
| API | `POST /api/send_chat/` + `ApiResponse.fetchJson` + `buildJsonPostInit` |
| 마크다운 | `renderMarkdown` → `escapeHtml` → 링크/이미지 치환 |
| URL 보안 | `isSafeHttpUrl` — `http`/`https`만 허용 |
| HTML sanitizer | `sanitizeChatHtml` — 허용 태그·속성 화이트리스트 |
| 모바일 사이드바 | `data-chat-sidebar-backdrop`, `aria-*`, ESC 닫기, `overflow-hidden`, 입력 focus scroll |
| 인라인 이미지 | `isImageUrl` + `buildChatImageHtml` (확장자·`lge.co.kr/kr/images/`) |

에러 시 assistant 말풍선에 `getErrorMessage` 문구 표시. **잔여:** `send_chat` 401 시 `loginUrl` 미전달 — [QA 평가서 §5](frontend-final-report.md#5-우선순위별-개선-권장-사항).

## 검색: `searchpage.js` + `search/*`

- `searchpage.js`: `LGSearchPage.initSearchFilter`, `initPagination` 호출만 담당
- `filter.js`:
  - `loadOptions()` — `ApiResponse.fetchJson` + `data-filter-options-loading` / `data-filter-options-error` 배너
  - `filterSubmitInFlight` + `data-search-filter-submit` busy
  - submit 직전 `clampRangeInput`, 빈 파라미터 `name` 제거
  - 모바일: `visualViewport` 기반 `maxHeight` 조정
- `pagination.js`: `data-pagination` 기반 페이지 링크 생성

검색 결과 본문은 **SSR**; 클라이언트 `fetch`는 필터 옵션 JSON 로드에 한정됩니다.

## 로그인: `loginpage.js`

- `data-auth-mode` 패널 전환 (기존)
- 2차: `username` trim·길이(150)·`^[\w.@+-]+$`, 비밀번호 필수 — `setCustomValidity` + `reportValidity`

회원가입·비밀번호 찾기는 HTML5 위주 — [QA 평가서](frontend-final-report.md).

## 스크립트·스타일 로드 매핑

| 페이지 | 순서 |
|--------|------|
| `chatpage.html` | `mobile-viewport.css` → `api-response.js` → `chatpage.js` |
| `productpage.html` | `api-response.js` → `wishlist-toggle.js` → `productpage.js` |
| `mypage.html` | `api-response.js` → `wishlist-toggle.js` |
| `searchpage.html` | `search_filter.css`, `mobile-viewport.css` → `api-response.js` → `filter.js` → `pagination.js` → `searchpage.js` |
| `loginpage.html` | `loginpage.js` |

## 관련 문서

- [기능: LG봇](../08-features/chat-lgneer.md)
- [기능: 검색·필터](../08-features/search-and-filter.md)
- [기능: 계정·찜](../08-features/accounts-and-favorites.md)
- [기능: 상품 상세](../08-features/product-detail.md)
- [REST API](../06-api/rest-api.md)
- [1차 테스트 평가서](frontend-test-report.md)
- [2차 QA 평가서](frontend-final-report.md)
