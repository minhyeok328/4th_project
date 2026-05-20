# 프론트엔드 QA 평가서 (2차 수정 후)

> **본 문서는 2차 수정 완료 후 QA 재평가입니다.**  
> 개선 근거·우선순위는 [1차 수정 후 테스트 평가서](frontend-test-report.md) §5를 기준으로 코드를 반영한 뒤, 동일 검수 기준으로 재점검한 결과입니다.  
> 1차(챗봇 URL 보안·찜 in-flight·`ApiResponse` 도입) 이후 2차에서 반영된 검색 필터 API UX·`fetchJson` 통합·마이페이지 찜 카운트·로그인 검증·검색 submit 가드·필터 로딩/에러 UI·모바일 터치·키보드 보완을 **정적 코드 분석** 기준으로 확인했습니다.  
> **런타임 실기기 테스트는 수행하지 않았습니다.** 해당 항목은 “확인 필요”로 표기합니다.

---

## 1. 검수 개요

- **검수 대상:** Workspace 프론트엔드 전체 — `templates/`, `static/js/`, `static/css/`, 페이지별 스크립트 로드
- **검수 목적:** 2차 수정 반영 후 주요 플로우의 장애 가능성·API/UX 일관성·잔여 리스크 식별
- **코드 수정 여부:** 수정하지 않음 (읽기·분석만)
- **주요 확인 기능:**
  - 검색/필터/페이지네이션 (`filter.js`, `pagination.js`, `searchpage.js`)
  - 챗봇 송수신·마크다운 렌더 (`chatpage.js`, `api-response.js`)
  - 찜 토글 (`wishlist-toggle.js`)
  - 로그인·패널 전환 (`loginpage.js`, `login_form.html`)
  - 모바일 보조 (`mobile-viewport.css`, `chatpage.html` 사이드바)
- **우선 검토 기준:** 사용자 영향도·비동기/API 복잡도·보안(HTML 경로)·2차에서 미완료로 남은 구조적 과제

---

## 2. 주요 로직 분석

### 2.1 우선 검토 대상 선정 이유

| 우선순위 | 검토 대상 | 선정 이유 | 사용자 영향도 |
|---|---|---|---|
| 1 | 챗봇 메시지 렌더링/전송 | `innerHTML`·마크다운·`fetchJson` POST·`inFlight` 집중; 보안·세션·장문 성능 리스크 | High |
| 2 | 검색 필터 (`filter.js`) | 700줄+ 단일 모듈, 옵션 JSON·칩 UI·submit·모바일 viewport; 2차 개선 다수 반영 | High |
| 3 | 찜 토글 + `ApiResponse` | POST·세션 리다이렉트·in-flight; 2차 `fetchJson`·마이페이지 카운트 동기화 | High |
| 4 | 인증(로그인/회원가입) | 로그인만 2차 클라이언트 검증; 회원가입·비밀번호 찾기는 미흡 | Medium |
| 5 | 인라인 스크립트·전역 `onclick` | `mainpage`, `account_profile`, `product_actions` 등 공통 레이어 밖 | Low |

### 2.2 관련 파일 및 함수

| 구분 | 파일 경로 | 함수/컴포넌트명 | 역할 |
|---|---|---|---|
| API 연동 | `static/js/api-response.js` | `fetchJson`, `parseFetchJsonResponse`, `notifyApiError` | 공통 fetch·JSON·에러 코드 |
| API 연동 | `static/js/chatpage.js` | `sendMessage`, `renderMarkdown`, `sanitizeChatHtml` | 챗봇 POST·마크다운·sanitizer |
| API 연동 | `static/js/wishlist-toggle.js` | `postToggleFavorite`, `syncMypageWishlistCount` | 찜 POST·마이페이지 DOM |
| API 연동 | `static/js/search/filter.js` | `loadOptions`, `renderChipGroups`, submit handler | 옵션 JSON·필터 UI |
| 상태 관리 | `static/js/chatpage.js` | `messages`, `inFlight`, `setBusy` | 대화·전송 잠금 |
| 상태 관리 | `static/js/wishlist-toggle.js` | `wishlistInFlight` | 상품별 동시 POST 차단 |
| 상태 관리 | `static/js/search/filter.js` | `filterSubmitInFlight`, `optionsByType` | submit·옵션 캐시 |
| 이벤트 처리 | `static/js/search/filter.js` | `initSearchFilter`, chip `click` | 필터·칩 토글 |
| 이벤트 처리 | `static/js/search/pagination.js` | `initPagination` | 페이지 링크 SSR 보조 |
| UI 렌더링 | `templates/components/search/search_filter.html` | 로딩/에러 배너 | 필터 옵션 피드백 |
| UI 렌더링 | `templates/chatpage.html` | `#chat-sidebar-overlay` | 모바일 사이드바 |
| 유틸/보안 | `static/js/chatpage.js` | `isSafeHttpUrl`, `escapeHtml` | URL·텍스트 이스케이프 |

### 2.3 현재 동작 흐름

1. **검색:** `searchpage.js` → `initSearchFilter` / `initPagination` → URL 파라미터 복원 → `loadOptions()` (`fetchJson` + 로딩/에러 배너) → 칩 렌더 → submit 시 `clampRangeInput`·빈 `name` 제거·`filterSubmitInFlight` 가드 → 전체 GET 네비게이션.
2. **챗봇:** `__lgChatPageInitialized` 가드 → 서버 히스토리 `textContent` hydrate → `sendMessage` → `fetchJson` + placeholder/`setBusy` → assistant `renderMarkdown` → `sanitizeChatHtml` → `innerHTML` 렌더.
3. **찜:** `ApiResponse.fetchJson` + `buildFormPostInit` → 성공 시 상세 UI 토글 또는 마이페이지 카드 제거 + `syncMypageWishlistCount()` → 빈 그리드 시 `reload`.

### 2.4 발견된 문제점

#### 2.4.1 1차 재평가 대비 2차에서 완화된 항목

| 이전 이슈 | 2차 반영 | 재평가 |
|---|---|---|
| 필터 옵션 fetch 무음 실패 | `fetchJson` + 인라인 에러 배너 | **완화** |
| `ApiResponse` 챗봇·찜만 적용 | `fetchJson`/`build*PostInit` + 필터·챗봇·찜 통합 | **완화** |
| 마이페이지 찜 개수 불일치 | `syncMypageWishlistCount` | **완화** |
| 검색 submit 연속 클릭 | `filterSubmitInFlight` + 버튼 busy | **완화** |
| 필터 옵션 로딩 UI 없음 | `data-filter-options-loading` | **완화** |
| 로그인 입력 검증 HTML5만 | `setCustomValidity` 검증 | **부분 완화** |
| 모바일 터치·키보드 미검증 | `mobile-viewport.css`, 사이드바·viewport JS | **부분 완화(실기기 확인 필요)** |

#### 2.4.2 2차 수정 후 잔여·신규 관찰

| 심각도 | 문제 | 원인 | 영향 |
|---|---|---|---|
| Medium | 챗봇 세션 만료(401 JSON) 시 로그인 유도 없음 | `send_chat` 401 + `fetchJson`에 `loginUrl` 미전달; 말풍선에 SERVER 계열 문구만 표시 | 재로그인 경로 불명확 (**확인 필요**: 실제 401 응답 본문·헤더) |
| Medium | `filter.js` 단일 파일 760줄+ | 필터·칩·프리셋·옵션·모바일·submit 한 모듈 | 회귀·테스트 비용 증가 |
| Low | `renderChipGroups`가 `list`에 `click` 리스너 매번 등록 | `loadOptions` 후 1회 호출이라 현재는 중복 없음; 재호출 시 중복 가능 | 칩 이중 토글 (**현재 경로에서는 재현 어려움**) |
| Low | 회원가입·비밀번호 찾기 클라이언트 검증 부족 | `registerpage.html` HTML5만; `reset_password_form` API 없음 | 잘못된 기대·빈 동작 |
| Low | 인라인 스크립트·전역 `onclick` 잔존 | `mainpage.html`, `account_profile.html`, `product_actions.html` | 정책 분산·중복 초기화 위험 |
| Low | TypeScript·Hook 구조 없음 | Django SSR + 바닐라 IIFE | 타입·컴포넌트 단위 검증 한계 |
| Low | 챗봇 `renderMessages` 전량 `innerHTML` 재구성 | 메시지 수 증가 시 비용 | 스크롤·입력 지연 가능 (**확인 필요**) |
| Low | 마이페이지 빈 그리드 판별 `document.querySelectorAll(".grid > .group")` | 전역 셀렉터 | 다른 `.grid` 추가 시 오탐 가능 |

### 2.5 수정 제안

> 코드는 수정하지 않았으며, 방향만 기술합니다.

- **제안 1:** 챗봇 `fetchJson`에 `loginUrl`(또는 401 전용 분기)을 연결해 세션 만료 시 로그인 이동 또는 전용 말풍선 문구 표시.
- **제안 2:** `filter.js`를 `filter-options.js` / `filter-chips.js` / `filter-submit.js` 등으로 분리하거나, 칩 `click`은 이벤트 위임 1회만 등록.
- **제안 3:** 회원가입에 로그인과 동일한 `setCustomValidity` 패턴 적용; 비밀번호 찾기는 API 확정 전 “준비 중” UI.
- **제안 4:** 인라인 스크립트를 `static/js`로 이전하고 페이지별 `extra_js`만 로드.
- **제안 5 (장기):** 핵심 모듈 JSDoc/TypeScript, 챗봇 incremental DOM 업데이트 검토.

---

## 3. 테스트 시나리오 및 결과

| 테스트 항목 | 테스트 내용 | 예상 결과 | 실제 분석 결과 (2차 후) | 상태 |
|---|---|---|---|---|
| 초기 렌더링 | 페이지 진입 시 화면 렌더링 | 오류 없이 렌더링 | 템플릿·`api-response.js` 선행 로드(검색/챗봇/찜)·`LGSearchPage` 초기화 경로 정상 | **Pass** |
| API 성공 응답 | 정상 데이터 수신 | 데이터 정상 표시 | 챗봇 `response`/`response_tail`, 찜 `{ ok, favorited }`, 필터 JSON → `optionsByType` 분기 유지 | **Pass** |
| API 실패 응답 | 서버/네트워크 오류 | 에러 처리 UI 표시 | 챗봇 말풍선; 찜 `alert`+로그; 필터 인라인 에러 배너+로그 | **Pass** |
| 빈 데이터 | 응답 데이터 없음 | 빈 상태 UI | 검색 empty·마이페이지 empty·`CHAT_EMPTY` 등 템플릿/메시지 존재 | **Pass** |
| 연속 클릭 | 주요 버튼 연속 클릭 | 중복 실행 방지 | 챗봇 `inFlight`; 찜 `wishlistInFlight`+`disabled`; 검색 submit `filterSubmitInFlight` | **Pass** |
| 입력 검증 | 잘못된 입력값 | 검증/방어 | 검색 `clampRangeInput`+submit 재clamp; 로그인 클라이언트 검증; 회원가입은 HTML5 위주 | **Warning** |
| 로딩 상태 | 비동기 처리 중 | 로딩 UI | 챗봇 placeholder·disable; 찜 busy; 필터 옵션 로딩 배너+`aria-busy` | **Pass** |
| 모바일 화면 | 작은 화면 | UI 깨짐 없음 | `mobile-viewport.css`, 사이드바 backdrop/ESC/body lock, `visualViewport` — **실기기·iOS Safari 확인 필요** | **Warning** |

**1차 재평가 대비:** API 실패·연속 클릭·로딩·필터 옵션 피드백은 **Warning → Pass**로 상향. 입력 검증·모바일은 **Warning 유지**(범위 확대·실측 미완).

---

## 4. 프론트엔드 코드 품질 검수

## 4.1 성능 최적화

### 발견된 문제

- 챗봇 `renderMessages()`가 매번 `messagesList.innerHTML = ""` 후 전체 재생성.
- 검색 필터는 전체 페이지 GET이라 submit 빈도는 낮으나, `filter.js` 초기화·칩 DOM 생성 비용이 큼.
- 필터 옵션은 페이지당 1회 `fetch` (적절).

### 영향

- 장문 대화·저사양 모바일에서 렌더·스크롤 지연 가능 (**확인 필요**).
- 검색 일반 사용에서는 영향 제한적.

### 개선 방향

- 챗봇 메시지 incremental append/patch.
- 칩 리스트 변경 시 diff 업데이트 또는 이벤트 위임 단일화.

---

## 4.2 보안 취약점

### 발견된 문제

- **완화 유지:** `isSafeHttpUrl`, `sanitizeChatHtml`, `escapeHtml` + 마크다운 후 sanitizer.
- `buildChatImageHtml`은 URL trim 후 문자열 결합; 최종 출력은 `sanitizeChatHtml` 경유 시 `IMG` `src` 재검증.
- 서버 히스토리는 hydrate 시 `textContent` 사용(안전); 이후 assistant는 마크다운 경로.
- CSP 헤더·속성 전용 이스케이프 강화 여부는 코드베이스에서 확인되지 않음 (**확인 필요**).

### 영향

- 1차 대비 XSS·악성 스킴 리스크는 낮음.
- 운영 페이로드·CSP 미적용 시 잔여 공격면은 **확인 필요**.

### 개선 방향

- CSP 정책(백엔드 연동) 검토.
- 악성 마크다운·이미지 URL 샘플 실브라우저 검증.

---

## 4.3 유지보수성

### 발견된 문제

- `api-response.js`로 API 레이어 일원화(2차 강화).
- `searchpage.js` / `pagination.js` 분리는 양호.
- `filter.js`·`chatpage.js`는 대형 단일 IIFE.
- TypeScript 없음; Hook/React 구조 없음(Django SSR 전제와 일치).
- 인라인 스크립트·`onclick` 혼재.

### 영향

- 2차로 API·검색 UX 일관성은 향상.
- 기능 추가 시 `filter.js` 충돌·회귀 위험 상대적으로 큼.

### 개선 방향

- 모듈 분리·인라인 JS 이전·JSDoc/TS 점진 도입.

---

## 4.4 UX 안정성

### 발견된 문제

- **개선:** 필터 옵션 로딩/실패 배너, 찜 카운트, submit 가드, 로그인 검증, 모바일 보조 CSS/JS.
- **잔여:** 에러 채널이 화면별 상이(말풍선 / `alert` / 인라인 배너) — 의도적이나 통일 여지 있음.
- 비밀번호 찾기 버튼은 패널 전환만, 실제 재설정 없음.
- 챗봇 401·빈 `response` 시 사용자 안내 문구 정확도는 **확인 필요**.

### 영향

- 핵심 플로우(검색·찜·챗봇 전송) 신뢰도는 1차 대비 상승.
- 인증 보조·세션 만료·실기기 모바일은 추가 검증 필요.

### 개선 방향

- 세션 만료 공통 UX.
- 미구현 기능 “준비 중” 명시.
- (선택) 토스트/배너 채널 통일.

---

## 5. 우선순위별 개선 권장 사항

| 우선순위 | 항목 | 개선 내용 | 예상 효과 |
|---|---|---|---|
| 1 | 챗봇 세션 만료 UX | 401/비로그인 시 로그인 이동 또는 전용 말풍선 | 세션 끊김 시 혼란 감소 |
| 2 | `filter.js` 모듈 분리·이벤트 위임 | 칩 리스너 중복 방지·가독성 | 회귀·유지보수 비용 감소 |
| 3 | 회원가입·비밀번호 찾기 | 검증/준비 중 UI·API 연동 시 `ApiResponse` 재사용 | 인증 플로우 기대치 정합 |
| 4 | 인라인 스크립트 정리 | `mainpage` 캐러셀·프로필·상품 인라인 → `static/js` | 정책·로드 순서 일원화 |
| 5 | 챗봇 렌더 성능 | incremental DOM | 장문 대화 체감 성능 개선 |

---

## 6. 최종 평가

### 전체 평가

- **1차 핵심(챗봇 보안·찜 중복·API 공통화)**은 유지·강화되었고, **2차에서 지적되던 검색 필터·테스트 시나리오 Warning 다수가 코드상 해소**된 상태입니다.
- 아키텍처는 **Django 템플릿 + 바닐라 JS(IIFE)** 이며, `api-response.js` 중심의 API 레이어가 챗봇·찜·필터 옵션까지 확장되었습니다.
- **TypeScript/React Hook 구조는 없음** — 프로젝트 전제와 일치.
- **실브라우저·실기기 검증 없이** 정적 분석만 수행했으므로, 모바일·iOS 키보드·401·장문 성능은 반드시 수동 QA가 필요합니다.

### 가장 먼저 해결해야 할 문제

- **챗봇 비로그인/401 응답 시 사용자 안내 및 로그인 경로** — API는 `status=401` JSON을 반환하나, 프론트는 `loginUrl` 없이 일반 오류 말풍선으로 처리하는 구조입니다 (**동작 일치 여부 확인 필요**).

### 수정 없이 확인 가능한 결론

- 검색 필터: `fetchJson`·로딩/에러 UI·submit in-flight·범위 clamp·모바일 viewport 보완 **코드 존재**.
- 찜: `fetchJson`·in-flight·마이페이지 `data-wishlist-count-badge` 동기화 **코드 존재**.
- 챗봇: `inFlight`·`fetchJson`·URL sanitizer·서버 메시지 `textContent` hydrate **코드 존재**.
- 로그인: `loginpage.js` 클라이언트 검증 **코드 존재**; 회원가입·비밀번호 찾기는 **미흡**.

### 추가 확인 필요 사항

- 실제 모바일(iOS Safari, Android Chrome)에서 챗봇 사이드바·입력 키보드·검색 필터 스크롤.
- 세션 만료 후 `send_chat` 401 응답과 화면 메시지·리다이렉트 일치.
- 악성 마크다운·외부 이미지 URL 클릭/렌더 샘플 테스트.
- 장문 대화 시 챗봇 스크롤·렌더 성능.
- DevTools 네트워크 차단 시 필터 옵션 에러 배너·칩 빈 상태 degrade 동작.

---

## 부록: 문서 이력

| 버전 | 설명 |
|---|---|
| [frontend-test-report.md](frontend-test-report.md) | 1차 수정 후 재평가 — 2차 개선 권장(§5)의 근거 문서 |
| 현재 | **2차 수정 후 QA 재평가** — §5 권장 항목 반영 코드 기준 정적 검수 |