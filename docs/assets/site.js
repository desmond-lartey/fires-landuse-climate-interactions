/* fires-landuse-climate-interactions — progressive enhancement only.
   The site is fully readable with JavaScript disabled. */

(function () {
  "use strict";

  /* ---- copy buttons on code blocks ---- */
  document.querySelectorAll(".codewrap").forEach(function (wrap) {
    var btn = wrap.querySelector(".copy");
    var pre = wrap.querySelector("pre");
    if (!btn || !pre) return;
    btn.addEventListener("click", function () {
      var text = pre.innerText;
      var done = function () {
        btn.textContent = "Copied";
        btn.classList.add("done");
        setTimeout(function () {
          btn.textContent = "Copy";
          btn.classList.remove("done");
        }, 1600);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
      }
      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "absolute";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { btn.textContent = "Select manually"; }
        document.body.removeChild(ta);
      }
    });
  });

  /* ---- mobile navigation ---- */
  var toggle = document.querySelector(".navtoggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.querySelector(".mast-nav").classList.toggle("open");
      var sb = document.querySelector(".sidebar");
      if (sb) sb.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---- scroll-spy for the section list ---- */
  var links = Array.prototype.slice.call(
    document.querySelectorAll('.sidebar a[href^="#"]')
  );
  if (links.length && "IntersectionObserver" in window) {
    var map = {};
    var targets = [];
    links.forEach(function (a) {
      var el = document.getElementById(a.getAttribute("href").slice(1));
      if (el) { map[el.id] = a; targets.push(el); }
    });
    var visible = new Set();
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) visible.add(e.target.id);
        else visible.delete(e.target.id);
      });
      var first = targets.filter(function (t) { return visible.has(t.id); })[0];
      if (!first) return;
      links.forEach(function (a) { a.classList.remove("on"); });
      map[first.id].classList.add("on");
    }, { rootMargin: "-70px 0px -68% 0px", threshold: 0 });
    targets.forEach(function (t) { obs.observe(t); });
  }

  /* ---- staggered reveal of the fire-season calendar ---- */
  var cells = document.querySelectorAll("table.cal td.v");
  if (cells.length && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    cells.forEach(function (c, i) {
      c.style.animationDelay = (i % 6) * 45 + Math.floor(i / 6) * 28 + "ms";
    });
  }
})();
