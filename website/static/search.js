/*
 * Progressive enhancement for the frameworks index.
 *
 * The index is fully rendered as static HTML. This script only hides entries
 * that do not match a filter, so with JavaScript disabled the complete index
 * stays readable and navigable. It performs no network request and stores
 * nothing.
 */
(function () {
  "use strict";

  var input = document.querySelector("[data-search]");
  var countEl = document.querySelector("[data-count]");
  var emptyEl = document.querySelector("[data-empty]");
  if (!input) return;

  var entries = Array.prototype.slice.call(document.querySelectorAll("[data-entry]"));
  var tiers = Array.prototype.slice.call(document.querySelectorAll("[data-tier]"));
  var total = entries.length;

  function report(shown, filtering) {
    if (countEl) {
      countEl.textContent = filtering
        ? shown + " of " + total + " frameworks"
        : total + " frameworks";
    }
    if (emptyEl) emptyEl.hidden = shown !== 0;
  }

  function apply() {
    var query = input.value.trim().toLowerCase();
    var filtering = query.length > 0;
    var shown = 0;

    entries.forEach(function (entry) {
      var match = !filtering || (entry.getAttribute("data-text") || "").indexOf(query) !== -1;
      entry.hidden = !match;
      if (match) shown++;
    });

    // Hide a tier heading when every framework inside it is filtered out, so
    // the page never shows an empty section header.
    tiers.forEach(function (tier) {
      var visible = tier.querySelectorAll("[data-entry]:not([hidden])").length;
      tier.hidden = visible === 0;
    });

    report(shown, filtering);
  }

  input.addEventListener("input", apply);
  report(total, false);
})();
