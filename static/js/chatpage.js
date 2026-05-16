(function () {
    "use strict";

    /** @type {{ id: number, role: "user" | "assistant", content: string }[]} */
    const messages = [];
    let messageId = 0;

    const recommended = document.getElementById("chat-recommended");
    const messagesPanel = document.getElementById("chat-messages");
    const messagesList = document.getElementById("chat-messages-list");
    const inputForm = document.getElementById("chat-input-form");
    const inputField = document.getElementById("chat-input-field");
    const sidebarOverlay = document.getElementById("chat-sidebar-overlay");
    const sidebarOpenBtn = document.getElementById("chat-sidebar-open");
    const sidebarCloseBtn = document.getElementById("chat-sidebar-close");
    const newChatButtons = document.querySelectorAll("[data-chat-new]");
    const recommendedButtons = document.querySelectorAll("[data-recommended-question]");

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

    function renderMessages() {
        if (!messagesList) {
            return;
        }

        messagesList.innerHTML = "";

        messages.forEach(function (message) {
            const bubble = document.createElement("div");
            bubble.textContent = message.content;

            if (message.role === "user") {
                bubble.className =
                    "ml-auto max-w-[70%] rounded-2xl bg-red-600 px-5 py-4 text-white";
            } else {
                bubble.className =
                    "max-w-[70%] rounded-2xl bg-gray-100 px-5 py-4 text-gray-900";
            }

            messagesList.appendChild(bubble);
        });

        messagesPanel.scrollTop = messagesPanel.scrollHeight;
    }

    function updateView() {
        const hasMessages = messages.length > 0;

        if (recommended) {
            recommended.classList.toggle("hidden", hasMessages);
            recommended.classList.toggle("flex", !hasMessages);
        }

        if (messagesPanel) {
            messagesPanel.classList.toggle("hidden", !hasMessages);
        }

        if (hasMessages) {
            renderMessages();
        }
    }

    function sendMessage(content) {
        const trimmed = content.trim();
        if (!trimmed) {
            return;
        }

        messages.push({
            id: Date.now(),
            role: "user",
            content: trimmed,
        });
        messageId += 1;

        updateView();

        /*
         * 나중에 여기서 AI API 호출
         *
         * fetch(...)
         *   .then(...)
         *   .then(function (data) {
         *     messages.push({
         *       id: Date.now(),
         *       role: "assistant",
         *       content: data.reply,
         *     });
         *     updateView();
         *   });
         */
    }

    function handleNewChat() {
        messages.length = 0;
        messageId = 0;
        if (window.history && window.history.replaceState) {
            window.history.replaceState({}, "", window.location.pathname);
        }
        updateView();
        closeSidebar();
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
            sendMessage(inputField.value);
            inputField.value = "";
        });
    }

    newChatButtons.forEach(function (button) {
        button.addEventListener("click", handleNewChat);
    });

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
