# Frontend 파트 문서

[← Docs 홈](../README.md)

**담당**: 박기은, 서민혁  
**스택**: Django Templates (SSR), Tailwind CSS v4, django-tailwind, 바닐라 JS

## 문서 목록

| 문서 | 내용 |
|------|------|
| [frontend.md](frontend.md) | 화면설계·페이지 체크리스트 |
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
| `static/js/` | 페이지별 클라이언트 로직 |
| `static/css/` | 보조 CSS |
| `static/data/` | 필터 옵션 JSON |
| `theme/` | Tailwind 소스·빌드 |
