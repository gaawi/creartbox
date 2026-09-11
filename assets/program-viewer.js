/* Concert programme viewer.
 *
 * The booklet is saddle-stitched, so it reads the way it is printed: the
 * cover on its own, then two facing pages at a time, then the back cover
 * on its own. Below 760px there is no room for a spread, so it turns one
 * page at a time. The pages are images rendered from the PDF by
 * tools/build_program_viewer.py; nothing is parsed in the browser.
 */
(function () {
  var root = document.querySelector("[data-program]");
  if (!root) return;

  var PAGES = parseInt(root.getAttribute("data-pages"), 10) || 0;
  var DIR = root.getAttribute("data-dir");
  var RATIO = parseFloat(root.getAttribute("data-ratio")) || 0.647;
  var TITLE = root.getAttribute("data-title") || "Programme";
  var PW = parseInt(root.getAttribute("data-pw"), 10) || 990;
  var PH = parseInt(root.getAttribute("data-ph"), 10) || 1530;
  if (!PAGES) return;

  var book = root.querySelector("[data-pv-book]");
  var stage = root.querySelector("[data-pv-stage]");
  var countEl = root.querySelector("[data-pv-count]");
  var strip = root.querySelector("[data-pv-strip]");
  var btnPrev = root.querySelector("[data-pv-prev]");
  var btnNext = root.querySelector("[data-pv-next]");
  var btnThumbs = root.querySelector("[data-pv-thumbs]");
  var btnZoom = root.querySelector("[data-pv-zoom]");
  var btnFull = root.querySelector("[data-pv-full]");

  var wide = window.matchMedia("(min-width: 761px)");
  var spread = wide.matches;
  var index = 0;        // index into the list of views
  var zoomed = false;

  function num(n) { return n < 10 ? "0" + n : "" + n; }
  function src(n) { return DIR + "/p" + num(n) + ".jpg"; }
  function thumb(n) { return DIR + "/t" + num(n) + ".jpg"; }

  /* What is on screen at once: [1], [2,3], [4,5] ... and whatever is
     left at the end - [16] for an even booklet, a last spread for an odd
     one. The cover is always alone, as it is on the printed copy. */
  function views() {
    var out = [];
    if (!spread) {
      for (var i = 1; i <= PAGES; i++) out.push([i]);
      return out;
    }
    out.push([1]);
    for (var p = 2; p <= PAGES; p += 2) {
      out.push(p + 1 <= PAGES ? [p, p + 1] : [p]);
    }
    return out;
  }

  var VIEWS = views();

  function viewOf(page) {
    for (var i = 0; i < VIEWS.length; i++) {
      if (VIEWS[i].indexOf(page) > -1) return i;
    }
    return 0;
  }

  function label() {
    var v = VIEWS[index];
    return (v.length === 2 ? v[0] + "-" + v[1] : v[0]) + " / " + PAGES;
  }

  /* Only the pages in view and their neighbours are fetched, so opening
     the page does not pull the whole booklet down the wire. */
  function preload() {
    var near = [index - 1, index, index + 1];
    near.forEach(function (i) {
      if (i < 0 || i >= VIEWS.length) return;
      VIEWS[i].forEach(function (p) { new Image().src = src(p); });
    });
  }

  function render() {
    book.innerHTML = "";
    book.classList.toggle("is-spread", VIEWS[index].length === 2);
    VIEWS[index].forEach(function (p) {
      var fig = document.createElement("div");
      fig.className = "pv-leaf";
      var img = document.createElement("img");
      // the rendered size, so the box is reserved before the file lands
      img.width = PW;
      img.height = PH;
      img.src = src(p);
      img.alt = TITLE + ", page " + p;
      img.draggable = false;
      fig.appendChild(img);
      book.appendChild(fig);
    });
    countEl.textContent = label();
    btnPrev.disabled = index === 0;
    btnNext.disabled = index === VIEWS.length - 1;
    if (strip && !strip.hidden) markThumbs();
    preload();
  }

  function go(i) {
    var next = Math.max(0, Math.min(VIEWS.length - 1, i));
    if (next === index) return;
    index = next;
    if (zoomed) setZoom(false);
    render();
  }

  btnPrev.addEventListener("click", function () { go(index - 1); });
  btnNext.addEventListener("click", function () { go(index + 1); });

  /* Re-lay the booklet when the screen crosses the spread threshold,
     keeping the reader on the page they were looking at. */
  function onWidth() {
    var now = wide.matches;
    if (now === spread) return;
    var current = VIEWS[index][0];
    spread = now;
    VIEWS = views();
    index = viewOf(current);
    render();
    if (strip && !strip.hidden) markThumbs();
  }
  if (wide.addEventListener) wide.addEventListener("change", onWidth);
  else wide.addListener(onWidth);

  /* ---- thumbnails ------------------------------------------------- */
  function buildThumbs() {
    if (strip.childElementCount) return;
    for (var p = 1; p <= PAGES; p++) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "pv-thumb";
      b.setAttribute("data-page", p);
      b.innerHTML = '<img src="' + thumb(p) + '" alt="" loading="lazy">' +
        '<span>' + p + '</span>';
      strip.appendChild(b);
    }
    strip.addEventListener("click", function (e) {
      var b = e.target.closest(".pv-thumb");
      if (!b) return;
      go(viewOf(parseInt(b.getAttribute("data-page"), 10)));
    });
  }

  function markThumbs() {
    var on = VIEWS[index];
    strip.querySelectorAll(".pv-thumb").forEach(function (b) {
      var p = parseInt(b.getAttribute("data-page"), 10);
      b.classList.toggle("on", on.indexOf(p) > -1);
    });
  }

  btnThumbs.addEventListener("click", function () {
    buildThumbs();
    var open = strip.hidden;
    strip.hidden = !open;
    btnThumbs.setAttribute("aria-expanded", String(open));
    btnThumbs.textContent = open ? "Hide pages" : "All pages";
    if (open) markThumbs();
  });

  /* ---- zoom -------------------------------------------------------- */
  function setZoom(on) {
    zoomed = on;
    root.classList.toggle("is-zoomed", on);
    btnZoom.setAttribute("aria-pressed", String(on));
    btnZoom.textContent = on ? "Fit page" : "Zoom";
    if (!on) {
      book.style.transform = "";
      book.style.transformOrigin = "";
    }
  }
  btnZoom.addEventListener("click", function () { setZoom(!zoomed); });

  /* While zoomed the pointer moves the magnified page rather than
     scrolling the window, which is what a phone expects here. */
  function pan(e) {
    if (!zoomed) return;
    var point = e.touches ? e.touches[0] : e;
    var box = stage.getBoundingClientRect();
    var x = Math.max(0, Math.min(1, (point.clientX - box.left) / box.width));
    var y = Math.max(0, Math.min(1, (point.clientY - box.top) / box.height));
    book.style.transformOrigin = (x * 100) + "% " + (y * 100) + "%";
    book.style.transform = "scale(2)";
  }
  stage.addEventListener("mousemove", pan);
  stage.addEventListener("touchmove", function (e) {
    if (!zoomed) return;
    e.preventDefault();
    pan(e);
  }, { passive: false });

  /* ---- full screen -------------------------------------------------- */
  btnFull.addEventListener("click", function () {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (root.requestFullscreen) {
      root.requestFullscreen();
    }
  });
  document.addEventListener("fullscreenchange", function () {
    var on = document.fullscreenElement === root;
    root.classList.toggle("is-full", on);
    btnFull.textContent = on ? "Leave full screen" : "Full screen";
  });

  /* ---- keyboard and swipe -------------------------------------------- */
  document.addEventListener("keydown", function (e) {
    if (/^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || ""))) return;
    if (e.key === "ArrowLeft") { go(index - 1); }
    else if (e.key === "ArrowRight") { go(index + 1); }
    else if (e.key === "Home") { go(0); }
    else if (e.key === "End") { go(VIEWS.length - 1); }
    else if (e.key === "Escape" && zoomed) { setZoom(false); }
    else return;
    e.preventDefault();
  });

  var startX = null, startY = null;
  stage.addEventListener("touchstart", function (e) {
    if (zoomed || e.touches.length !== 1) return;
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
  }, { passive: true });
  stage.addEventListener("touchend", function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    var dy = e.changedTouches[0].clientY - startY;
    // a vertical drag is the reader scrolling the page, not turning one
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.6) {
      go(index + (dx < 0 ? 1 : -1));
    }
    startX = startY = null;
  }, { passive: true });

  render();
})();
