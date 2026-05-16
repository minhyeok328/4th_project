(function () {
    "use strict";

    const panels = document.querySelectorAll(".auth-panel");
    const modeButtons = document.querySelectorAll("[data-auth-mode]");

    function showPanel(mode) {
        panels.forEach(function (panel) {
            panel.classList.add("hidden");
        });

        const target = document.getElementById("auth-panel-" + mode);
        if (target) {
            target.classList.remove("hidden");
        }
    }

    modeButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const mode = button.getAttribute("data-auth-mode");
            if (mode) {
                showPanel(mode);
            }
        });
    });
})();
