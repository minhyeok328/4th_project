/**
 * 검색 결과 페이지 엔트리 스크립트.
 *
 * 역할: DOM 준비 후 `window.LGSearchPage`에 등록된 하위 모듈만 순서대로 초기화한다.
 * 실제 필터·페이지네이션 로직은 `search/filter.js`, `search/pagination.js`에 있다.
 *
 * 실행 순서: searchpage.js → initSearchFilter → initPagination (템플릿에서 스크립트 로드 순서에 의존)
 */
(function () {
    "use strict";

    // REFACTOR (유지보수성): 엔트리 파일은 초기화만 담당하고 세부 로직은 search/* 모듈로 분리
    const module = window.LGSearchPage || {};
    if (typeof module.initSearchFilter === "function") {
        module.initSearchFilter();
    }
    if (typeof module.initPagination === "function") {
        module.initPagination();
    }
})();
