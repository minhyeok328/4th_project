/**
 * AI 챗봇 대화 페이지 클라이언트 스크립트.
 *
 * 역할:
 * - 서버 렌더 메시지 복원 → in-memory 배열 → 말풍선 DOM 갱신
 * - 사용자·추천 질문 전송 → Django JSON API → assistant 응답(마크다운+tail) 표시
 * - 새 대화 시 사이드바 목록·`chat_id` URL 동기화(history.replaceState)
 *
 * 외부 연결:
 * - `#chat-input-form` data-send-chat-url, data-csrf-token, data-chatpage-url, data-chat-id
 * - `ApiResponse.fetchJson` + `buildJsonPostInit` (LLM 응답은 서버에서 생성)
 * - XSS: `renderMarkdown` → `sanitizeChatHtml` (허용 태그·http(s) URL만)
 *
 * 실행 순서: IIFE 1회 → hydrateServerMessages → updateView → submit/추천질문 → sendMessage
 */
(function () {
    "use strict";

    // FIX (중복 복사 해결): 스크립트가 중복 실행되면 이벤트가 중복 바인딩되어 동일 메시지가 2회 생성될 수 있으므로 1회만 초기화
    if (window.__lgChatPageInitialized) {
        return;
    }
    window.__lgChatPageInitialized = true;

    // 클라이언트 메시지 상태 — 서버 HTML과 병합 후 여기서만 렌더 소스로 사용
    /** @type {{ id: number, role: "user" | "assistant", content: string, tail?: string, pending?: boolean }[]} */
    const messages = [];
    let messageId = 0;
    let inFlight = false;
    let pendingDotsTimer = null;

    const PENDING_REPLY_BASE = "답변을 작성 중입니다";
    const PENDING_REPLY_DOTS = [".", "..", "...", "."];

    const recommended = document.getElementById("chat-recommended");
    const messagesPanel = document.getElementById("chat-messages");
    const messagesList = document.getElementById("chat-messages-list");
    const inputForm = document.getElementById("chat-input-form");
    const inputField = document.getElementById("chat-input-field");
    const inputSubmit = document.getElementById("chat-input-submit");
    const sidebarOverlay = document.getElementById("chat-sidebar-overlay");
    const sidebarBackdrop = document.querySelector("[data-chat-sidebar-backdrop]");
    const sidebarOpenBtn = document.getElementById("chat-sidebar-open");
    const sidebarCloseBtn = document.getElementById("chat-sidebar-close");
    const mobileMedia = window.matchMedia("(max-width: 767px)");
    const recommendedButtons = document.querySelectorAll("[data-recommended-question]");

    /** 폼 data-*에서 전송 URL·CSRF·채팅방 페이지 URL·현재 chat_id를 읽는다 */
    function getConfig() {
        if (!inputForm) {
            return { sendUrl: "", csrf: "", chatpageUrl: "", chatId: "" };
        }
        return {
            sendUrl: inputForm.dataset.sendChatUrl || "",
            csrf: inputForm.dataset.csrfToken || "",
            chatpageUrl: inputForm.dataset.chatpageUrl || "",
            chatId: inputForm.dataset.chatId || "",
        };
    }

    /**
     * 활성 대화 id를 폼 dataset과 브라우저 URL(?chat_id=)에 반영한다.
     * 새로고침·공유 시 동일 대화를 열 수 있게 history.replaceState 사용.
     */
    function setChatId(newId) {
        if (!inputForm) {
            return;
        }

        const idStr = newId ? String(newId) : "";
        inputForm.dataset.chatId = idStr;

        const { chatpageUrl } = getConfig();
        if (!chatpageUrl || !window.history || !window.history.replaceState) {
            return;
        }

        const target = idStr
            ? chatpageUrl + "?chat_id=" + encodeURIComponent(idStr)
            : chatpageUrl;
        window.history.replaceState({}, "", target);
    }

    /**
     * 첫 메시지로 새 대화가 생성되면 사이드바에 방 링크·삭제 폼을 DOM으로 삽입한다.
     * 서버 전체 리렌더 없이 목록만 갱신하기 위함.
     */
    function insertSidebarRoom(chatId, name) {
        if (!chatId) {
            return;
        }

        const config = getConfig();
        const chatpageUrl = config.chatpageUrl;
        if (!chatpageUrl) {
            return;
        }

        const idAttr = "chat_id=" + chatId;
        const displayName = (name || "새 대화").trim() || "새 대화";

        document.querySelectorAll("aside").forEach(function (aside) {
            const listContainer = aside.querySelector(".space-y-2");
            if (!listContainer) {
                return;
            }

            listContainer.querySelectorAll("p").forEach(function (p) {
                if (p.textContent && p.textContent.indexOf("저장된 대화가 없습니다") !== -1) {
                    p.remove();
                }
            });

            if (listContainer.querySelector('a[href*="' + idAttr + '"]')) {
                return;
            }

            listContainer.querySelectorAll("a").forEach(function (a) {
                a.classList.remove("border-red-200", "bg-red-50/40", "text-gray-900");
            });

            const wrap = document.createElement("div");
            wrap.className = "group flex items-stretch gap-2";

            const link = document.createElement("a");
            link.href = chatpageUrl + "?chat_id=" + encodeURIComponent(chatId);
            link.className =
                "flex-1 truncate rounded-2xl border border-red-200 bg-red-50/40 px-4 py-3 text-left text-sm text-gray-900 transition-all duration-200 hover:border-gray-200 hover:bg-gray-50 hover:shadow-sm";
            link.textContent = displayName;

            const form = document.createElement("form");
            form.method = "post";
            form.action = chatpageUrl;
            form.className = "flex";
            form.setAttribute("onsubmit", "return confirm('이 대화를 삭제할까요?');");

            const csrfInput = document.createElement("input");
            csrfInput.type = "hidden";
            csrfInput.name = "csrfmiddlewaretoken";
            csrfInput.value = config.csrf || "";

            const idInput = document.createElement("input");
            idInput.type = "hidden";
            idInput.name = "delete_id";
            idInput.value = String(chatId);

            const btn = document.createElement("button");
            btn.type = "submit";
            btn.className =
                "rounded-2xl border border-gray-100 px-3 text-sm font-semibold text-gray-400 transition-all duration-200 hover:border-red-200 hover:bg-red-50 hover:text-red-600";
            btn.title = "대화 삭제";
            btn.setAttribute("aria-label", "대화 삭제");
            btn.textContent = "×";

            form.appendChild(csrfInput);
            form.appendChild(idInput);
            form.appendChild(btn);

            wrap.appendChild(link);
            wrap.appendChild(form);

            listContainer.insertBefore(wrap, listContainer.firstChild);
        });
    }

    /** SSR로 내려온 `[data-server-message]`를 messages 배열로 옮긴다(초기 1회) */
    function hydrateServerMessages() {
        if (!messagesList) {
            return;
        }

        messagesList.querySelectorAll("[data-server-message]").forEach(function (el) {
            const rawRole = el.getAttribute("data-role");
            const role = rawRole === "user" ? "user" : "assistant";
            const content = el.textContent.trim();
            if (!content) {
                return;
            }
            messages.push({
                id: messageId,
                role: role,
                content: content,
            });
            messageId += 1;
        });
    }

    /** 텍스트 노드 경유로 HTML 이스케이프 — 마크다운 전처리용 */
    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value;
        return div.innerHTML;
    }

    const LINK_CLASS = "font-semibold text-red-600 underline hover:text-red-700";
    const CHAT_IMG_CLASS =
        "my-3 block w-full max-h-64 max-w-full rounded-xl border border-gray-200/70 bg-gray-50 object-contain object-center p-2";

    const IMAGE_EXT_RE = /\.(png|jpe?g|gif|webp|bmp|svg|avif)(\?[^\s#]*)?$/i;
    const LGE_IMAGE_PATH_RE = /\/kr\/images\//i;

    /**
     * 확장자 또는 LG 이미지 경로 패턴으로 이미지 URL 여부를 판별한다.
     * 링크 대신 인라인 img로 렌더할지 결정하는 데 사용.
     */
    // REFACTOR (AI 대화 이미지): URL이 이미지인지 판별 — 마크다운·자동링크를 공통 <img>로 통일
    function isImageUrl(url) {
        if (!isSafeHttpUrl(url)) {
            return false;
        }

        try {
            const parsed = new URL(url.trim(), window.location.href);
            const pathQuery = parsed.pathname + parsed.search;
            if (IMAGE_EXT_RE.test(pathQuery)) {
                return true;
            }
            if (
                parsed.hostname.endsWith("lge.co.kr") &&
                LGE_IMAGE_PATH_RE.test(parsed.pathname)
            ) {
                return true;
            }
            return false;
        } catch (_err) {
            return false;
        }
    }

    /** 안전 URL 전제 하 챗용 img 태그 HTML 문자열 생성 */
    function buildChatImageHtml(url, alt) {
        const safeAlt = (alt || "상품 이미지").trim() || "상품 이미지";
        return (
            '<img src="' + url.trim() + '" alt="' + safeAlt +
            '" class="' + CHAT_IMG_CLASS + '" loading="lazy">'
        );
    }

    // REFACTOR (챗봇 URL 보안): javascript:/data: 등 위험 스킴 차단 — http·https만 링크/이미지에 허용
    function isSafeHttpUrl(url) {
        if (!url || typeof url !== "string") {
            return false;
        }

        const trimmed = url.trim();
        if (!trimmed) {
            return false;
        }

        const schemeMatch = trimmed.match(/^([a-z][a-z0-9+.-]*):/i);
        if (schemeMatch) {
            const scheme = schemeMatch[1].toLowerCase();
            if (scheme !== "http" && scheme !== "https") {
                return false;
            }
        }

        try {
            const parsed = new URL(trimmed, window.location.href);
            return parsed.protocol === "http:" || parsed.protocol === "https:";
        } catch (_err) {
            return false;
        }
    }

    /**
     * LLM·마크다운 치환 HTML을 DOMParser로 파싱 후 화이트리스트 태그·클래스·URL만 허용한다.
     * javascript:/data: 등 비안전 링크·이미지는 제거 또는 텍스트로 대체.
     */
    // REFACTOR (챗봇 URL 보안): 렌더 결과에서 허용 태그·속성만 남기고 이벤트 핸들러·위험 URL 제거
    function sanitizeChatHtml(html) {
        if (!html) {
            return "";
        }

        const doc = new DOMParser().parseFromString(
            '<div id="chat-md-sanitize-root">' + html + "</div>",
            "text/html"
        );
        const root = doc.getElementById("chat-md-sanitize-root");
        if (!root) {
            return "";
        }

        const ALLOWED_TAGS = new Set([
            "A",
            "STRONG",
            "EM",
            "OL",
            "UL",
            "LI",
            "IMG",
            "BR",
            "DIV",
        ]);

        const LIST_CLASS =
            "my-2 list-decimal space-y-1 pl-5";
        const NESTED_UL_CLASS = "my-2 list-disc space-y-1 pl-4";
        const UL_CLASS = "my-2 list-disc space-y-1 pl-5";
        const TAIL_DIV_CLASS =
            "mt-3 border-t border-gray-200 pt-3 text-xs leading-relaxed text-gray-600";
        const IMG_CLASS = CHAT_IMG_CLASS;

        function allowedClass(tagName, className) {
            if (!className) {
                return tagName === "BR";
            }
            if (tagName === "A") {
                return className === LINK_CLASS;
            }
            if (tagName === "IMG") {
                return className === IMG_CLASS;
            }
            if (tagName === "OL") {
                return className === LIST_CLASS;
            }
            if (tagName === "UL") {
                return className === NESTED_UL_CLASS || className === UL_CLASS;
            }
            if (tagName === "DIV") {
                return className === TAIL_DIV_CLASS;
            }
            return tagName === "LI" || tagName === "STRONG" || tagName === "EM";
        }

        function scrubElement(el) {
            const nodes = Array.from(el.childNodes);
            for (let i = 0; i < nodes.length; i++) {
                const node = nodes[i];
                if (node.nodeType === Node.TEXT_NODE) {
                    continue;
                }
                if (node.nodeType !== Node.ELEMENT_NODE) {
                    node.remove();
                    continue;
                }

                const tag = node.tagName;
                if (!ALLOWED_TAGS.has(tag)) {
                    const text = doc.createTextNode(node.textContent || "");
                    node.replaceWith(text);
                    continue;
                }

                const savedHref = tag === "A" ? node.getAttribute("href") : null;
                const savedSrc = tag === "IMG" ? node.getAttribute("src") : null;
                const savedAlt = tag === "IMG" ? node.getAttribute("alt") : null;
                const savedClass = node.getAttribute("class");

                Array.from(node.attributes).forEach(function (attr) {
                    node.removeAttribute(attr.name);
                });

                if (tag === "A") {
                    if (isSafeHttpUrl(savedHref || "")) {
                        node.setAttribute("href", savedHref.trim());
                        node.setAttribute("target", "_blank");
                        node.setAttribute("rel", "noopener");
                        node.setAttribute("class", LINK_CLASS);
                    } else {
                        const plain = doc.createTextNode(node.textContent || "");
                        node.replaceWith(plain);
                        continue;
                    }
                } else if (tag === "IMG") {
                    if (isSafeHttpUrl(savedSrc || "")) {
                        node.setAttribute("src", savedSrc.trim());
                        node.setAttribute("alt", savedAlt || "");
                        node.setAttribute("class", IMG_CLASS);
                        node.setAttribute("loading", "lazy");
                    } else {
                        node.remove();
                        continue;
                    }
                } else if (tag === "BR") {
                    // no attributes
                } else if (allowedClass(tag, savedClass)) {
                    if (savedClass) {
                        node.setAttribute("class", savedClass);
                    }
                }

                scrubElement(node);
            }
        }

        scrubElement(root);
        return root.innerHTML;
    }

    /**
     * 제한된 마크다운(굵게·기울임·목록·링크·이미지)을 HTML로 변환 후 sanitize한다.
     * assistant 말풍선 본문·tail 모두 이 경로를 탄다.
     */
    function renderMarkdown(text) {
        if (!text) {
            return "";
        }

        let s = escapeHtml(String(text));

        // REFACTOR (챗봇 URL 보안 + AI 대화 이미지): 마크다운 이미지를 공통 스타일로 인라인 표시
        s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, function (_m, alt, url) {
            if (isSafeHttpUrl(url)) {
                return buildChatImageHtml(url, alt);
            }
            return "![" + alt + "](" + url + ")";
        });

        // REFACTOR (챗봇 URL 보안 + AI 대화 이미지): 이미지 URL 링크는 <a> 대신 <img>로 바로 렌더
        s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (_m, label, url) {
            if (isSafeHttpUrl(url)) {
                if (isImageUrl(url)) {
                    return buildChatImageHtml(url, label);
                }
                return (
                    '<a href="' + url + '" target="_blank" rel="noopener" class="' +
                    LINK_CLASS + '">' + label + "</a>"
                );
            }
            return "[" + label + "](" + url + ")";
        });

        // bold: **text**
        s = s.replace(/\*\*([^*\n]+?)\*\*/g, "<strong>$1</strong>");

        // italic: *text*
        s = s.replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, "$1<em>$2</em>");

        // REFACTOR (챗봇 URL 보안 + AI 대화 이미지): 노출된 이미지 URL은 링크가 아닌 인라인 이미지로 표시
        s = s.replace(/(^|[\s(])(https?:\/\/[^\s)<]+)/g, function (_m, lead, url) {
            if (!isSafeHttpUrl(url)) {
                return lead + url;
            }
            if (isImageUrl(url)) {
                return lead + buildChatImageHtml(url, "");
            }
            return (
                lead + '<a href="' + url + '" target="_blank" rel="noopener" class="' +
                LINK_CLASS + '">' + url + "</a>"
            );
        });

        // 줄 단위로 ordered/unordered 목록 태그를 열고 닫으며 HTML 조각 배열 생성
        const lines = s.split("\n");
        const out = [];
        let olOpen = false;
        let olLiOpen = false;
        let nestedUlOpen = false;
        let ulOpen = false;

        function closeNestedUl() {
            if (nestedUlOpen) {
                out.push("</ul>");
                nestedUlOpen = false;
            }
        }

        function closeOlLi() {
            closeNestedUl();
            if (olLiOpen) {
                out.push("</li>");
                olLiOpen = false;
            }
        }

        function closeOl() {
            closeOlLi();
            if (olOpen) {
                out.push("</ol>");
                olOpen = false;
            }
        }

        function closeStandaloneUl() {
            if (ulOpen) {
                out.push("</ul>");
                ulOpen = false;
            }
        }

        function closeAllLists() {
            closeStandaloneUl();
            closeOl();
        }

        for (let i = 0; i < lines.length; i++) {
            const raw = lines[i];
            const olM = raw.match(/^\s*\d+\.\s+(.*)$/);
            const ulM = raw.match(/^\s*[-*]\s+(.*)$/);

            if (olM) {
                closeStandaloneUl();
                closeOlLi();
                if (!olOpen) {
                    out.push('<ol class="my-2 list-decimal space-y-1 pl-5">');
                    olOpen = true;
                }
                out.push("<li>" + olM[1]);
                olLiOpen = true;
            } else if (ulM) {
                if (olLiOpen) {
                    if (!nestedUlOpen) {
                        out.push('<ul class="my-2 list-disc space-y-1 pl-4">');
                        nestedUlOpen = true;
                    }
                    out.push("<li>" + ulM[1] + "</li>");
                } else {
                    closeOl();
                    if (!ulOpen) {
                        out.push('<ul class="my-2 list-disc space-y-1 pl-5">');
                        ulOpen = true;
                    }
                    out.push("<li>" + ulM[1] + "</li>");
                }
            } else {
                const trimmed = raw.trim();
                if (trimmed === "") {
                    out.push("");
                    continue;
                }
                closeAllLists();
                out.push(raw);
            }
        }
        closeAllLists();

        let html = "";
        for (let j = 0; j < out.length; j++) {
            const part = out[j];
            if (!part) {
                html += "<br>";
                continue;
            }
            if (/^<\/?(ol|ul|li|img|p|h\d|blockquote)\b/i.test(part)) {
                html += part;
            } else {
                const isLast = j === out.length - 1;
                html += part + (isLast ? "" : "<br>");
            }
        }
        // REFACTOR (챗봇 URL 보안): 마크다운 치환 후 DOM sanitizer로 잔여 위험 태그·속성 제거
        return sanitizeChatHtml(html);
    }

    /** messages 배열 전체를 말풍선 DOM으로 다시 그리고 패널을 맨 아래로 스크롤 */
    function renderMessages() {
        if (!messagesList) {
            return;
        }

        messagesList.innerHTML = "";

        messages.forEach(function (message) {
            const bubble = document.createElement("div");

            if (message.role === "user") {
                bubble.className =
                    "ml-auto max-w-[70%] whitespace-pre-wrap break-words rounded-2xl bg-red-600 px-5 py-4 text-white";
                bubble.textContent = message.content;
            } else {
                bubble.className =
                    "max-w-[80%] break-words rounded-2xl bg-gray-100 px-5 py-4 text-sm leading-relaxed text-gray-900" +
                    (message.pending ? " opacity-70" : "");

                let html = renderMarkdown(message.content);

                if (message.tail) {
                    html +=
                        '<div class="mt-3 border-t border-gray-200 pt-3 text-xs leading-relaxed text-gray-600">' +
                        renderMarkdown(message.tail) +
                        "</div>";
                }

                bubble.innerHTML = html;
            }

            messagesList.appendChild(bubble);
        });

        if (messagesPanel) {
            messagesPanel.scrollTop = messagesPanel.scrollHeight;
        }
    }

    /** 메시지 유무에 따라 추천 질문 영역·대화 패널 표시를 전환하고 필요 시 renderMessages 호출 */
    function updateView() {
        const hasMessages = messages.length > 0;

        if (recommended) {
            recommended.classList.toggle("hidden", hasMessages);
            recommended.classList.toggle("flex", !hasMessages);
        }

        if (messagesPanel) {
            messagesPanel.classList.toggle("hidden", !hasMessages);
            messagesPanel.classList.toggle("block", hasMessages);
        }

        if (hasMessages) {
            renderMessages();
        }
    }

    /** API 요청 중 입력·전송 버튼 비활성화(inFlight와 연동) */
    function setBusy(isBusy) {
        inFlight = isBusy;
        if (inputField) {
            inputField.disabled = isBusy;
        }
        if (inputSubmit) {
            inputSubmit.disabled = isBusy;
        }
    }

    function stopPendingDotsAnimation() {
        if (pendingDotsTimer !== null) {
            clearInterval(pendingDotsTimer);
            pendingDotsTimer = null;
        }
    }

    /** assistant placeholder 말풍선에 "답변 작성 중..." 점 애니메이션 적용 */
    function startPendingDotsAnimation(placeholderMsg) {
        stopPendingDotsAnimation();

        let step = 0;
        placeholderMsg.content = PENDING_REPLY_BASE + PENDING_REPLY_DOTS[0];

        pendingDotsTimer = setInterval(function () {
            if (messages.indexOf(placeholderMsg) === -1) {
                stopPendingDotsAnimation();
                return;
            }

            step = (step + 1) % PENDING_REPLY_DOTS.length;
            placeholderMsg.content = PENDING_REPLY_BASE + PENDING_REPLY_DOTS[step];
            renderMessages();
        }, 450);
    }

    /** messages에 한 건 추가하고 객체 참조를 반환(placeholder 애니메이션용) */
    function appendMessage(role, content, tail, pending) {
        messageId += 1;
        const msg = {
            id: Date.now() + messageId,
            role: role,
            content: content,
        };
        if (tail) {
            msg.tail = tail;
        }
        if (pending) {
            msg.pending = true;
        }
        messages.push(msg);
        return msg;
    }

    /**
     * 사용자 메시지를 로컬에 추가한 뒤 챗 API로 전송하고 응답을 assistant 말풍선으로 반영한다.
     * 새 대화(wasNew)이면 사이드바·chat_id URL을 갱신한다.
     */
    async function sendMessage(content) {
        const trimmed = (content || "").trim();
        if (!trimmed || inFlight) {
            return;
        }

        const config = getConfig();
        if (!config.sendUrl || !config.csrf) {
            return;
        }

        appendMessage("user", trimmed);
        updateView();
        setBusy(true);

        const placeholder = appendMessage("assistant", PENDING_REPLY_BASE + ".", "", true);
        renderMessages();
        startPendingDotsAnimation(placeholder);

        let payloadChatId = null;
        if (config.chatId) {
            const parsed = Number(config.chatId);
            if (!Number.isNaN(parsed) && parsed > 0) {
                payloadChatId = parsed;
            }
        }

        const wasNew = payloadChatId === null;

        try {
            // REFACTOR (ApiResponse 적용 범위 확대): fetch·JSON POST init·응답 파싱을 fetchJson 한 경로로 통일(말풍선 표시는 기존 유지)
            const parsed = await ApiResponse.fetchJson(
                config.sendUrl,
                ApiResponse.buildJsonPostInit({
                    csrfToken: config.csrf,
                    body: JSON.stringify({
                        chat_id: payloadChatId,
                        user_input: trimmed,
                    }),
                }),
                { logContext: "챗봇 전송 오류:" }
            );

            const idx = messages.indexOf(placeholder);
            if (idx !== -1) {
                messages.splice(idx, 1);
            }

            if (!parsed) {
                updateView();
                return;
            }

            if (!parsed.ok || !parsed.data) {
                appendMessage(
                    "assistant",
                    ApiResponse.getErrorMessage(
                        parsed.error,
                        ApiResponse.MESSAGES.SERVER
                    )
                );
                updateView();
                return;
            }

            const data = parsed.data;
            const reply = typeof data.response === "string" ? data.response : "";
            const tail = typeof data.response_tail === "string" ? data.response_tail : "";

            appendMessage(
                "assistant",
                reply || ApiResponse.MESSAGES.CHAT_EMPTY,
                tail
            );
            updateView();

            if (data.chat_id) {
                if (wasNew) {
                    insertSidebarRoom(
                        data.chat_id,
                        data.chatroom_name || trimmed.slice(0, 30)
                    );
                }
                setChatId(data.chat_id);
            }
        } catch (err) {
            const idx = messages.indexOf(placeholder);
            if (idx !== -1) {
                messages.splice(idx, 1);
            }
            // REFACTOR (ApiResponse 적용 범위 확대): fetchJson이 처리하지 않는 예외만 fallback 로그·말풍선 표시
            ApiResponse.logApiError("챗봇 전송 오류:", err);
            appendMessage(
                "assistant",
                ApiResponse.getErrorMessage(ApiResponse.ERROR_CODES.NETWORK)
            );
            updateView();
        } finally {
            stopPendingDotsAnimation();
            setBusy(false);
            if (inputField) {
                inputField.focus();
            }
        }
    }

    /** 모바일 대화 목록 오버레이 열기 — body 스크롤 잠금 */
    function openSidebar() {
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove("hidden");
            sidebarOverlay.setAttribute("aria-hidden", "false");
        }
        // REFACTOR (모바일 화면): 사이드바 열림 시 배경 스크롤 잠금으로 터치 스크롤 간섭 방지
        document.body.classList.add("overflow-hidden");
        if (sidebarOpenBtn) {
            sidebarOpenBtn.setAttribute("aria-expanded", "true");
        }
    }

    function closeSidebar() {
        if (sidebarOverlay) {
            sidebarOverlay.classList.add("hidden");
            sidebarOverlay.setAttribute("aria-hidden", "true");
        }
        document.body.classList.remove("overflow-hidden");
        if (sidebarOpenBtn) {
            sidebarOpenBtn.setAttribute("aria-expanded", "false");
        }
    }

    // 이벤트: 폼 제출 → sendMessage, 추천 질문, 사이드바·ESC·모바일 입력 포커스
    if (inputForm && inputField) {
        inputForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const value = inputField.value;
            inputField.value = "";
            sendMessage(value);
        });
    }

    recommendedButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const question = button.getAttribute("data-recommended-question");
            if (question) {
                sendMessage(question);
            }
        });
    });

    if (sidebarOpenBtn) {
        sidebarOpenBtn.addEventListener("click", openSidebar);
    }

    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener("click", closeSidebar);
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", closeSidebar);
    }

    // REFACTOR (모바일 화면): ESC·배경 탭으로 사이드바 닫기 — 터치·키보드 조작 모두 지원
    document.addEventListener("keydown", function (event) {
        if (
            event.key === "Escape" &&
            sidebarOverlay &&
            !sidebarOverlay.classList.contains("hidden")
        ) {
            closeSidebar();
        }
    });

    // REFACTOR (모바일 화면): 가상 키보드 표시 시 입력창이 가려지지 않도록 스크롤 보정
    if (inputField && mobileMedia.matches) {
        inputField.addEventListener("focus", function () {
            window.setTimeout(function () {
                inputField.scrollIntoView({ block: "nearest", behavior: "smooth" });
            }, 300);
        });
    }

    // 초기화 마무리: SSR 메시지 복원 후 화면 상태 동기화
    hydrateServerMessages();
    updateView();
})();
