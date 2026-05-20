# Frontend 파트 문서

[← Docs 홈](../README.md)

**담당**: 박기은, 서민혁  
**스택**: Django Templates (SSR), Tailwind CSS v4, django-tailwind, 바닐라 JS

## 문서 흐름 (평가 → 개선 → QA)

```
정적 검수 (1차 반영 후)
  → frontend-test-report.md  … 잔여 리스크·§5 2차 권장
        ↓ 코드 반영
  → frontend-final-report.md … 2차 반영 후 QA 재평가
        ↓
  client-javascript.md · frontend.md  … 구현·체크리스트 동기화
```

## 문서 목록

| 문서 | 내용 |
|------|------|
| [frontend.md](frontend.md) | 화면설계·페이지 체크리스트·1·2차 개선 요약 |
| [client-javascript.md](client-javascript.md) | 공통 JS 모듈·`ApiResponse`·페이지별 로드 순서 |
| [frontend-test-report.md](frontend-test-report.md) | **1차 수정 후** 재평가·2차 개선 권장(§5) |
| [frontend-final-report.md](frontend-final-report.md) | **2차 수정 후** QA 재평가 (test-report §5 기준) |
| [pages-and-routes.md](pages-and-routes.md) | URL ↔ 템플릿 ↔ 뷰 매핑 |
| [templates-components.md](templates-components.md) | 컴포넌트 트리·include 구조 |

## 연관 파트

- API 연동: [06-api/rest-api.md](../06-api/rest-api.md)
- 검색·필터 동작: [08-features/search-and-filter.md](../08-features/search-and-filter.md)
- Tailwind 빌드: [개발 환경](../01-getting-started/development-environment.md)

## 디렉터리 (Frontend 관점)

| 경로 | 역할 |
|------|------|
| `templates/` | 페이지·재사용 컴포넌트 |
| `static/js/` | 페이지별·공통 클라이언트 로직 (`api-response.js`, `wishlist-toggle.js`, `search/filter.js` 등) |
| `static/css/` | 보조 CSS (`search_filter.css`, `mobile-viewport.css`) |
| `static/data/` | 필터 옵션 JSON |
| `theme/static_src/` | Tailwind npm (`install` · `build` · `dev`) |
| `media/` | 프로필 업로드 (accounts) |
