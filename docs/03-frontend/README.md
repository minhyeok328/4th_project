# 프론트엔드

[문서 홈](../README.md)

## 구현 방식

Django Templates가 페이지를 서버에서 렌더링하고 바닐라 JavaScript가 비동기 요청과 화면 상태를 처리합니다. Tailwind CSS v4와 DaisyUI를 [theme/static_src](../../theme/static_src/)에서 빌드합니다. React·SPA 라우터·TypeScript 기반 프로젝트는 아닙니다.

## 주요 연결

| 기능 | 템플릿·클라이언트 | 서버 연결 |
|---|---|---|
| 검색 | `searchpage.html`, `search/filter.js`, `search/pagination.js` | GET `/products/` |
| 상세·찜 | `productpage.html`, `wishlist-toggle.js` | POST `/accounts/mypage/` |
| 채팅 | `chatpage.html`, `chatpage.js` | POST `/api/send_chat/` |
| 계정 | 로그인·회원가입·마이페이지 템플릿 | Django 폼 POST |

[api-response.js](../../static/js/api-response.js)는 JSON 파싱·리다이렉트·네트워크 실패를 공통 형식으로 처리합니다. 사용하는 페이지는 이 파일을 의존 모듈보다 먼저 로드해야 합니다. 검색 결과는 HTML 재탐색으로 갱신하며 필터 옵션만 정적 JSON으로 가져옵니다.

## 상세 문서

- [화면 구성](frontend.md): 페이지별 구현과 미연결 UI
- [페이지와 URL](pages-and-routes.md): 뷰·템플릿 매핑
- [템플릿과 컴포넌트](templates-components.md): include 구조·데이터 속성
- [클라이언트 JavaScript](client-javascript.md): 공통 모듈·이벤트·로드 순서

## 검증 범위

[1차 기록](frontend-test-report.md)과 [2차 기록](frontend-final-report.md)은 과거 정적 분석입니다. 기록의 Pass는 현재 브라우저 실행 성공을 의미하지 않습니다. 모바일 키보드, 장문 채팅, 세션 만료, 외부 이미지·마크다운 입력은 [검증과 한계](../10-quality/verification-and-limitations.md)의 수동 확인 대상입니다.
