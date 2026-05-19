(function () {
    "use strict";

    const tabButtons = document.querySelectorAll("[data-product-tab]");
    const tabPanels = document.querySelectorAll(".product-tab-panel");
    const backButton = document.getElementById("product-back-button");

    function setActiveTab(tabId) {
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
