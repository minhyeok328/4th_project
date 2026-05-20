/**
 * 로그인·회원가입 통합 인증 페이지 스크립트.
 *
 * 역할:
 * - 로그인/회원가입 패널 전환(탭 버튼 → 패널 표시)
 * - 로그인 폼 제출 전 클라이언트 검증(HTML5 required 보완)
 *
 * 외부 연결: 폼은 Django `POST`로 제출 — 이 스크립트는 `preventDefault` 없이 검증만 수행.
 * DOM: `.auth-panel`, `[data-auth-mode]`, `#auth-panel-login`
 */
(function () {
    "use strict";

    const USERNAME_MAX_LENGTH = 150;
    const USERNAME_PATTERN = /^[\w.@+-]+$/;

    const panels = document.querySelectorAll(".auth-panel");
    const modeButtons = document.querySelectorAll("[data-auth-mode]");

    /**
     * 로그인 폼에 submit 리스너를 붙여 아이디·비밀번호 규칙을 검사한다.
     * 실패 시 `setCustomValidity` + `reportValidity`로 브라우저 기본 UI를 띄우고 제출을 막는다.
     */
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

        // 제출 직전: trim·길이·패턴·비밀번호 존재 검사 — 실패 시 preventDefault
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

    /**
     * 인증 모드(로그인/회원가입 등)에 해당하는 패널만 노출한다.
     * @param {string} mode - `#auth-panel-{mode}` 접미사
     */
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
