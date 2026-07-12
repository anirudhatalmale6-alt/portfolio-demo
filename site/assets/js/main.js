/* Portfolio interactions: lightbox, testimonial cycler, scroll reveal.
   Vanilla, ~4KB, no dependencies. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- sticky header rule ---------- */
  var head = document.querySelector(".site-head");
  var onScroll = function () {
    head.classList.toggle("is-stuck", window.scrollY > 8);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---------- scroll reveal ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reduced || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ---------- lightbox ---------- */
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var lb = document.getElementById("lightbox");
  var lbStage = lb.querySelector(".lb-stage");
  var lbImg = lb.querySelector(".lb-stage img");
  var lbTitle = lb.querySelector(".lb-info h3");
  var lbText = lb.querySelector(".lb-info p");
  var lbCount = lb.querySelector(".lb-count");
  var index = 0;
  var lastFocus = null;

  var items = cards.map(function (c) {
    return {
      src: c.dataset.full,
      alt: c.dataset.alt,
      title: c.dataset.title,
      category: c.dataset.category,
      year: c.dataset.year,
      description: c.dataset.description
    };
  });

  function preload(i) {
    if (i < 0 || i >= items.length) return;
    var im = new Image();
    im.src = items[i].src;
  }

  function show(i) {
    index = (i + items.length) % items.length;
    var it = items[index];
    lbImg.classList.remove("is-ready", "is-zoomed");
    lbStage.classList.remove("is-zoomed");
    lbImg.onload = function () { lbImg.classList.add("is-ready"); };
    lbImg.src = it.src;
    lbImg.alt = it.alt;
    lbTitle.textContent = it.title;
    lbText.textContent = it.category + " · " + it.year + " — " + it.description;
    lbCount.textContent = String(index + 1).padStart(2, "0") + " / " + String(items.length).padStart(2, "0");
    preload(index + 1);
    preload(index - 1);
  }

  function open(i, trigger) {
    lastFocus = trigger || document.activeElement;
    show(i);
    lb.classList.add("is-open");
    lb.setAttribute("aria-hidden", "false");
    document.body.classList.add("lb-open");
    lb.querySelector(".lb-close").focus();
  }

  function close() {
    lb.classList.remove("is-open");
    lb.setAttribute("aria-hidden", "true");
    document.body.classList.remove("lb-open");
    lbImg.src = "";
    if (lastFocus) lastFocus.focus();
  }

  cards.forEach(function (c, i) {
    c.addEventListener("click", function () { open(i, c); });
  });

  lb.querySelector(".lb-close").addEventListener("click", close);
  lb.querySelector(".lb-prev").addEventListener("click", function () { show(index - 1); });
  lb.querySelector(".lb-next").addEventListener("click", function () { show(index + 1); });

  lbStage.addEventListener("click", function (e) {
    if (e.target === lbImg) {
      var zoom = !lbImg.classList.contains("is-zoomed");
      lbImg.classList.toggle("is-zoomed", zoom);
      lbStage.classList.toggle("is-zoomed", zoom);
    } else {
      close();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (!lb.classList.contains("is-open")) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowRight") show(index + 1);
    else if (e.key === "ArrowLeft") show(index - 1);
    else if (e.key === "Tab") {
      // simple focus trap
      var f = lb.querySelectorAll("button");
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  /* swipe */
  var x0 = null;
  lbStage.addEventListener("touchstart", function (e) { x0 = e.changedTouches[0].clientX; }, { passive: true });
  lbStage.addEventListener("touchend", function (e) {
    if (x0 === null || lbImg.classList.contains("is-zoomed")) { x0 = null; return; }
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 48) show(dx < 0 ? index + 1 : index - 1);
    x0 = null;
  }, { passive: true });

  /* ---------- testimonials ---------- */
  var quotes = Array.prototype.slice.call(document.querySelectorAll(".quote"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".dot"));
  var qi = 0;
  var timer = null;
  var DELAY = 6500;

  function goto(i) {
    qi = (i + quotes.length) % quotes.length;
    quotes.forEach(function (q, n) { q.classList.toggle("is-active", n === qi); });
    dots.forEach(function (d, n) { d.setAttribute("aria-selected", n === qi ? "true" : "false"); });
  }
  function play() { if (!reduced && quotes.length > 1) timer = setInterval(function () { goto(qi + 1); }, DELAY); }
  function pause() { clearInterval(timer); }

  dots.forEach(function (d, i) {
    d.addEventListener("click", function () { pause(); goto(i); play(); });
  });
  var stage = document.querySelector(".quotes");
  if (stage) {
    stage.addEventListener("mouseenter", pause);
    stage.addEventListener("mouseleave", play);
    stage.addEventListener("focusin", pause);
  }
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) pause(); else { pause(); play(); }
  });
  goto(0);
  play();
})();
