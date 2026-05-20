# 프론트엔드 테스트 평가서

> **본 문서는 1차 수정 후 재평가입니다.**  
> 초기 검수에서 식별된 우선순위 1~3 항목(챗봇 URL 보안, 찜 중복 실행 방지, API 실패 UX 표준화)이 코드에 반영된 뒤, 동일한 검수 기준으로 프론트엔드 전체를 다시 점검한 결과를 정리합니다.  
> **1차 이전**에 작성된 단정적 문구(예: “찜은 중복 방지 미흡”)는 아래 **§2.4.1·§3**에서 ‘이전 상태’로 구분하고, **현재 상태**는 재평가 결론에 맞게 갱신했습니다.  
> 구현 상세: [client-javascript.md](client-javascript.md)  
> **2차 수정·QA 결과:** [frontend-final-report.md](frontend-final-report.md) (본 문서 §5 권장 항목 반영 후 재평가)

---

## 0. 1차 수정 반영 요약 (재평가 전제)

| 우선순위 (초기) | 항목 | 반영 위치 (요약) | 재평가 시 판단 |
|---|---|---|---|
| 1 | 챗봇 마크다운 URL 보안 | `static/js/chatpage.js` — `isSafeHttpUrl`, `sanitizeChatHtml`, 이미지 URL 판별·공통 `<img>` 스타일 | **반영됨** — High 이슈 완화 |
| 2 | 찜 중복 실행 방지 | `static/js/wishlist-toggle.js` — `wishlistInFlight`, `setWishlistButtonBusy` | **반영됨** — 연속 클릭 가드·버튼 비활성화 |
| 3 | API 실패 UX 표준화 | `static/js/api-response.js` — `parseFetchJsonResponse`, `MESSAGES`; 챗봇·찜에서 사용 | **부분 반영** — 챗봇·찜은 통일, 검색 필터 옵션 `fetch` 등은 미연동 |

**스크립트 로드 순서 (참고):** 챗봇·상품·마이페이지에서 `api-response.js`가 찜/챗봇 모듈보다 먼저 로드되어 `ApiResponse` 전역이 보장됩니다.

---

## 1. 검수 개요

- **검수 대상:** Workspace 전체 프론트엔드 (`templates/`, `static/js/`, `static/css/`, Tailwind 템플릿 기반 화면)
- **검수 목적:** 1차 수정 반영 후, 사용자 주요 플로우 중심으로 장애 가능성·영향도·복잡도가 큰 로직을 우선 재점검하고, **잔여 리스크**와 **2차 개선 후보**를 식별함
- **문서 성격:** **1차 수정 후 재평가** (초기 평가서의 연장; 동일 레포 기준 시점 이후 스냅샷)
- **코드 수정 여부 (본 문서 작성 시):** 문서만 갱신 (리포트 작성 목적의 분석·서술)
- **주요 확인 기능:**
  - 검색/필터/페이지네이션 (`filter.js`, `pagination.js`, `searchpage.js`)
  - 챗봇 메시지 송수신·마크다운 렌더링 (`chatpage.js` + `api-response.js`)
  - 상품 상세 찜하기 / 마이페이지 찜 해제 (`wishlist-toggle.js`, 관련 템플릿 data 속성)
  - 로그인·비밀번호 찾기 패널 전환 (`loginpage.js`, `reset_password_form` 등)
- **우선 검토 기준:**
  - 사용자 주요 플로우 직접 영향
  - API 요청/응답 처리, 에러/로딩 처리 일관성
  - 이벤트/비동기 중복 실행 가능성
  - 입력 검증, 보안(특히 HTML로 이어지는 경로)
  - 유지보수성(책임 분리, 중복 코드, 하드코딩, 공통 유틸 적용 범위)

---

## 2. 주요 로직 분석

### 2.1 우선 검토 대상 선정 이유 (재평가 기준)

| 우선순위 | 검토 대상 | 선정 이유 | 사용자 영향도 |
|---|---|---|---|
| 1 | 챗봇 메시지 렌더링/전송 | HTML 렌더링 + `fetch` POST 빈도 높음; 1차 보안·API UX 수정이 집중됨 | High |
| 2 | 찜 토글 API | 상태 변경·세션/리다이렉트 응답과 맞닿음; 1차에서 in-flight·공통 파서 반영 | High |
| 3 | 검색 필터/페이지네이션 | 파라미터·범위 clamp·칩 UI 복잡도 큼; `fetch` 기반 옵션 로드는 공통 API 레이어 밖에 있음 | Medium |

### 2.2 관련 파일 및 함수 (1차 수정 후 기준)

| 구분 | 파일 경로 | 함수/컴포넌트명 | 역할 |
|---|---|---|---|
| API 연동 | `static/js/chatpage.js` | `sendMessage` | 챗봇 POST, `inFlight`, `ApiResponse.parseFetchJsonResponse` |
| API 연동 | `static/js/wishlist-toggle.js` | `postToggleFavorite`, `productPageWishlistToggle`, `mypageWishlistToggle` | 찜 POST, in-flight, 버튼 busy |
| API 연동 | `static/js/api-response.js` | `parseFetchJsonResponse`, `notifyApiError`, `MESSAGES` | JSON/리다이렉트/파싱 실패 공통 처리 |
| API 연동 | `static/js/search/filter.js` | `loadOptions` | 정적 JSON 옵션 `fetch` (공통 레이어 미적용) |
| 상태 관리 | `static/js/chatpage.js` | `messages`, `inFlight`, `setBusy` | 메시지·전송 잠금 |
| 상태 관리 | `static/js/wishlist-toggle.js` | `wishlistInFlight` | `product_code` 단위 동시 요청 차단 |
| 이벤트 처리 | `static/js/search/filter.js` | `initSearchFilter`, `renderChipGroups`, form `submit` | 필터·URL 파라미터 |
| 이벤트 처리 | `static/js/search/pagination.js` | `initPagination` | 페이지 링크 생성 |
| UI 렌더링 | `templates/components/chat/chat_main.html` | `#chat-input-form`, `data-server-message` | 챗봇 입력·서버 히스토리 |
| UI 렌더링 | `templates/components/search/*` | 필터·그리드·페이지네이션 | 검색 UI |
| 유틸/보안 | `static/js/chatpage.js` | `renderMarkdown`, `sanitizeChatHtml`, `isSafeHttpUrl` | 마크다운·URL allowlist·DOM sanitizer |

### 2.3 현재 동작 흐름 (재평가 시점)

1. **검색:** `searchpage.js` → `LGSearchPage.initSearchFilter` / `initPagination` → URL 복원·범위 clamp·칩 렌더 → `loadOptions()`로 `SEARCH_FILTER_OPTIONS_URL` JSON 로드 → 폼 submit 시 빈 `name` 제거 후 전체 페이지 GET.
2. **챗봇:** `chatpage.js` 단일 초기화 가드 → 서버 메시지 `textContent` hydrate → `sendMessage`에서 placeholder·`setBusy` → `ApiResponse.parseFetchJsonResponse` → assistant는 `renderMarkdown` + `sanitizeChatHtml` + (선택) 이미지 URL 인라인 렌더.
3. **찜:** 템플릿에 `data-wishlist-post-url`, `data-csrf-token` 등 설정 → `wishlist-toggle.js`에서 `fetch` → `ApiResponse.parseFetchJsonResponse` (상품 상세는 `loginUrl` 옵션) → 성공 시 DOM 갱신(상세 토글 / 마이페이지 카드 제거·빈 그리드 시 `reload`).

### 2.4 발견된 문제점

#### 2.4.1 초기 검수 시점(1차 수정 전) — 참고용 보관

| 심각도 | 문제 | 원인 | 영향 |
|---|---|---|---|
| High | 챗봇 마크다운 링크/이미지 URL 스킴 검증 부재 | `javascript:`/`data:` 등 차단 없음 | 악성 링크·XSS 리스크 |
| Medium | 찜 연속 클릭 시 중복 요청 | in-flight·disable 없음 | 상태 불일치·부하 |
| Medium | 마이페이지 찜해제 비정상 응답 처리 | `response.json()` 전제, 비JSON 미대응 | 파싱 오류·무응답 체감 |
| Medium | 상세 찜 실패 시 피드백 부족 | `console.error` 위주 | 사용자 무인지 |

#### 2.4.2 1차 수정 후 재평가 — 잔여·신규 관찰

| 심각도 | 문제 | 원인 | 영향 |
|---|---|---|---|
| Medium | 검색 필터 옵션 `fetch` 실패 시 사용자 안내 없음 | `loadOptions`가 `.catch`에서 `{}`만 설정, `ApiResponse` 미사용 | 칩/옵션 공백 시 원인 불명 |
| Low | `ApiResponse` 적용 범위가 챗봇·찜에 한정 | 설계상 점진 도입 | 화면별 에러 정책 완전 통일까지는 미도달 |
| Low | 마이페이지 “총 N개” 뱃지가 클라이언트 제거와 동기화 안 됨 | 카드만 DOM 제거, 카운트는 서버 렌더 값 | 숫자 불일치 체감(마지막 1건 전까지) |
| Low | 비밀번호 찾기 미연동 | `type="button"` + API 없음 | 기대 불일치 (1차 범위 밖) |
| Low | TypeScript·Hook 아키텍처 부재 | Django 템플릿 + 바닐라 IIFE | 타입·컴포넌트 단위 회귀 방지 한계 |
| Low | 인라인 스크립트 잔존 | `mainpage.html` 캐러셀, `account_profile.html` 등 | 공통 레이어와 분산 |

### 2.5 수정 제안

> **재평가 관점:** 1차에서 이미 반영된 항목(챗봇 URL·찜 가드·챗봇/찜 API 파싱)은 아래 “완료”로 보고, **2차 이후**에 고려할 제안만 나열합니다.

- **완료(1차):** 챗봇 URL allowlist + DOM sanitizer; 찜 in-flight + 버튼 busy; 챗봇·찜에 공통 JSON 파서 및 사용자 메시지(말풍선 / `alert`).
- **제안 1 (2차):** `filter.js`의 `loadOptions`에 `ApiResponse.parseFetchJsonResponse` 적용 및 실패 시 배지·토스트 등 최소 피드백.
- **제안 2 (2차):** 마이페이지 찜 해제 성공 시 `총 N개` DOM 갱신 또는 카운트 전용 API/부분 템플릿 재렌더.
- **제안 3 (2차):** 비밀번호 찾기 — API 확정 전 “준비 중” 안내 또는 백엔드 연동 후 동일 `ApiResponse` 패턴 적용.
- **제안 4 (장기):** 인라인 스크립트를 `static/js`로 이전, 핵심 모듈 JSDoc/TS 전환 검토.

---

## 3. 테스트 시나리오 및 결과 (1차 수정 후 재평가)

| 테스트 항목 | 테스트 내용 | 예상 결과 | 실제 분석 결과 (재평가) | 상태 |
|---|---|---|---|---|
| 초기 렌더링 | 페이지 진입 시 화면 렌더링 확인 | 오류 없이 렌더링 | 템플릿·스크립트 로드 경로 정상 | **Pass** |
| API 성공 응답 | 정상 데이터 수신 | 데이터 정상 표시 | 챗봇 JSON, 찜 `{ ok, favorited }` 분기 유지 | **Pass** |
| API 실패 응답 | 서버/네트워크 오류 | 에러 처리 UI 표시 | 챗봇: 말풍선 문구; 찜: `alert`+로그; 필터 옵션 `fetch`만 무음 | **Warning** |
| 빈 데이터 | 응답 데이터 없음 | 빈 상태 UI 표시 | 검색 그리드·마이페이지 empty·챗봇 `CHAT_EMPTY` 등 존재 | **Pass** |
| 연속 클릭 | 주요 버튼 빠르게 여러 번 클릭 | 중복 실행 방지 | 챗봇 `inFlight`; 찜 `wishlistInFlight`+`disabled`; 검색 submit 등은 별도 가드 없음 | **Warning** |
| 입력 검증 | 잘못된 입력값 입력 | 검증 또는 방어 처리 | 검색 범위 `clampRangeInput` 양호; 로그인 등은 HTML5·서버 의존 | **Warning** |
| 로딩 상태 | 비동기 처리 중 | 로딩 상태 표시 | 챗봇 placeholder·disable 양호; 찜 busy 스타일; 필터 옵션 로딩 UI 없음 | **Warning** |
| 모바일 화면 | 작은 화면에서 실행 | UI 깨짐 없음 | Tailwind 반응형 다수; 실제 터치·키보드는 **확인 필요** | **Warning** |

**초기 평가 대비 변화 요약:** 찜 연속 클릭 항목은 **Fail → Warning**(핵심 버튼은 가드 적용, 다른 폼은 예외). API 실패는 찜·챗봇 구간은 **Warning 완화**(사용자 메시지 확보), 필터 옵션은 여전히 **Warning**.

---

## 4. 프론트엔드 코드 품질 검수 (재평가)

## 4.1 성능 최적화

### 발견된 문제

- 챗봇 `renderMessages`가 전체 목록을 매번 `innerHTML`로 재구성 — 대화 길이 증가 시 비용 증가 가능.
- 검색은 전체 페이지 네비게이션 위주라 필터 제출 빈도는 보통 낮으나, 중복 submit에 대한 클라이언트 측 제한은 없음.

### 영향

- 장문 대화에서 스크롤·렌더 지연 가능성(실측 **확인 필요**).
- 검색은 일반 사용에서 영향 제한적.

### 개선 방향

- 챗봇 incremental DOM 업데이트 검토.
- 필요 시 submit 짧은 disable 또는 debounce.

---

## 4.2 보안 취약점

### 발견된 문제 (재평가)

- **완화됨:** 마크다운 링크/이미지에 `http`/`https` 검증 및 `sanitizeChatHtml`로 허용 태그·속성 화이트리스트 처리.
- **잔여:** 이미지 `alt` 등 속성 문자열 이스케이프를 별도 레이어로 강화할 여지(낮은 우선, 실제 페이로드로 **확인 필요**).
- 서버 렌더 히스토리는 Django 이스케이프 전제; 이후 `renderMarkdown` 경로와의 조합은 운영 데이터로 재검증 권장.

### 영향

- 1차 대비 챗봇 XSS·악성 스킴 리스크는 현저히 감소.
- 속성 경계·저장 메시지 조합은 추가 점검 가치 있음.

### 개선 방향

- 속성 전용 이스케이프·CSP 헤더 검토(백엔드 설정과 연동 시).

---

## 4.3 유지보수성

### 발견된 문제

- `api-response.js`·`wishlist-toggle.js`로 API·찜 책임이 일부 모듈화됨.
- 검색은 `filter.js` / `pagination.js` / `searchpage.js`로 이미 분리되어 가독성 양호.
- 템플릿 인라인 스크립트·전역 `onclick`이 여전히 혼재; TypeScript 없음.

### 영향

- 챗봇·찜 유지보수성은 향상; 검색·메인·프로필은 분산 유지.
- 계약 변경 시 런타임만으로 검증되는 부분 존재.

### 개선 방향

- 남은 `fetch`를 `ApiResponse`로 통합.
- 인라인 → `static/js` 이전, JSDoc/TS 점진 도입.

---

## 4.4 UX 안정성

### 발견된 문제

- 챗봇·찜 실패 시 사용자 피드백은 **1차 대비 개선** (말풍선 vs `alert` — 채널은 화면별 상이).
- 필터 옵션 로드 실패·비밀번호 찾기 미구현은 여전히 체감 공백.
- 마이페이지 찜 개수 뱃지와 DOM 불일치 가능.

### 영향

- 핵심 플로우 신뢰도는 상승; 보조 플로우에서 “무반응” 인식 잔존.

### 개선 방향

- 토스트/배너 등 통일 채널 검토.
- 미구현 기능 명시 안내.
- 카운트 동기화.

---

## 5. 우선순위별 개선 권장 사항 (2차 이후)

| 우선순위 | 항목 | 개선 내용 | 예상 효과 |
|---|---|---|---|
| 1 | 검색 필터 옵션 API 실패 UX | `loadOptions`에 공통 파서·사용자 안내 | 옵션 공백 시 원인 가시성 |
| 2 | `ApiResponse` 적용 범위 확대 | 남은 `fetch`·향후 폼 AJAX에 동일 정책 | 에러 처리 일관성 |
| 3 | 마이페이지 찜 카운트 동기화 | DOM 또는 서버 재조회 | 숫자·목록 일치 |
| 4 | 비밀번호 찾기·인라인 스크립트 | 정책 확정 후 모듈화 | 기대치·유지보수 개선 |

---

## 6. 최종 평가 (1차 수정 후 재평가)

### 전체 평가

- 초기 우선순위 1~3은 코드에 **반영되어** 챗봇 보안·찜 중복·챗봇/찜 API 실패 UX는 **정적 분석 기준으로 크게 개선**되었습니다.
- 검색 필터의 옵션 JSON 로드, 비밀번호 찾기, 일부 인라인 스크립트, TypeScript 부재는 **잔여 과제**로 남습니다.
- 아키텍처는 Django 템플릿 + 바닐라 JS 모듈 혼합이며, React/Hook 기반 구조는 아닙니다.

### 가장 먼저 해결해야 할 문제 (재평가 기준)

- **검색 `loadOptions` 실패 시 사용자 안내 부재** — 공통 API 정책이 아직 적용되지 않은 유일한 주요 `fetch` 경로에 가깝습니다.

### 수정 없이 확인 가능한 결론

- 챗봇: URL 검증·sanitizer·`inFlight`·공통 파서 연동 **양호**.
- 찜: in-flight·버튼 busy·공통 파서·실패 `alert` **양호**.
- 검색: 범위 clamp·빈 파라미터 제거·페이지네이션 **양호**.

### 추가 확인 필요 사항

- 실제 브라우저에서 악성 마크다운·외부 이미지 URL 샘플로 챗봇 렌더·클릭 동작 검증.
- 모바일에서 챗봇 사이드바·입력·검색 필터 터치 동작.
- 세션 만료 시 `send_chat` 401/302 응답과 챗봇 말풍선 문구의 일치 여부.
- 장문 대화 시 챗봇 스크롤·렌더 성능.

---

## 부록: 문서 이력

| 버전 | 설명 |
|---|---|
| 초기 | 1차 수정 전 정적 검수 결과 (본 파일 상단 §2.4.1·초기 §3과 대응) |
| 현재 | **1차 수정 후 재평가** — 반영 코드 기준으로 §0·§1·§2.2~2.4.2·§3~§6 갱신 및 확장 |
| 후속 | [frontend-final-report.md](frontend-final-report.md) — 본 문서 §5 기준 2차 코드 반영 후 QA 재평가 |
