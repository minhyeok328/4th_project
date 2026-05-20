(function () {
    "use strict";

    // FIX (중복 복사 해결): 스크립트가 중복 실행되면 이벤트가 중복 바인딩되어 동일 메시지가 2회 생성될 수 있으므로 1회만 초기화
    if (window.__lgChatPageInitialized) {
        return;
    }
    window.__lgChatPageInitialized = true;

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
    const sidebarOpenBtn = document.getElementById("chat-sidebar-open");
    const sidebarCloseBtn = document.getElementById("chat-sidebar-close");
    const recommendedButtons = document.querySelectorAll("[data-recommended-question]");

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

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value;
        return div.innerHTML;
    }

    const LINK_CLASS = "font-semibold text-red-600 underline hover:text-red-700";

    function renderMarkdown(text) {
        if (!text) {
            return "";
        }

        let s = escapeHtml(String(text));

        // images: ![alt](url)
        s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, function (_m, alt, url) {
            return (
                '<img src="' + url + '" alt="' + alt +
                '" class="my-2 max-w-full rounded-lg" loading="lazy">'
            );
        });

        // inline link: [text](url)
        s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (_m, label, url) {
            return (
                '<a href="' + url + '" target="_blank" rel="noopener" class="' +
                LINK_CLASS + '">' + label + "</a>"
            );
        });

        // bold: **text**
        s = s.replace(/\*\*([^*\n]+?)\*\*/g, "<strong>$1</strong>");

        // italic: *text*
        s = s.replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, "$1<em>$2</em>");

        // raw URL autolink (only outside HTML attributes)
        s = s.replace(/(^|[\s(])(https?:\/\/[^\s)<]+)/g, function (_m, lead, url) {
            return (
                lead + '<a href="' + url + '" target="_blank" rel="noopener" class="' +
                LINK_CLASS + '">' + url + "</a>"
            );
        });

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
        return html;
    }

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
            const response = await fetch(config.sendUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": config.csrf,
                    "X-Requested-With": "XMLHttpRequest",
                },
                credentials: "same-origin",
                body: JSON.stringify({
                    chat_id: payloadChatId,
                    user_input: trimmed,
                }),
            });

            const idx = messages.indexOf(placeholder);
            if (idx !== -1) {
                messages.splice(idx, 1);
            }

            if (!response.ok) {
                appendMessage("assistant", "요청 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
                updateView();
                return;
            }

            const data = await response.json().catch(function () {
                return null;
            });

            if (!data) {
                appendMessage("assistant", "응답을 해석할 수 없습니다.");
                updateView();
                return;
            }

            const reply = typeof data.response === "string" ? data.response : "";
            const tail = typeof data.response_tail === "string" ? data.response_tail : "";

            appendMessage("assistant", reply || "답변을 생성하지 못했습니다.", tail);
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
            appendMessage("assistant", "네트워크 오류로 응답을 받지 못했습니다.");
            updateView();
        } finally {
            stopPendingDotsAnimation();
            setBusy(false);
            if (inputField) {
                inputField.focus();
            }
        }
    }

    function openSidebar() {
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove("hidden");
        }
    }

    function closeSidebar() {
        if (sidebarOverlay) {
            sidebarOverlay.classList.add("hidden");
        }
    }

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

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", function (event) {
            if (event.target === sidebarOverlay) {
                closeSidebar();
            }
        });
    }

    hydrateServerMessages();
    updateView();
})();
