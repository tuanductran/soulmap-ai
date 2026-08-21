(() => {
  const metadataSelectors = [
    'meta[name="description"]',
    'meta[property^="og:"]',
    'meta[name^="twitter:"]',
  ];

  function syncDocumentMetadata(responseText) {
    if (!responseText || typeof DOMParser === "undefined") return;
    const nextDocument = new DOMParser().parseFromString(responseText, "text/html");
    if (!nextDocument.documentElement.lang) return;

    document.documentElement.lang = nextDocument.documentElement.lang;
    document.title = nextDocument.title;

    for (const selector of metadataSelectors) {
      for (const currentMeta of document.head.querySelectorAll(selector)) {
        currentMeta.remove();
      }
      for (const nextMeta of nextDocument.head.querySelectorAll(selector)) {
        document.head.appendChild(nextMeta.cloneNode(true));
      }
    }

    const currentCanonical = document.head.querySelector('link[rel="canonical"]');
    const nextCanonical = nextDocument.head.querySelector('link[rel="canonical"]');
    if (currentCanonical && nextCanonical) {
      currentCanonical.replaceWith(nextCanonical.cloneNode(true));
    }

    for (const currentAlternate of document.head.querySelectorAll('link[rel="alternate"]')) {
      currentAlternate.remove();
    }
    for (const nextAlternate of nextDocument.head.querySelectorAll('link[rel="alternate"]')) {
      document.head.appendChild(nextAlternate.cloneNode(true));
    }

    for (const id of ["soulmap-locale-data"] ) {
      const currentScript = document.getElementById(id);
      const nextScript = nextDocument.getElementById(id);
      if (currentScript && nextScript) currentScript.textContent = nextScript.textContent;
    }

    const currentStructuredData = document.querySelector('script[type="application/ld+json"]');
    const nextStructuredData = nextDocument.querySelector('script[type="application/ld+json"]');
    if (currentStructuredData && nextStructuredData) {
      currentStructuredData.textContent = nextStructuredData.textContent;
    }
  }

  document.addEventListener("htmx:beforeRequest", () => {
    document.documentElement.setAttribute("aria-busy", "true");
  });

  document.addEventListener("htmx:beforeSwap", (event) => {
    const target = event.detail?.target;
    if (target !== document.body) return;
    syncDocumentMetadata(event.detail?.xhr?.responseText);
  });

  document.addEventListener("htmx:afterSettle", (event) => {
    if (event.detail?.target !== document.body) return;
    document.documentElement.removeAttribute("aria-busy");
    document.body.classList.remove("modal-open");
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    document.dispatchEvent(new CustomEvent("soulmap:page-ready"));
  });

  document.addEventListener("htmx:responseError", () => {
    document.documentElement.removeAttribute("aria-busy");
  });
})();

document.addEventListener("alpine:init", () => {
  Alpine.data("languageMenu", () => ({
    open: false,
    toggle() {
      if (this.open) {
        this.close(true);
      } else {
        this.openMenu();
      }
    },
    openMenu() {
      this.open = true;
      this.$nextTick(() => this.focusFirst());
    },
    close(returnFocus = true) {
      this.open = false;
      if (returnFocus) {
        this.$nextTick(() => {
          this.$root.querySelector(".locale-trigger")?.focus();
        });
      }
    },
    focusFirst() {
      this.$root.querySelector('[role="menuitem"]')?.focus();
    },
    onKeydown(event) {
      const items = Array.from(this.$root.querySelectorAll('[role="menuitem"]'));
      if (event.key === "Escape") {
        event.preventDefault();
        this.close(true);
        return;
      }
      if (!items.length || !["ArrowDown", "ArrowUp"].includes(event.key)) return;
      event.preventDefault();
      if (!this.open) {
        this.openMenu();
        return;
      }
      const currentIndex = items.indexOf(document.activeElement);
      const direction = event.key === "ArrowDown" ? 1 : -1;
      const nextIndex = currentIndex < 0
        ? 0
        : (currentIndex + direction + items.length) % items.length;
      items[nextIndex].focus();
    },
  }));

  Alpine.data("navScroll", () => ({
    canScrollLeft: false,
    canScrollRight: false,
    scroller: null,
    updateScrollState() {
      if (!this.scroller) return;
      const maxScroll = this.scroller.scrollWidth - this.scroller.clientWidth;
      this.canScrollLeft = this.scroller.scrollLeft > 1;
      this.canScrollRight = this.scroller.scrollLeft < maxScroll - 1;
    },
    init() {
      this.scroller = this.$root.querySelector(".nav-links");
      if (!this.scroller) return;
      const update = () => this.updateScrollState();
      this.scroller.addEventListener("scroll", update, { passive: true });
      window.addEventListener("resize", update, { passive: true });
      if ("ResizeObserver" in window) {
        this.resizeObserver = new ResizeObserver(update);
        this.resizeObserver.observe(this.scroller);
      }
      this.$nextTick(() => {
        update();
        requestAnimationFrame(() => requestAnimationFrame(update));
      });
      if (document.fonts?.ready) {
        document.fonts.ready.then(update);
      }
    },
  }));

  Alpine.data("clipboard", () => ({
    copied: false,
    copyFailed: false,
    async copy(value) {
      this.copied = false;
      this.copyFailed = false;
      let success = false;
      try {
        await navigator.clipboard.writeText(value);
        success = true;
      } catch (error) {
        const input = document.createElement("input");
        input.value = value;
        input.setAttribute("readonly", "true");
        input.style.position = "fixed";
        input.style.opacity = "0";
        document.body.appendChild(input);
        input.select();
        try {
          success = document.execCommand("copy");
        } catch (fallbackError) {
          success = false;
        }
        input.remove();
      }
      this.copied = success;
      this.copyFailed = !success;
      if (success) {
        window.setTimeout(() => { this.copied = false; }, 1600);
      }
    }
  }));

  Alpine.data("skillCatalog", () => ({
    openSlug: "",
    returnFocus: null,
    mode: "search",
    modeDescription: "",
    queryLabel: "",
    queryPlaceholder: "",
    queryHint: "",
    searchEntries: null,
    searchLoading: false,
    searchRequest: 0,
    init() {
      this.$nextTick(() => {
        const form = this.$root.querySelector("form[data-search-api]");
        if (!form) return;
        const input = form.querySelector("input[name=q]");
        if (input) {
          input.addEventListener("input", () => this.search(form));
        }
        this.updateModeDescription(form);
        this.search(form);
      });
    },
    updateModeDescription(form) {
      const asking = this.mode === "ask";
      this.modeDescription = asking
        ? form.dataset.searchAskHint
        : form.dataset.searchSearchHint;
      this.queryLabel = asking
        ? form.dataset.askQueryLabel
        : form.dataset.searchQueryLabel;
      this.queryPlaceholder = asking
        ? form.dataset.askQueryPlaceholder
        : form.dataset.searchQueryPlaceholder;
      this.queryHint = asking
        ? form.dataset.askQueryHint
        : form.dataset.searchQueryHint;
    },
    modeChanged() {
      const form = this.$root.querySelector("form[data-search-api]");
      if (!form) return;
      this.updateModeDescription(form);
      this.search(form);
    },
    preventSubmit(event) {
      event.preventDefault();
      this.search(event.currentTarget);
    },
    async loadSearchEntries(form) {
      if (this.searchEntries) return this.searchEntries;
      const endpoint = form.dataset.searchApi;
      if (!endpoint) return [];
      this.searchLoading = true;
      try {
        const url = new URL(endpoint, window.location.href);
        url.searchParams.set("limit", "100");
        const response = await fetch(url.toString(), {
          headers: { Accept: "application/json" },
          credentials: "same-origin",
        });
        if (!response.ok) throw new Error(`Search API returned ${response.status}`);
        const payload = await response.json();
        this.searchEntries = Array.isArray(payload.results) ? payload.results : [];
      } catch (error) {
        this.searchEntries = null;
        return null;
      } finally {
        this.searchLoading = false;
      }
      return this.searchEntries;
    },
    async search(form) {
      const engine = window.SoulMapSearch;
      const request = ++this.searchRequest;
      const input = form.querySelector("input[name=q]");
      const grid = this.$root.querySelector("#skill-grid");
      const questionResults = this.$root.querySelector("#question-results");
      if (!engine || !input || !grid || !questionResults) return;
      const query = input.value.slice(0, engine.MAX_QUERY_LENGTH);
      const loading = form.querySelector("#skill-search-loading");
      if (loading) loading.hidden = false;
      grid.setAttribute("aria-busy", "true");
      questionResults.setAttribute("aria-busy", "true");
      const entries = await this.loadSearchEntries(form);
      if (loading) loading.hidden = true;
      grid.setAttribute("aria-busy", "false");
      questionResults.setAttribute("aria-busy", "false");
      if (request !== this.searchRequest) return;
      if (!entries) {
        this.renderSearchError(form, grid, questionResults);
        return;
      }

      if (this.mode === "ask") {
        this.renderAskResults(engine.search(entries, query, { mode: "ask", limit: engine.MAX_QUESTION_RESULTS }), form, grid, questionResults);
      } else {
        this.renderSkillResults(engine.search(entries, query, { mode: "search", limit: engine.MAX_RESULTS }), grid, questionResults);
      }
      document.body.dispatchEvent(new CustomEvent("soulmap:search", {
        detail: { mode: this.mode, query, count: this.mode === "ask" ? questionResults.querySelectorAll("article").length : grid.querySelectorAll(":scope > .skill-card:not([hidden])").length },
      }));
    },
    renderSearchError(form, grid, questionResults) {
      const message = document.createElement("p");
      message.className = "empty-state search-error";
      message.setAttribute("role", "alert");
      message.textContent = form.dataset.searchError || "Search is temporarily unavailable.";
      if (this.mode === "ask") {
        grid.hidden = true;
        questionResults.hidden = false;
        questionResults.replaceChildren(message);
        return;
      }
      questionResults.hidden = true;
      grid.hidden = false;
      for (const card of grid.querySelectorAll(":scope > .skill-card")) {
        card.hidden = true;
        card.setAttribute("aria-hidden", "true");
      }
      const existingError = grid.querySelector(":scope > .search-error");
      if (existingError) existingError.remove();
      grid.appendChild(message);
    },
    renderSkillResults(ranked, grid, questionResults) {
      questionResults.hidden = true;
      grid.hidden = false;
      const existingError = grid.querySelector(":scope > .search-error");
      if (existingError) existingError.remove();
      const cards = Array.from(grid.querySelectorAll(":scope > .skill-card"));
      const cardsBySlug = new Map(
        cards.map((card) => [card.dataset.skillSlug || card.querySelector(".skill-card__slug")?.textContent?.trim(), card])
      );
      const visibleSlugs = new Set(ranked.map((item) => item.entry.slug));
      for (const item of ranked) {
        const card = cardsBySlug.get(item.entry.slug);
        if (card) {
          card.hidden = false;
          card.setAttribute("aria-hidden", "false");
          grid.appendChild(card);
        }
      }
      for (const card of cards) {
        const slug = card.dataset.skillSlug || card.querySelector(".skill-card__slug")?.textContent?.trim();
        const visible = visibleSlugs.has(slug);
        card.hidden = !visible;
        card.setAttribute("aria-hidden", String(!visible));
      }
      const existingEmpty = grid.querySelector(":scope > .empty-state[data-client-search]");
      if (ranked.length === 0 && cards.length > 0) {
        const empty = existingEmpty || document.createElement("p");
        empty.className = "empty-state";
        empty.dataset.clientSearch = "true";
        empty.setAttribute("role", "status");
        empty.textContent = grid.dataset.searchEmpty || "No results.";
        if (!existingEmpty) grid.appendChild(empty);
      } else if (existingEmpty) {
        existingEmpty.remove();
      }
    },
    renderAskResults(ranked, form, grid, questionResults) {
      grid.hidden = true;
      questionResults.hidden = false;
      questionResults.replaceChildren();
      if (!ranked.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.setAttribute("role", "status");
        empty.textContent = form.dataset.askEmpty || "No matching Skill scenario.";
        questionResults.appendChild(empty);
        return;
      }
      for (const result of ranked) {
        const article = document.createElement("article");
        article.className = "question-card";
        const meta = document.createElement("p");
        meta.className = "skill-card__meta";
        meta.textContent = `${result.entry.group} · ${result.scenario.title}`;
        const title = document.createElement("h2");
        title.textContent = result.entry.title;
        const scenario = document.createElement("p");
        scenario.className = "question-card__scenario";
        scenario.textContent = result.scenario.title;
        const label = document.createElement("p");
        label.className = "question-label";
        label.textContent = form.dataset.askResultLabel || "Starter question";
        const question = document.createElement("blockquote");
        question.textContent = result.scenario.question;
        const actions = document.createElement("div");
        actions.className = "skill-card__actions";
        const useButton = document.createElement("button");
        useButton.className = "button small";
        useButton.type = "button";
        useButton.textContent = form.dataset.askUseLabel || "Use this question";
        useButton.addEventListener("click", () => this.useQuestion(result.scenario.question, form));
        const skillLink = document.createElement("a");
        skillLink.className = "link-button small secondary";
        const skillRoot = form.dataset.skillRoot || "/skills";
        skillLink.href = `${skillRoot.replace(/\/$/, "")}/${encodeURIComponent(result.entry.slug)}`;
        skillLink.textContent = form.dataset.askDetailsLabel || "View Skill";
        actions.append(useButton, skillLink);
        article.append(meta, title, scenario, label, question, actions);
        questionResults.appendChild(article);
      }
    },
    useQuestion(question, form) {
      const input = form.querySelector("input[name=q]");
      if (!input) return;
      input.value = question;
      this.search(form);
    },
    open(slug, trigger) {
      this.returnFocus = trigger || document.activeElement;
      document.body.classList.add("modal-open");
      this.openSlug = slug;
      this.$nextTick(() => this.focusDialog());
    },
    close() {
      this.openSlug = "";
      document.body.classList.remove("modal-open");
      this.$nextTick(() => {
        if (this.returnFocus && typeof this.returnFocus.focus === "function") {
          this.returnFocus.focus();
        }
      });
    },
    focusDialog() {
      const dialog = this.$root.querySelector("[role=dialog]:not([hidden])");
      if (dialog) dialog.focus();
    },
    trap(event) {
      if (!this.openSlug) return;
      const dialog = this.$root.querySelector('[role="dialog"]');
      if (!dialog || !dialog.contains(document.activeElement)) return;
      if (event.key === "Escape") {
        event.preventDefault();
        this.close();
        return;
      }
      if (event.key !== "Tab") return;
      const focusable = Array.from(
        dialog.querySelectorAll("a[href], button:not([disabled]), [tabindex]:not([tabindex='-1'])")
      );
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  }));
});
