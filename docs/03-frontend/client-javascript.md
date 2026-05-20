# 클라이언트 JavaScript 모듈

[← Frontend 홈](README.md) · [화면설계](frontend.md) · [1차 수정 후 테스트 평가서](frontend-test-report.md)

## 개요

Django 템플릿(SSR) 위에서 페이지별·공통 바닐라 JS 모듈로 상호작용을 처리합니다.  
2026년 1차 프론트 개선(#93)에서 **챗봇 마크다운 보안**, **찜 중복 요청 방지**, **API 실패 UX 공통화**가 반영되었습니다.

## 모듈 구조

```
static/js/
├── api-response.js          # 공통 fetch JSON·에러 메시지
├── wishlist-toggle.js       # 찜 토글 (상품 상세·마이페이지)
├── chatpage.js              # LG봇 UI·전송·마크다운 렌더
├── searchpage.js            # 검색 페이지 초기화 엔트리
├── search/
│   ├── filter.js            # 필터 UI·URL 파라미터·옵션 JSON 로드
│   └── pagination.js        # 페이지네이션 컨트롤
├── productpage.js           # 상품 탭·뒤로가기
└── loginpage.js             # 로그인/회원가입 패널 전환
```

## 공통: `api-response.js`

전역 `window.ApiResponse`를 노출합니다.

| API | 역할 |
|-----|------|
| `parseFetchJsonResponse(response, { loginUrl })` | 리다이렉트·`content-type`·JSON 파싱 실패 통합 처리 |
| `notifyApiError(code, options)` | 기본 `alert` (코드 → `MESSAGES` 매핑) |
| `getErrorMessage(errorCode, fallback)` | 인라인 표시용 문구 (챗봇 말풍선 등) |
| `logApiError(context, error)` | `console.error` 형식 통일 |
| `MESSAGES` | NETWORK, SERVER, PARSE, WISHLIST, CHAT_EMPTY 등 |

**사용 페이지:** `chatpage.html`, `productpage.html`, `mypage.html` — 반드시 **의존 모듈보다 먼저** 로드합니다.

**미적용:** `search/filter.js`의 `loadOptions()` (정적 JSON, 실패 시 무음 degrade) — 2차 개선 후보.

## 찜: `wishlist-toggle.js`

템플릿 인라인 `fetch` 로직을 모듈로 이전했습니다.

| 전역 함수 | 호출 위치 |
|-----------|-----------|
| `productPageWishlistToggle(button, productCode)` | `product_actions.html` `onclick` |
| `mypageWishlistToggle(button, productCode)` | `recent_products.html` `onclick` |

### 동작 요약

- `wishlistInFlight`(`Set`)으로 동일 `product_code` 동시 POST 차단
- 요청 중 `disabled`, `opacity-60`, `aria-busy`
- `POST /accounts/mypage/` — `action=toggle_favorite`
- `ApiResponse.parseFetchJsonResponse` (상품 상세: `loginUrl`로 세션 만료 시 로그인 이동)
- 실패 시 `alert` (WISHLIST / SERVER_SHORT / PARSE)

### 템플릿 data 속성

| 요소 | 속성 |
|------|------|
| `#product-actions` | `data-wishlist-post-url`, `data-csrf-token`, `data-login-url`, `data-is-authenticated` |
| `#mypage-wishlist-section` | `data-wishlist-post-url`, `data-csrf-token` |

## 챗봇: `chatpage.js`

| 기능 | 구현 |
|------|------|
| 중복 초기화 방지 | `window.__lgChatPageInitialized` |
| 전송 중 잠금 | `inFlight`, `setBusy` (입력·전송 버튼) |
| API | `POST /api/send_chat/` + `ApiResponse.parseFetchJsonResponse` |
| 마크다운 | `renderMarkdown` → `escapeHtml` → 링크/이미지 치환 |
| URL 보안 | `isSafeHttpUrl` — `http`/`https`만 허용 |
| HTML sanitizer | `sanitizeChatHtml` — 허용 태그·속성 화이트리스트 |
| 인라인 이미지 | `isImageUrl` + `buildChatImageHtml` (확장자·`lge.co.kr/kr/images/`) |

에러 시 assistant 말풍선에 `ApiResponse.MESSAGES` 문구 표시 (네트워크·서버·파싱).

## 검색: `searchpage.js` + `search/*`

- `searchpage.js`: `LGSearchPage.initSearchFilter`, `initPagination` 호출만 담당
- `filter.js`: 필터 칩·범위 clamp·폼 submit 시 빈 파라미터 제거
- `pagination.js`: `data-pagination` 기반 페이지 링크 생성

검색 결과 본문은 **SSR**; 클라이언트 `fetch`는 필터 옵션 JSON 로드에 한정됩니다.

## 스크립트 로드 매핑

| 페이지 | `extra_js` / 인라인 순서 |
|--------|-------------------------|
| `chatpage.html` | `api-response.js` → `chatpage.js` |
| `productpage.html` | `api-response.js` → `wishlist-toggle.js` → `productpage.js` |
| `mypage.html` | `api-response.js` → `wishlist-toggle.js` |
| `searchpage.html` | `filter.js` → `pagination.js` → `searchpage.js` |
| `loginpage.html` | `loginpage.js` |

## 관련 문서

- [기능: LG봇](../08-features/chat-lgneer.md)
- [기능: 계정·찜](../08-features/accounts-and-favorites.md)
- [기능: 상품 상세](../08-features/product-detail.md)
- [REST API](../06-api/rest-api.md)
- [1차 수정 후 테스트 평가서](frontend-test-report.md)
