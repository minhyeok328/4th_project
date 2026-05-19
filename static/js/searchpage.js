(function () {
    function initSearchFilter() {
        const FILTER_LABELS = {
            name: "상품명",
            price__gte: "최소 가격",
            price__lte: "최대 가격",
            proficiency_level__gte: "난이도 최소",
            proficiency_level__lte: "난이도 최대",
            power_consum__gte: "소비전력 최소",
            power_consum__lte: "소비전력 최대",
            color: "색상",
            color__in: "색상",
            install_type: "설치 타입",
            cool_type: "냉각 방식",
            door_type: "도어 타입",
            door_cnt__gte: "도어 수 최소",
            door_cnt__lte: "도어 수 최대",
            total_cap__gte: "총 용량 최소",
            total_cap__lte: "총 용량 최대",
            refrige_cap__gte: "냉장 용량 최소",
            refrige_cap__lte: "냉장 용량 최대",
            freeze_cap__gte: "냉동 용량 최소",
            freeze_cap__lte: "냉동 용량 최대",
            smart_diag: "스마트 진단",
            ice_maker: "제빙기",
            cool_cap__gte: "냉방 능력 최소",
            cool_cap__lte: "냉방 능력 최대",
            coverage__gte: "적용 면적 최소",
            coverage__lte: "적용 면적 최대",
            wind_speed__gte: "풍속 최소",
            wind_speed__lte: "풍속 최대",
            dehumid__gte: "제습량 최소",
            dehumid__lte: "제습량 최대",
            voltage__gte: "전압 최소",
            voltage__lte: "전압 최대",
            hertz__gte: "주파수 최소",
            hertz__lte: "주파수 최대",
            resol_code: "해상도",
            display_type: "디스플레이",
            os_type: "OS",
            screen_size__gte: "화면 크기 최소",
            screen_size__lte: "화면 크기 최대",
            ref_rate__gte: "주사율 최소",
            ref_rate__lte: "주사율 최대",
            speaker_output__gte: "스피커 최소",
            speaker_output__lte: "스피커 최대",
            width__gte: "너비 최소",
            width__lte: "너비 최대",
            height__gte: "높이 최소",
            height__lte: "높이 최대",
            depth__gte: "깊이 최소",
            depth__lte: "깊이 최대",
            weight__gte: "무게 최소",
            weight__lte: "무게 최대",
            washing_cap__gte: "세탁 용량 최소",
            washing_cap__lte: "세탁 용량 최대",
            drying_cap__gte: "건조 용량 최소",
            drying_cap__lte: "건조 용량 최대",
            spin_op__gte: "탈수 최소",
            spin_op__lte: "탈수 최대",
            door_design: "도어 디자인",
            control_type: "조작 방식",
            door_type: "도어 타입",
            water_temp: "물 온도",
            suction_power__gte: "흡입력 최소",
            suction_power__lte: "흡입력 최대",
            battery_cnt__gte: "배터리 최소",
            battery_cnt__lte: "배터리 최대",
            unit_weight__gte: "본체 무게 최소",
            unit_weight__lte: "본체 무게 최대",
            tower_weight__gte: "타워 무게 최소",
            tower_weight__lte: "타워 무게 최대",
            unit_width__gte: "본체 너비 최소",
            unit_width__lte: "본체 너비 최대",
            unit_height__gte: "본체 높이 최소",
            unit_height__lte: "본체 높이 최대",
        };

        const RESOL_LABELS = {
            RES000: "8K / Micro RGB",
            RES001: "4K UHD",
            RES002: "FHD",
        };

        const IGNORE_PARAMS = new Set(["product_type", "page", "price_preset"]);

        const form = document.querySelector("[data-search-filter-form]");
        const filterRoot = document.querySelector("[data-search-filter]");
        if (!form || !filterRoot) {
            return;
        }

        const productType = filterRoot.dataset.productType || "REF";
        const params = new URLSearchParams(window.location.search);
        const priceMinInput = form.querySelector('input[name="price__gte"]');
        const priceMaxInput = form.querySelector('input[name="price__lte"]');
        const presetRadios = form.querySelectorAll("[data-price-preset]");
        const countBadge = document.querySelector("[data-filter-count-badge]");
        const submitLabel = document.querySelector("[data-filter-submit-label]");
        const activeFiltersWrap = document.querySelector("[data-active-filters-wrap]");
        const activeFiltersEl = document.querySelector("[data-active-filters]");
        const activeFiltersClear = document.querySelector("[data-active-filters-clear]");

        let optionsByType = {};

        function formatWon(value) {
            const num = Number(value);
            if (!Number.isFinite(num)) {
                return value;
            }
            return num.toLocaleString("ko-KR") + "원";
        }

        function paramLabel(key) {
            return FILTER_LABELS[key] || key.replace(/__/g, " ").replace(/_/g, " ");
        }

        function displayValue(key, value) {
            if (key === "resol_code" || key.endsWith("resol_code")) {
                return RESOL_LABELS[value] || value;
            }
            if (key.startsWith("price")) {
                return formatWon(value);
            }
            if (key.includes("__in")) {
                return value
                    .split(",")
                    .map(function (v) {
                        return v.trim();
                    })
                    .filter(Boolean)
                    .join(", ");
            }
            return value;
        }

        function countActiveFilters() {
            let count = 0;
            params.forEach(function (_value, key) {
                if (!IGNORE_PARAMS.has(key)) {
                    count += 1;
                }
            });
            return count;
        }

        function updateFilterCountUi() {
            const count = countActiveFilters();
            if (countBadge) {
                countBadge.textContent = String(count);
                countBadge.classList.toggle("hidden", count === 0);
                countBadge.classList.toggle("inline-flex", count > 0);
            }
            if (submitLabel) {
                submitLabel.textContent = count > 0 ? "필터 적용 (" + count + ")" : "필터 적용";
            }
        }

        function buildUrlWithoutParam(removeKey) {
            const next = new URLSearchParams(window.location.search);
            next.delete(removeKey);
            if (!next.has("page")) {
                next.set("page", "1");
            }
            const query = next.toString();
            return window.location.pathname + (query ? "?" + query : "");
        }

        function renderActiveFilters() {
            if (!activeFiltersEl || !activeFiltersWrap) {
                return;
            }

            activeFiltersEl.innerHTML = "";
            const entries = [];
            params.forEach(function (value, key) {
                if (IGNORE_PARAMS.has(key) || value === "") {
                    return;
                }
                entries.push({ key: key, value: value });
            });

            if (!entries.length) {
                activeFiltersWrap.hidden = true;
                return;
            }

            activeFiltersWrap.hidden = false;
            entries.forEach(function (entry) {
                const pill = document.createElement("a");
                pill.href = buildUrlWithoutParam(entry.key);
                pill.className =
                    "inline-flex max-w-full items-center gap-1 rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-medium text-red-800 transition-colors hover:bg-red-100";
                pill.title = "클릭하여 제거";
                pill.innerHTML =
                    '<span class="truncate">' +
                    paramLabel(entry.key) +
                    ": " +
                    displayValue(entry.key, entry.value) +
                    '</span><span aria-hidden="true" class="shrink-0 text-red-500">×</span>';
                activeFiltersEl.appendChild(pill);
            });
        }

        if (activeFiltersClear) {
            activeFiltersClear.addEventListener("click", function (event) {
                event.preventDefault();
                const pt = params.get("product_type") || productType;
                window.location.href =
                    window.location.pathname + "?product_type=" + encodeURIComponent(pt) + "&page=1";
            });
        }

        function restoreInputsFromParams() {
            form.querySelectorAll("[data-filter-param]").forEach(function (input) {
                const value = params.get(input.name);
                if (value !== null && value !== "") {
                    input.value = value;
                }
            });

            form.querySelectorAll("[data-filter-toggle]").forEach(function (group) {
                const hidden = group.querySelector("[data-filter-toggle-hidden]");
                const checkbox = group.querySelector("[data-filter-toggle-input]");
                if (!hidden || !checkbox) {
                    return;
                }
                const v = params.get(hidden.name);
                checkbox.checked = v === "1";
                hidden.value = checkbox.checked ? "1" : "";
            });
        }

        function loadOptions() {
            const url = window.SEARCH_FILTER_OPTIONS_URL;
            if (!url) {
                return Promise.resolve({});
            }
            return fetch(url)
                .then(function (res) {
                    return res.json();
                })
                .then(function (data) {
                    optionsByType = data || {};
                })
                .catch(function () {
                    optionsByType = {};
                });
        }

        function syncChipHidden(group) {
            const hidden = group.querySelector("[data-filter-chip-value]");
            const mode = group.dataset.mode || "multi";
            if (!hidden || mode === "single") {
                return;
            }
            const values = [];
            group.querySelectorAll('[data-filter-chip][aria-pressed="true"]').forEach(function (chip) {
                values.push(chip.dataset.chipValue);
            });
            hidden.value = values.join(",");
        }

        function renderChipGroups() {
            const typeOptions = optionsByType[productType] || {};
            form.querySelectorAll("[data-filter-chips]").forEach(function (group) {
                const field = group.dataset.field;
                const mode = group.dataset.mode || "multi";
                const list = group.querySelector("[data-filter-chips-list]");
                const hidden = group.querySelector("[data-filter-chip-value]");
                if (!field || !list || !hidden) {
                    return;
                }

                const choices = typeOptions[field] || [];
                list.innerHTML = "";

                const paramName = mode === "single" ? field : field + "__in";
                hidden.name = paramName;
                const current = params.get(paramName) || "";
                const selected = new Set(
                    mode === "single"
                        ? current
                            ? [current]
                            : []
                        : current.split(",").map(function (v) {
                            return v.trim();
                        })
                );

                choices.forEach(function (choice) {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className =
                        "max-w-full truncate rounded-full border border-gray-200 bg-white px-3 py-1.5 text-left text-xs font-medium text-gray-700 transition-colors hover:border-red-200 hover:bg-red-50 hover:text-red-700";
                    button.dataset.filterChip = "1";
                    button.dataset.chipValue = choice;
                    button.setAttribute("aria-pressed", selected.has(choice) ? "true" : "false");
                    if (field === "resol_code" && RESOL_LABELS[choice]) {
                        button.textContent = RESOL_LABELS[choice];
                        button.title = choice;
                    } else {
                        button.textContent = choice;
                    }
                    if (selected.has(choice)) {
                        button.classList.add("border-red-600", "bg-red-50", "text-red-700");
                    }
                    list.appendChild(button);
                });

                syncChipHidden(group);

                list.addEventListener("click", function (event) {
                    const chip = event.target.closest("[data-filter-chip]");
                    if (!chip) {
                        return;
                    }
                    const value = chip.dataset.chipValue;
                    if (mode === "single") {
                        const isActive = chip.getAttribute("aria-pressed") === "true";
                        list.querySelectorAll("[data-filter-chip]").forEach(function (btn) {
                            btn.setAttribute("aria-pressed", "false");
                            btn.classList.remove("border-red-600", "bg-red-50", "text-red-700");
                        });
                        if (isActive) {
                            hidden.value = "";
                        } else {
                            chip.setAttribute("aria-pressed", "true");
                            chip.classList.add("border-red-600", "bg-red-50", "text-red-700");
                            hidden.value = value;
                        }
                    } else {
                        const pressed = chip.getAttribute("aria-pressed") === "true";
                        chip.setAttribute("aria-pressed", pressed ? "false" : "true");
                        chip.classList.toggle("border-red-600", !pressed);
                        chip.classList.toggle("bg-red-50", !pressed);
                        chip.classList.toggle("text-red-700", !pressed);
                        syncChipHidden(group);
                    }
                });
            });
        }

        function initPresets() {
            form.querySelectorAll("[data-filter-presets]").forEach(function (wrap) {
                const minName = wrap.dataset.targetMin;
                const maxName = wrap.dataset.targetMax;
                const minInput = form.querySelector('input[name="' + minName + '"]');
                const maxInput = form.querySelector('input[name="' + maxName + '"]');
                if (!minInput || !maxInput) {
                    return;
                }

                function syncPresetActive() {
                    const min = minInput.value.trim();
                    const max = maxInput.value.trim();
                    wrap.querySelectorAll("[data-filter-preset]").forEach(function (btn) {
                        const pMin = btn.dataset.presetMin || "";
                        const pMax = btn.dataset.presetMax || "";
                        btn.dataset.active = min === pMin && max === pMax ? "true" : "false";
                    });
                }

                wrap.querySelectorAll("[data-filter-preset]").forEach(function (btn) {
                    btn.addEventListener("click", function () {
                        minInput.value = btn.dataset.presetMin || "";
                        maxInput.value = btn.dataset.presetMax || "";
                        syncPresetActive();
                    });
                });

                minInput.addEventListener("input", syncPresetActive);
                maxInput.addEventListener("input", syncPresetActive);
                syncPresetActive();
            });
        }

        function syncPricePresetFromInputs() {
            if (!priceMinInput || !priceMaxInput) {
                return;
            }

            const min = priceMinInput.value.trim();
            const max = priceMaxInput.value.trim();
            let matched = false;

            presetRadios.forEach(function (radio) {
                const presetMin = radio.dataset.priceMin || "";
                const presetMax = radio.dataset.priceMax || "";

                if (radio.value === "") {
                    if (!min && !max) {
                        radio.checked = true;
                        matched = true;
                    }
                    return;
                }

                if (min === presetMin && max === presetMax) {
                    radio.checked = true;
                    matched = true;
                }
            });

            if (!matched && presetRadios.length) {
                presetRadios[0].checked = true;
            }
        }

        function clearPriceInputs() {
            if (!priceMinInput || !priceMaxInput) {
                return;
            }
            priceMinInput.value = "";
            priceMaxInput.value = "";
        }

        function applyPricePreset(radio) {
            if (!priceMinInput || !priceMaxInput || !radio) {
                return;
            }
            if (radio.value === "" || radio.hasAttribute("data-price-clear")) {
                clearPriceInputs();
                return;
            }
            priceMinInput.value = radio.dataset.priceMin || "";
            priceMaxInput.value = radio.dataset.priceMax || "";
        }

        presetRadios.forEach(function (radio) {
            radio.addEventListener("change", function () {
                if (radio.checked) {
                    applyPricePreset(radio);
                }
            });
        });

        const directClearRadio = form.querySelector("[data-price-preset][data-price-clear]");
        if (directClearRadio) {
            const directClearLabel = directClearRadio.closest("label");
            if (directClearLabel) {
                directClearLabel.addEventListener("click", function () {
                    window.setTimeout(function () {
                        directClearRadio.checked = true;
                        clearPriceInputs();
                    }, 0);
                });
            }
        }

        if (priceMinInput) {
            priceMinInput.addEventListener("input", syncPricePresetFromInputs);
        }
        if (priceMaxInput) {
            priceMaxInput.addEventListener("input", syncPricePresetFromInputs);
        }

        function parseRangeLimit(value) {
            if (value === undefined || value === "") {
                return null;
            }
            const parsed = Number(value);
            return Number.isFinite(parsed) ? parsed : null;
        }

        function formatRangeValue(value, step) {
            if (step === 1 || step === "1") {
                return String(Math.round(value));
            }
            const decimals = String(step).includes(".") ? String(step).split(".")[1].length : 0;
            return decimals > 0 ? value.toFixed(decimals) : String(value);
        }

        function clampRangeInput(input) {
            const group = input.closest("[data-filter-range]");
            if (!group) {
                return;
            }

            const raw = input.value.trim();
            if (raw === "") {
                return;
            }

            let value = Number(raw);
            if (!Number.isFinite(value)) {
                input.value = "";
                return;
            }

            const rangeMin = parseRangeLimit(group.dataset.rangeMin);
            const rangeMax = parseRangeLimit(group.dataset.rangeMax);
            const step = group.dataset.rangeStep || input.step || "any";
            const minInput = group.querySelector('[data-filter-bound="min"]');
            const maxInput = group.querySelector('[data-filter-bound="max"]');

            if (rangeMin !== null) {
                value = Math.max(rangeMin, value);
            }
            if (rangeMax !== null) {
                value = Math.min(rangeMax, value);
            }

            if (input === minInput && maxInput) {
                const peerMax = parseRangeLimit(maxInput.value.trim());
                if (peerMax !== null) {
                    value = Math.min(value, peerMax);
                }
            } else if (input === maxInput && minInput) {
                const peerMin = parseRangeLimit(minInput.value.trim());
                if (peerMin !== null) {
                    value = Math.max(value, peerMin);
                }
            }

            const formatted = formatRangeValue(value, step);
            if (input.value !== formatted) {
                input.value = formatted;
            }
        }

        form.querySelectorAll("[data-filter-range] [data-filter-param]").forEach(function (input) {
            input.addEventListener("input", function () {
                clampRangeInput(input);
            });
            input.addEventListener("blur", function () {
                clampRangeInput(input);
            });
        });

        form.querySelectorAll("[data-filter-range]").forEach(function (group) {
            group.querySelectorAll("[data-filter-param]").forEach(function (input) {
                clampRangeInput(input);
            });
        });

        form.querySelectorAll("[data-filter-toggle]").forEach(function (group) {
            const checkbox = group.querySelector("[data-filter-toggle-input]");
            const hidden = group.querySelector("[data-filter-toggle-hidden]");
            if (!checkbox || !hidden) {
                return;
            }
            checkbox.addEventListener("change", function () {
                hidden.value = checkbox.checked ? "1" : "";
            });
        });

        form.addEventListener("submit", function () {
            form.querySelectorAll("[data-filter-param]").forEach(function (input) {
                if (input.value.trim() === "") {
                    input.removeAttribute("name");
                }
            });

            form.querySelectorAll("[data-filter-chips]").forEach(function (group) {
                syncChipHidden(group);
                const hidden = group.querySelector("[data-filter-chip-value]");
                if (hidden && hidden.value.trim() === "") {
                    hidden.removeAttribute("name");
                }
            });

            form.querySelectorAll("[data-filter-toggle-hidden]").forEach(function (hidden) {
                if (hidden.value.trim() === "") {
                    hidden.removeAttribute("name");
                }
            });

            presetRadios.forEach(function (radio) {
                radio.removeAttribute("name");
            });
        });

        restoreInputsFromParams();

        loadOptions().then(function () {
            renderChipGroups();
            initPresets();
            syncPricePresetFromInputs();
            updateFilterCountUi();
            renderActiveFilters();
        });
    }

    function initPagination() {
        const nav = document.querySelector("[data-pagination]");
        if (!nav) {
            return;
        }

        const current = Number(nav.dataset.current);
        const numPages = Number(nav.dataset.numPages);
        const summary = nav.querySelector("[data-pagination-summary]");
        const controls = nav.querySelector("[data-pagination-controls]");

        if (!controls || numPages <= 1) {
            return;
        }

        const btnBase =
            "inline-flex min-h-10 items-center justify-center rounded-xl border px-3 text-sm font-medium shadow-sm transition-all";
        const btnDefault = btnBase + " border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50";
        const btnActive = btnBase + " min-w-10 border-red-600 bg-red-50 font-bold text-red-600";
        const btnDisabled = btnBase + " cursor-not-allowed border-gray-100 bg-gray-50 text-gray-300";

        function pageHref(page) {
            const params = new URLSearchParams(window.location.search);
            params.set("page", String(page));
            return "?" + params.toString();
        }

        function pageNumbers() {
            const windowSize = 2;
            const pages = new Set();
            const onEnds = 1;

            for (let i = 1; i <= Math.min(onEnds, numPages); i += 1) {
                pages.add(i);
            }
            for (let i = Math.max(1, numPages - onEnds + 1); i <= numPages; i += 1) {
                pages.add(i);
            }
            for (let i = current - windowSize; i <= current + windowSize; i += 1) {
                if (i >= 1 && i <= numPages) {
                    pages.add(i);
                }
            }

            const sorted = Array.from(pages).sort(function (a, b) {
                return a - b;
            });

            const items = [];
            let prev = null;
            sorted.forEach(function (num) {
                if (prev !== null && num - prev > 1) {
                    items.push({ kind: "gap" });
                }
                items.push({ kind: "page", number: num });
                prev = num;
            });
            return items;
        }

        function makeLink(label, page, className) {
            const link = document.createElement("a");
            link.href = pageHref(page);
            link.className = className;
            link.textContent = label;
            return link;
        }

        function makeSpan(label, className) {
            const span = document.createElement("span");
            span.className = className;
            span.textContent = label;
            return span;
        }

        if (summary) {
            summary.textContent =
                nav.dataset.start + "–" + nav.dataset.end + " / 총 " + nav.dataset.total + "개";
        }

        controls.replaceChildren();

        if (nav.dataset.prev) {
            controls.appendChild(makeLink("이전", Number(nav.dataset.prev), btnDefault + " px-3.5"));
        } else {
            controls.appendChild(makeSpan("이전", btnDisabled + " px-3.5"));
        }

        pageNumbers().forEach(function (item) {
            if (item.kind === "gap") {
                const gap = document.createElement("span");
                gap.className = "px-1 text-sm text-gray-400";
                gap.textContent = "…";
                controls.appendChild(gap);
                return;
            }

            if (item.number === current) {
                const currentSpan = makeSpan(String(item.number), btnActive);
                currentSpan.setAttribute("aria-current", "page");
                controls.appendChild(currentSpan);
                return;
            }

            controls.appendChild(makeLink(String(item.number), item.number, btnDefault + " min-w-10"));
        });

        if (nav.dataset.next) {
            controls.appendChild(makeLink("다음", Number(nav.dataset.next), btnDefault + " px-3.5"));
        } else {
            controls.appendChild(makeSpan("다음", btnDisabled + " px-3.5"));
        }
    }

    initSearchFilter();
    initPagination();
})();
