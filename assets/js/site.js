/* =============================================================
   site.js — interactions only. All CONTENT and FEATURE TOGGLES are
   driven by _data/settings.yml + _data/profile.yml + _data/publications.yml
   at Jekyll build time (see index.html / _layouts/default.html).
   This file just wires up whatever ended up on the page — it reads
   window.SITE_FEATURES (injected by the layout) so turning a feature
   off in settings.yml means its DOM elements simply won't exist here,
   and this script skips them without erroring.
   ============================================================= */
(function () {
  "use strict";

  var FEATURES = window.SITE_FEATURES || {};

  function initScrollSpy() {
    if (FEATURES.scrollspy_nav === false) return;
    var sections = Array.from(document.querySelectorAll("main section[id], section.hero[id]"));
    var navLinks = document.querySelectorAll(".nav-links a");
    if (!sections.length || !navLinks.length) return;
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          navLinks.forEach(function (a) { a.classList.remove("active"); });
          var active = document.querySelector('.nav-links a[href="#' + e.target.id + '"]');
          if (active) active.classList.add("active");
        }
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    sections.forEach(function (s) { spy.observe(s); });
  }

  function initReveal() {
    if (FEATURES.scroll_reveal === false) return;
    var revealObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("visible"); revealObs.unobserve(e.target); }
      });
    }, { threshold: 0.06 });
    document.querySelectorAll(".section").forEach(function (s) { revealObs.observe(s); });
  }

  function initPubFilter() {
    var searchEl = document.getElementById("pub-search");
    var yearEl = document.getElementById("pub-year");
    var typeEl = document.getElementById("pub-type");
    var countEl = document.getElementById("pub-count");
    var pubs = Array.from(document.querySelectorAll("#pub-list .pub"));
    if (!pubs.length) return;

    // Any of these controls may be entirely absent from the DOM if their
    // feature was turned off in settings.yml — guard every reference.
    function filterPubs() {
      var term = searchEl ? (searchEl.value || "").trim().toLowerCase() : "";
      var year = yearEl ? yearEl.value : "";
      var type = typeEl ? typeEl.value : "";
      var n = 0;
      pubs.forEach(function (p) {
        var ok = (!term || p.dataset.search.indexOf(term) !== -1) &&
          (!year || p.dataset.year === year) &&
          (!type || p.dataset.type === type);
        p.style.display = ok ? "" : "none";
        if (ok) n++;
      });
      if (countEl) countEl.textContent = n + " of " + pubs.length + " publications";
    }

    if (searchEl) searchEl.addEventListener("input", filterPubs);
    if (yearEl) yearEl.addEventListener("change", filterPubs);
    if (typeEl) typeEl.addEventListener("change", filterPubs);
    filterPubs();
  }

  window.toggleBibtex = function (btn) {
    var pre = btn.closest(".pub").querySelector(".bibtex-block");
    if (!pre) return; // bibtex_export feature disabled, block doesn't exist
    var show = pre.style.display !== "block";
    pre.style.display = show ? "block" : "none";
    btn.setAttribute("aria-expanded", show ? "true" : "false");
    btn.textContent = show ? "Hide BibTeX" : "BibTeX";
  };

  function boot() {
    initScrollSpy();
    initReveal();
    initPubFilter();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
