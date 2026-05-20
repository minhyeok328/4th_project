(function () {
    "use strict";

    // REFACTOR (API 실패 UX 표준화): 화면별 메시지 문구를 한곳에서 관리해 실패 피드백 일관성 확보
    const MESSAGES = {
        NETWORK: "네트워크 오류로 응답을 받지 못했습니다.",
        SERVER: "요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        SERVER_SHORT: "서버 처리 중 오류가 발생했습니다.",
        PARSE: "응답을 해석할 수 없습니다.",
        WISHLIST: "찜 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        INVALID_INPUT: "상품 정보를 찾을 수 없습니다.",
        CHAT_EMPTY: "답변을 생성하지 못했습니다.",
    };

    const ERROR_CODES = {
        NETWORK: "NETWORK",
        SERVER: "SERVER",
        PARSE: "PARSE",
    };

    // REFACTOR (API 실패 UX 표준화): 기본은 alert — 챗봇 등 인라인 표시는 channel 옵션으로 분기
    function notifyApiError(messageOrCode, options) {
        const opts = options || {};
        if (opts.silent) {
            return;
        }

        const text =
            MESSAGES[messageOrCode] ||
            messageOrCode ||
            MESSAGES.SERVER;

        if (opts.channel === "inline") {
            return text;
        }

        alert(text);
    }

    function getErrorMessage(errorCode, fallbackMessage) {
        if (errorCode && MESSAGES[errorCode]) {
            return MESSAGES[errorCode];
        }
        if (fallbackMessage) {
            return fallbackMessage;
        }
        return MESSAGES.SERVER;
    }

    // REFACTOR (API 실패 UX 표준화): response.ok·content-type·JSON 파싱·리다이렉트를 공통 파싱
    function parseFetchJsonResponse(response, options) {
        const opts = options || {};
        const loginUrl = opts.loginUrl || "";

        if (response.redirected && loginUrl) {
            window.location.href = response.url || loginUrl;
            return Promise.resolve(null);
        }

        const contentType = response.headers.get("content-type") || "";
        const isJson = contentType.includes("application/json");

        if (!isJson) {
            if (loginUrl) {
                window.location.href = loginUrl;
                return Promise.resolve(null);
            }
            return Promise.resolve({
                ok: false,
                status: response.status,
                data: null,
                error: ERROR_CODES.PARSE,
            });
        }

        return response
            .json()
            .then(function (data) {
                return {
                    ok: response.ok,
                    status: response.status,
                    data: data,
                    error: response.ok ? null : ERROR_CODES.SERVER,
                };
            })
            .catch(function () {
                return {
                    ok: false,
                    status: response.status,
                    data: null,
                    error: ERROR_CODES.PARSE,
                };
            });
    }

    function logApiError(context, error) {
        console.error(context || "API 요청 오류:", error);
    }

    window.ApiResponse = {
        MESSAGES: MESSAGES,
        ERROR_CODES: ERROR_CODES,
        notifyApiError: notifyApiError,
        getErrorMessage: getErrorMessage,
        parseFetchJsonResponse: parseFetchJsonResponse,
        logApiError: logApiError,
    };
})();
