(function () {
    "use strict";

    // REFACTOR (찜 기능 중복 실행 방지): 동일 product_code에 대한 동시 요청 차단
    const wishlistInFlight = new Set();

    // REFACTOR (찜 기능 중복 실행 방지): 요청 중 버튼 비활성화로 연속 클릭·중복 POST 방지
    function setWishlistButtonBusy(button, busy) {
        if (!button) {
            return;
        }
        button.disabled = busy;
        button.classList.toggle("opacity-60", busy);
        button.classList.toggle("cursor-not-allowed", busy);
        button.classList.toggle("pointer-events-none", busy);
        if (busy) {
            button.setAttribute("aria-busy", "true");
        } else {
            button.removeAttribute("aria-busy");
        }
    }

    function postToggleFavorite(options) {
        const button = options.button;
        const productCode = options.productCode;
        const postUrl = options.postUrl;
        const csrfToken = options.csrfToken;
        const loginUrl = options.loginUrl || "";
        const onSuccess = options.onSuccess;

        if (!productCode || !postUrl) {
            // REFACTOR (API 실패 UX 표준화): 입력 오류 메시지를 공통 정책에서 조회
            ApiResponse.notifyApiError("INVALID_INPUT");
            return Promise.resolve();
        }

        if (wishlistInFlight.has(productCode)) {
            return Promise.resolve();
        }

        wishlistInFlight.add(productCode);
        setWishlistButtonBusy(button, true);

        const formData = new FormData();
        formData.append("product_code", productCode);
        formData.append("action", "toggle_favorite");

        return ApiResponse.fetchJson(
            postUrl,
            ApiResponse.buildFormPostInit({
                body: formData,
                csrfToken: csrfToken,
            }),
            {
                loginUrl: loginUrl,
                logContext: "찜 연동 에러:",
            }
        )
            .then(function (result) {
                if (!result) {
                    return;
                }

                // REFACTOR (ApiResponse 적용 범위 확대): 네트워크 실패는 공통 fetchJson이 처리 — 찜 전용 문구는 기존과 동일하게 WISHLIST
                if (result.error === ApiResponse.ERROR_CODES.NETWORK) {
                    ApiResponse.notifyApiError("WISHLIST");
                    return;
                }

                if (!result.ok || !result.data || !result.data.ok) {
                    // REFACTOR (ApiResponse 적용 범위 확대): 본문 ok:false(HTTP 200)는 notifyJsonFetchError 대상이 아니므로 기존 문구 매핑 유지
                    ApiResponse.notifyApiError(
                        result.error === ApiResponse.ERROR_CODES.PARSE
                            ? "PARSE"
                            : "SERVER_SHORT"
                    );
                    return;
                }

                if (typeof onSuccess === "function") {
                    onSuccess(result.data, button);
                }
            })
            .finally(function () {
                wishlistInFlight.delete(productCode);
                setWishlistButtonBusy(button, false);
            });
    }

    function getWishlistConfigFromElement(root) {
        if (!root) {
            return { postUrl: "", csrfToken: "", loginUrl: "" };
        }
        return {
            postUrl: root.dataset.wishlistPostUrl || "",
            csrfToken: root.dataset.csrfToken || "",
            loginUrl: root.dataset.loginUrl || "",
        };
    }

    // REFACTOR (마이페이지 찜 카운트 동기화): 찜 해제로 카드만 제거될 때 서버 렌더 뱃지가 갱신되지 않으므로 남은 카드 수로 DOM 반영
    function syncMypageWishlistCount() {
        const section = document.getElementById("mypage-wishlist-section");
        if (!section) {
            return;
        }
        const badge = section.querySelector("[data-wishlist-count-badge]");
        if (!badge) {
            return;
        }
        const count = section.querySelectorAll(".grid > .group").length;
        badge.textContent = "총 " + count + "개";
    }

    function applyProductPageFavoriteUi(button, favorited) {
        if (favorited) {
            button.innerText = "찜 완료";
            button.classList.remove("bg-white", "text-red-600", "hover:bg-red-50");
            button.classList.add("bg-red-600", "text-white", "hover:bg-red-700");
            button.setAttribute("data-status", "done");
        } else {
            button.innerText = "찜하기";
            button.classList.remove("bg-red-600", "text-white", "hover:bg-red-700");
            button.classList.add("bg-white", "text-red-600", "hover:bg-red-50");
            button.setAttribute("data-status", "none");
        }
    }

    window.productPageWishlistToggle = function (button, productCode) {
        const section = document.getElementById("product-actions");
        if (!section || section.dataset.isAuthenticated !== "true") {
            const loginUrl = section ? section.dataset.loginUrl : "";
            if (loginUrl) {
                window.location.href = loginUrl;
            }
            return;
        }

        const config = getWishlistConfigFromElement(section);

        postToggleFavorite({
            button: button,
            productCode: productCode,
            postUrl: config.postUrl,
            csrfToken: config.csrfToken,
            loginUrl: config.loginUrl,
            onSuccess: function (data) {
                applyProductPageFavoriteUi(button, !!data.favorited);
            },
        });
    };

    window.mypageWishlistToggle = function (button, productCode) {
        const section = document.getElementById("mypage-wishlist-section");
        const config = getWishlistConfigFromElement(section);
        const productCard = button.closest(".group");

        postToggleFavorite({
            button: button,
            productCode: productCode,
            postUrl: config.postUrl,
            csrfToken: config.csrfToken,
            onSuccess: function () {
                if (productCard) {
                    productCard.remove();
                }

                // REFACTOR (마이페이지 찜 카운트 동기화): 카드 제거 직후 뱃지 문구를 남은 찜 개수와 일치시킴
                syncMypageWishlistCount();

                if (document.querySelectorAll(".grid > .group").length === 0) {
                    location.reload();
                }
            },
        });
    };
})();
