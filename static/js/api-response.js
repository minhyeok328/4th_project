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

    // REFACTOR (ApiResponse 적용 범위 확대): FormData POST 등 향후 폼 AJAX가 동일 헤더·credentials 정책을 쓰도록 공통 init 생성
    function buildFormPostInit(options) {
        const opts = options || {};
        const init = {
            method: "POST",
            credentials: "same-origin",
        };
        if (opts.csrfToken) {
            init.headers = {
                "X-CSRFToken": opts.csrfToken,
            };
        }
        if (opts.body !== undefined) {
            init.body = opts.body;
        }
        return init;
    }

    // REFACTOR (ApiResponse 적용 범위 확대): JSON POST(챗봇·향후 REST AJAX)용 init을 한곳에서 조립해 요청 형식 통일
    function buildJsonPostInit(options) {
        const opts = options || {};
        const headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        };
        if (opts.csrfToken) {
            headers["X-CSRFToken"] = opts.csrfToken;
        }
        return {
            method: "POST",
            credentials: "same-origin",
            headers: headers,
            body: opts.body,
        };
    }

    // REFACTOR (ApiResponse 적용 범위 확대): fetch + parseFetchJsonResponse + 네트워크 실패를 동일 result 형태로 반환
    function fetchJson(url, init, options) {
        const opts = options || {};
        const logContext = opts.logContext || "API 요청 오류:";

        return fetch(url, init)
            .then(function (response) {
                return parseFetchJsonResponse(response, {
                    loginUrl: opts.loginUrl || "",
                });
            })
            .catch(function (error) {
                logApiError(logContext, error);
                return {
                    ok: false,
                    status: 0,
                    data: null,
                    error: ERROR_CODES.NETWORK,
                };
            });
    }

    // REFACTOR (ApiResponse 적용 범위 확대): 화면별 alert 정책만 옵션으로 두고 HTTP·파싱·네트워크 실패 문구를 공통 매핑
    function notifyJsonFetchError(result, options) {
        const opts = options || {};
        if (!result || opts.silent) {
            return;
        }

        if (result.error === ERROR_CODES.NETWORK) {
            notifyApiError(opts.networkMessage || "NETWORK", opts);
            return;
        }

        if (!result.ok) {
            notifyApiError(
                result.error === ERROR_CODES.PARSE
                    ? opts.parseMessage || "PARSE"
                    : opts.serverMessage || "SERVER_SHORT",
                opts
            );
        }
    }

    window.ApiResponse = {
        MESSAGES: MESSAGES,
        ERROR_CODES: ERROR_CODES,
        notifyApiError: notifyApiError,
        getErrorMessage: getErrorMessage,
        parseFetchJsonResponse: parseFetchJsonResponse,
        logApiError: logApiError,
        buildFormPostInit: buildFormPostInit,
        buildJsonPostInit: buildJsonPostInit,
        fetchJson: fetchJson,
        notifyJsonFetchError: notifyJsonFetchError,
    };
})();
