document.addEventListener("alpine:init", () => {
  Alpine.data("clipboard", () => ({
    copied: false,
    async copy(value) {
      try {
        await navigator.clipboard.writeText(value);
      } catch (error) {
        const input = document.createElement("input");
        input.value = value;
        input.setAttribute("readonly", "true");
        input.style.position = "fixed";
        input.style.opacity = "0";
        document.body.appendChild(input);
        input.select();
        document.execCommand("copy");
        input.remove();
      }
      this.copied = true;
      window.setTimeout(() => { this.copied = false; }, 1600);
    }
  }));

  Alpine.data("skillCatalog", () => ({
    openSlug: "",
    returnFocus: null,
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
