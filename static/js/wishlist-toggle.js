/**
 * 찜(즐겨찾기) 토글 공통 스크립트.
 *
 * 역할:
 * - 상품 상세·마이페이지에서 동일 API로 찜 on/off
 * - 중복 POST·연속 클릭 방지, 인증·에러 UX는 `ApiResponse`에 위임
 *
 * 외부 연결:
 * - `data-wishlist-post-url`, `data-csrf-token` (템플릿 data-*)
 * - POST FormData: product_code, action=toggle_favorite
 * - 전역: `window.productPageWishlistToggle`, `window.mypageWishlistToggle`
 */
(function () {
    "use strict";

    // REFACTOR (찜 기능 중복 실행 방지): 동일 product_code에 대한 동시 요청 차단
    const wishlistInFlight = new Set();

    /**
     * 찜 버튼 busy 상태 — 요청 중 재클릭·중복 POST를 막기 위한 시각·접근성 피드백.
     * @param {HTMLButtonElement|null} button
     * @param {boolean} busy
     */
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

    /**
     * 찜 토글 API를 호출하고 성공 시 `onSuccess` 콜백을 실행한다.
     * @param {Object} options - button, productCode, postUrl, csrfToken, loginUrl, onSuccess
     * @returns {Promise<void>}
     */
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

    /** 템플릿 루트 요소의 data-*에서 찜 API URL·CSRF·로그인 URL을 읽는다. */
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

    /**
     * 마이페이지 찜 섹션 뱃지 문구를 남은 카드 수와 맞춘다.
     * 서버 전체 리렌더 없이 카드 DOM만 제거될 때 카운트 불일치를 방지한다.
     */
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

    /** 상품 상세 찜 버튼 라벨·색상을 favorited 상태에 맞게 갱신한다. */
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

    /** 상품 상세: 미로그인 시 로그인 URL로 이동, 로그인 시 찜 토글 후 버튼 UI 갱신. */
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

    /** 마이페이지: 찜 해제 시 카드 제거·뱃지 동기화, 목록이 비면 전체 새로고침. */
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
