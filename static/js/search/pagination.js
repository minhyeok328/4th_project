/**
 * 검색 결과 페이지네이션 클라이언트 모듈.
 *
 * 역할: 서버가 data-*로 넘긴 현재 페이지·총 페이지를 읽어 컨트롤 DOM을 동적 생성한다.
 * 링크는 기존 쿼리스트링에 `page`만 바꾼 GET — 필터 조건은 URLSearchParams로 유지.
 *
 * 등록: `window.LGSearchPage.initPagination` — `searchpage.js`에서 호출.
 */
(function () {
    "use strict";

    // REFACTOR (유지보수성): 페이지네이션 로직을 별도 모듈로 분리해 검색 필터 로직과 책임 분리
    /**
     * `[data-pagination]` 네비게이션에 요약 문구·이전/다음·페이지 번호 버튼을 렌더한다.
     * numPages <= 1 이면 컨트롤을 만들지 않는다.
     */
    function initPagination() {
        const nav = document.querySelector("[data-pagination]");
        if (!nav) {
            return;
        }

        const current = Number(nav.dataset.current);
        const numPages = Number(nav.dataset.numPages);
        const summary = nav.querySelector("[data-pagination-summary]");
        const controls = nav.querySelector("[data-pagination-controls]");

        if (!controls || numPages <= 1) {
            return;
        }

        const btnBase =
            "inline-flex min-h-10 items-center justify-center rounded-xl border px-3 text-sm font-medium shadow-sm transition-all";
        const btnDefault = btnBase + " border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50";
        const btnActive = btnBase + " min-w-10 border-red-600 bg-red-50 font-bold text-red-600";
        const btnDisabled = btnBase + " cursor-not-allowed border-gray-100 bg-gray-50 text-gray-300";

        /** 현재 검색 쿼리를 유지한 채 page 파라미터만 바꾼 href 생성 */
        function pageHref(page) {
            const params = new URLSearchParams(window.location.search);
            params.set("page", String(page));
            return "?" + params.toString();
        }

        /**
         * 현재 페이지 주변·양 끝 페이지 번호와 생략(gap) 마커 목록을 만든다.
         * 긴 목록에서도 UI 폭을 제한하기 위한 윈도우+끝 고정 전략.
         */
        function pageNumbers() {
            const windowSize = 2;
            const pages = new Set();
            const onEnds = 1;

            for (let i = 1; i <= Math.min(onEnds, numPages); i += 1) {
                pages.add(i);
            }
            for (let i = Math.max(1, numPages - onEnds + 1); i <= numPages; i += 1) {
                pages.add(i);
            }
            for (let i = current - windowSize; i <= current + windowSize; i += 1) {
                if (i >= 1 && i <= numPages) {
                    pages.add(i);
                }
            }

            const sorted = Array.from(pages).sort(function (a, b) {
                return a - b;
            });

            const items = [];
            let prev = null;
            sorted.forEach(function (num) {
                if (prev !== null && num - prev > 1) {
                    items.push({ kind: "gap" });
                }
                items.push({ kind: "page", number: num });
                prev = num;
            });
            return items;
        }

        function makeLink(label, page, className) {
            const link = document.createElement("a");
            link.href = pageHref(page);
            link.className = className;
            link.textContent = label;
            return link;
        }

        function makeSpan(label, className) {
            const span = document.createElement("span");
            span.className = className;
            span.textContent = label;
            return span;
        }

        if (summary) {
            summary.textContent =
                nav.dataset.start + "–" + nav.dataset.end + " / 총 " + nav.dataset.total + "개";
        }

        controls.replaceChildren();

        if (nav.dataset.prev) {
            controls.appendChild(makeLink("이전", Number(nav.dataset.prev), btnDefault + " px-3.5"));
        } else {
            controls.appendChild(makeSpan("이전", btnDisabled + " px-3.5"));
        }

        pageNumbers().forEach(function (item) {
            if (item.kind === "gap") {
                const gap = document.createElement("span");
                gap.className = "px-1 text-sm text-gray-400";
                gap.textContent = "…";
                controls.appendChild(gap);
                return;
            }

            if (item.number === current) {
                const currentSpan = makeSpan(String(item.number), btnActive);
                currentSpan.setAttribute("aria-current", "page");
                controls.appendChild(currentSpan);
                return;
            }

            controls.appendChild(makeLink(String(item.number), item.number, btnDefault + " min-w-10"));
        });

        if (nav.dataset.next) {
            controls.appendChild(makeLink("다음", Number(nav.dataset.next), btnDefault + " px-3.5"));
        } else {
            controls.appendChild(makeSpan("다음", btnDisabled + " px-3.5"));
        }
    }

    window.LGSearchPage = window.LGSearchPage || {};
    window.LGSearchPage.initPagination = initPagination;
})();
