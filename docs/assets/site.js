/* fires-landuse-climate-interactions — progressive enhancement only.
   The site is fully readable and navigable with JavaScript disabled. */

(function () {
  "use strict";

  /* ---------------- theme toggle (persisted) ---------------- */
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem("fli-theme"); } catch (e) {}
  if (stored) root.setAttribute("data-theme", stored);
  else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    root.setAttribute("data-theme", "dark");
  }

  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("fli-theme", next); } catch (e) {}
    });
  }

  /* ---------------- mobile sidebar ---------------- */
  var burger = document.querySelector(".burger");
  var sidebar = document.querySelector(".sidebar");
  var scrim = document.querySelector(".sidebar-scrim");
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove("open");
    if (scrim) scrim.classList.remove("open");
    if (burger) burger.setAttribute("aria-expanded", "false");
  }
  if (burger && sidebar) {
    burger.addEventListener("click", function () {
      var open = sidebar.classList.toggle("open");
      if (scrim) scrim.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  if (scrim) scrim.addEventListener("click", closeSidebar);
  sidebar && sidebar.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", closeSidebar);
  });

  /* ---------------- copy buttons on code blocks ---------------- */
  document.querySelectorAll(".codewrap").forEach(function (wrap) {
    var btn = wrap.querySelector(".copy");
    var pre = wrap.querySelector("pre");
    if (!btn || !pre) return;
    btn.addEventListener("click", function () {
      var text = pre.innerText;
      var done = function () {
        btn.textContent = "Copied";
        btn.classList.add("done");
        setTimeout(function () { btn.textContent = "Copy"; btn.classList.remove("done"); }, 1500);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else { fallback(); }
      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = text; ta.setAttribute("readonly", "");
        ta.style.position = "absolute"; ta.style.left = "-9999px";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { btn.textContent = "Select manually"; }
        document.body.removeChild(ta);
      }
    });
  });

  /* ---------------- right-hand TOC scroll-spy ---------------- */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {}, targets = [];
    tocLinks.forEach(function (a) {
      var el = document.getElementById(a.getAttribute("href").slice(1));
      if (el) { map[el.id] = a; targets.push(el); }
    });
    var visible = new Set();
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) visible.add(e.target.id); else visible.delete(e.target.id);
      });
      var first = targets.filter(function (t) { return visible.has(t.id); })[0];
      if (!first) return;
      tocLinks.forEach(function (a) { a.classList.remove("on"); });
      map[first.id].classList.add("on");
    }, { rootMargin: "-72px 0px -70% 0px", threshold: 0 });
    targets.forEach(function (t) { obs.observe(t); });
  }

  /* ---------------- sidebar active-section highlighting ---------------- */
  var sideSubLinks = Array.prototype.slice.call(document.querySelectorAll(".side-sub a[href*='#']"));
  if (sideSubLinks.length && "IntersectionObserver" in window) {
    var smap = {}, stargets = [];
    sideSubLinks.forEach(function (a) {
      var hash = a.getAttribute("href").split("#")[1];
      var el = hash ? document.getElementById(hash) : null;
      if (el) { smap[el.id] = a; stargets.push(el); }
    });
    var svisible = new Set();
    var sobs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) svisible.add(e.target.id); else svisible.delete(e.target.id);
      });
      var first = stargets.filter(function (t) { return svisible.has(t.id); })[0];
      sideSubLinks.forEach(function (a) { a.removeAttribute("aria-current"); });
      if (first) smap[first.id].setAttribute("aria-current", "section");
    }, { rootMargin: "-72px 0px -70% 0px", threshold: 0 });
    stargets.forEach(function (t) { sobs.observe(t); });
  }

  /* ---------------- cross-page search ---------------- */
  var input = document.querySelector(".topbar-search input");
  var results = document.querySelector(".search-results");
  var index = null;
  var activeIdx = -1;

  function loadIndex() {
    if (index) return Promise.resolve(index);
    return fetch("search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; return index; })
      .catch(function () { index = []; return index; });
  }

  function render(matches, query) {
    if (!results) return;
    if (!matches.length) {
      results.innerHTML = '<div class="search-empty">No matches for "' + escapeHtml(query) + '"</div>';
      results.classList.add("open");
      return;
    }
    results.innerHTML = matches.slice(0, 12).map(function (m, i) {
      return '<a href="' + m.page + (m.id ? "#" + m.id : "") + '" data-idx="' + i + '">' +
        '<span class="sr-page">' + escapeHtml(m.pageTitle) + '</span>' +
        '<span class="sr-heading">' + escapeHtml(m.text) + "</span></a>";
    }).join("");
    results.classList.add("open");
    activeIdx = -1;
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  if (input && results) {
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      if (!q) { results.classList.remove("open"); return; }
      loadIndex().then(function (idx) {
        var matches = idx.filter(function (item) {
          return item.text.toLowerCase().indexOf(q) !== -1 ||
                 item.pageTitle.toLowerCase().indexOf(q) !== -1;
        });
        render(matches, q);
      });
    });
    input.addEventListener("keydown", function (e) {
      var links = results.querySelectorAll("a");
      if (e.key === "ArrowDown") {
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, links.length - 1);
        links.forEach(function (l, i) { l.classList.toggle("active", i === activeIdx); });
        if (links[activeIdx]) links[activeIdx].scrollIntoView({ block: "nearest" });
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, 0);
        links.forEach(function (l, i) { l.classList.toggle("active", i === activeIdx); });
      } else if (e.key === "Enter") {
        if (activeIdx >= 0 && links[activeIdx]) { links[activeIdx].click(); }
      } else if (e.key === "Escape") {
        results.classList.remove("open"); input.blur();
      }
    });
    document.addEventListener("click", function (e) {
      if (!results.contains(e.target) && e.target !== input) results.classList.remove("open");
    });
  }
})();
