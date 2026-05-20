/**
 * 상품 상세 페이지 UI 스크립트.
 *
 * 역할: 탭 전환(스펙·리뷰 등 패널 표시)과 뒤로가기 버튼 동작.
 * 찜 토글은 `wishlist-toggle.js`의 `productPageWishlistToggle`이 담당한다.
 *
 * DOM: `data-product-tab`, `#product-tab-*`, `#product-back-button`
 * 서버 요청 없음 — 클릭 시 클래스 토글과 history API만 사용.
 */
(function () {
    "use strict";

    const tabButtons = document.querySelectorAll("[data-product-tab]");
    const tabPanels = document.querySelectorAll(".product-tab-panel");
    const backButton = document.getElementById("product-back-button");

    /**
     * 지정 탭 id에 맞는 패널만 보이게 하고 탭 버튼 스타일을 갱신한다.
     * @param {string} tabId - `data-product-tab` 값과 `#product-tab-{id}` 접미사
     */
    function setActiveTab(tabId) {
        // 모든 패널 숨김 후 대상 패널만 표시
        tabPanels.forEach(function (panel) {
            panel.classList.add("hidden");
        });

        tabButtons.forEach(function (button) {
            const isActive = button.getAttribute("data-product-tab") === tabId;
            button.classList.toggle("text-red-600", isActive);
            button.classList.toggle("text-gray-900", !isActive);
            button.classList.toggle("hover:bg-gray-50", !isActive);
        });

        const panel = document.getElementById("product-tab-" + tabId);
        if (panel) {
            panel.classList.remove("hidden");
        }
    }

    tabButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const tabId = button.getAttribute("data-product-tab");
            if (tabId) {
                setActiveTab(tabId);
            }
        });
    });

    // 이전 페이지가 있으면 history.back, 직접 진입 시 목록 URL로 이동
    if (backButton) {
        backButton.addEventListener("click", function () {
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = "/products/";
            }
        });
    }
})();
