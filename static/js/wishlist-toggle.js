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

        return fetch(postUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
            },
            body: formData,
        })
            .then(function (response) {
                // REFACTOR (API 실패 UX 표준화): 찜 API 응답 파싱을 공통 유틸로 통일
                return ApiResponse.parseFetchJsonResponse(response, {
                    loginUrl: loginUrl,
                });
            })
            .then(function (result) {
                if (!result) {
                    return;
                }

                if (!result.ok || !result.data || !result.data.ok) {
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
            .catch(function (error) {
                ApiResponse.logApiError("찜 연동 에러:", error);
                ApiResponse.notifyApiError("WISHLIST");
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

                if (document.querySelectorAll(".grid > .group").length === 0) {
                    location.reload();
                }
            },
        });
    };
})();
