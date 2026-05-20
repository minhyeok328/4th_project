(function () {
    "use strict";

    const USERNAME_MAX_LENGTH = 150;
    const USERNAME_PATTERN = /^[\w.@+-]+$/;

    const panels = document.querySelectorAll(".auth-panel");
    const modeButtons = document.querySelectorAll("[data-auth-mode]");

    // REFACTOR (입력 검증): HTML5 required만으로는 공백·형식 오입력 방어가 부족해 제출 전 클라이언트 검증 추가
    function initLoginFormValidation() {
        const panel = document.getElementById("auth-panel-login");
        if (!panel) {
            return;
        }

        const form = panel.querySelector("form");
        if (!form) {
            return;
        }

        const usernameInput = form.querySelector('input[name="username"]');
        const passwordInput = form.querySelector('input[name="password"]');
        if (!usernameInput || !passwordInput) {
            return;
        }

        function clearFieldValidity() {
            usernameInput.setCustomValidity("");
            passwordInput.setCustomValidity("");
        }

        usernameInput.addEventListener("input", function () {
            usernameInput.setCustomValidity("");
        });
        passwordInput.addEventListener("input", function () {
            passwordInput.setCustomValidity("");
        });

        form.addEventListener("submit", function (event) {
            clearFieldValidity();

            const username = usernameInput.value.trim();
            const password = passwordInput.value;

            if (!username) {
                usernameInput.setCustomValidity("아이디를 입력해주세요.");
                usernameInput.reportValidity();
                event.preventDefault();
                return;
            }

            if (username.length > USERNAME_MAX_LENGTH) {
                usernameInput.setCustomValidity("아이디는 150자 이하여야 합니다.");
                usernameInput.reportValidity();
                event.preventDefault();
                return;
            }

            if (!USERNAME_PATTERN.test(username)) {
                usernameInput.setCustomValidity(
                    "아이디는 영문, 숫자 및 @ . + - _ 만 사용할 수 있습니다."
                );
                usernameInput.reportValidity();
                event.preventDefault();
                return;
            }

            if (!password) {
                passwordInput.setCustomValidity("비밀번호를 입력해주세요.");
                passwordInput.reportValidity();
                event.preventDefault();
                return;
            }

            usernameInput.value = username;
        });
    }

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

    initLoginFormValidation();
})();
