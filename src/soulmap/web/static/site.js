const normaliseSearchText = (value) => {
  const folded = String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase();
  return folded.replace(/[^a-z0-9]+/g, " ").trim();
};

const searchTerms = (value) => normaliseSearchText(value).split(/\s+/).filter(Boolean);

const entrySearchText = (entry) =>
  [
    entry.slug,
    entry.group,
    entry.title,
    entry.summary,
    entry.use_when,
    entry.best_for,
    entry.boundary,
  ]
    .filter(Boolean)
    .join(" ");

const scoreSearchEntry = (entry, query) => {
  const normalizedQuery = normaliseSearchText(query);
  if (!normalizedQuery) return 0;
  const terms = searchTerms(query);
  const slug = normaliseSearchText(entry.slug);
  const title = normaliseSearchText(entry.title);
  const group = normaliseSearchText(entry.group);
  const haystack = normaliseSearchText(entrySearchText(entry));
  if (!terms.every((term) => haystack.includes(term))) return -1;

  let score = 0;
  if (normalizedQuery === slug) score += 1000;
  if (normalizedQuery === title) score += 900;
  if (normalizedQuery === group) score += 360;
  if (slug.includes(normalizedQuery)) score += 500;
  if (title.includes(normalizedQuery)) score += 420;
  if (group.includes(normalizedQuery)) score += 360;
  for (const term of terms) {
    if (slug.startsWith(term)) score += 40;
    if (title.startsWith(term)) score += 35;
    if (haystack.includes(term)) score += 15;
  }
  return score;
};

document.addEventListener("alpine:init", () => {
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
          input.addEventListener("change", () => this.search(form));
        }
        this.search(form);
      });
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
      const request = ++this.searchRequest;
      const input = form.querySelector("input[name=q]");
      const grid = this.$root.querySelector("#skill-grid");
      if (!input || !grid) return;
      const query = input.value;
      const loading = form.querySelector("#skill-search-loading");
      if (loading) loading.hidden = false;
      grid.setAttribute("aria-busy", "true");
      const entries = await this.loadSearchEntries(form);
      if (loading) loading.hidden = true;
      grid.setAttribute("aria-busy", "false");
      if (request !== this.searchRequest || !entries) return;

      const cards = Array.from(grid.querySelectorAll(":scope > .skill-card"));
      const cardsBySlug = new Map(
        cards.map((card) => [card.querySelector(".code-pill")?.textContent?.trim(), card])
      );
      const ranked = entries
        .map((entry, index) => ({ entry, index, score: scoreSearchEntry(entry, query) }))
        .filter((item) => item.score >= 0)
        .sort((left, right) => right.score - left.score || left.index - right.index);
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
        const slug = card.querySelector(".code-pill")?.textContent?.trim();
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
      if (event.key === "Escape") {
        event.preventDefault();
        this.close();
        return;
      }
      if (event.key !== "Tab") return;
      const dialog = event.currentTarget;
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
