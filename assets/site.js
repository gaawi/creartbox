/* === CreArtBox · site.js - small, dependency-free interactions === */

/* ----- Eventbrite ticket URL config ----------------------------------
   Each event used on the site has a stable id (data-event="..."). To
   wire a real Eventbrite event, set its URL here. Until then, the link
   falls back to the Eventbrite organiser page.
---------------------------------------------------------------------- */
const EVENTBRITE_ORG = "https://www.eventbrite.com/o/creartbox";
const EVENTBRITE = {
  "threshold-2026-06-06": EVENTBRITE_ORG,
  "tworoads-2026-09-18": EVENTBRITE_ORG,
  "afterlight-2026-10-04": EVENTBRITE_ORG,
  "noctum-2026-11-14": EVENTBRITE_ORG,
  "winter-2026-12-11": EVENTBRITE_ORG,
  "awave-2027-02-06": EVENTBRITE_ORG,
  "season-subscription": EVENTBRITE_ORG,
};

/* ----- Donate URL config - Stripe Payment Links ----------------------
   Three Stripe Payment Links (one per frequency). The donate form picks
   the right one based on the selected frequency and appends the amount
   as a Stripe pre-fill param (Stripe accepts ?prefilled_promo_code= but
   amounts via Payment Links require pre-built variants OR Checkout). For
   custom amounts the donate form falls back to a generic Payment Link.

   To wire real Stripe URLs:
     1. In your Stripe dashboard, create three Payment Links with
        "Customer chooses amount" enabled - one for one-time, one for
        monthly, one for annual.
     2. Replace the URLs below.

   Until then, the buttons open an email so you don't lose donors. */
const DONATE_LINKS = {
  once:    "mailto:info@creartbox.nyc?subject=Donation%20to%20CreArtBox%20%28one-time%29",
  monthly: "mailto:info@creartbox.nyc?subject=Donation%20to%20CreArtBox%20%28monthly%29",
  annual:  "mailto:info@creartbox.nyc?subject=Donation%20to%20CreArtBox%20%28annual%29",
};
const DONATE_URL = DONATE_LINKS.once;

/* Dark mode is the only mode. Set the attribute once and forget. */
document.documentElement.setAttribute("data-theme", "dark");

document.addEventListener("DOMContentLoaded", function () {

  // Mobile menu
  const burger = document.querySelector(".nav-burger");
  const navInner = document.querySelector(".nav-strip-inner");
  if (burger && navInner) {
    burger.addEventListener("click", () => navInner.classList.toggle("open"));
  }

  // Mobile per-page pill sub-nav (built from the active page's dropdown)
  initPagePills();

  // Ensemble member cards: open full bio in a modal on mobile
  initMemberCards();

  // Copy-bio buttons under each bio version
  initBioCopy();

  // Persistent audio dock (background play across pages)
  initAudioDock();

  // Wire ticket buttons: [data-event="..."] => Eventbrite URL
  document.querySelectorAll("[data-event]").forEach((el) => {
    const id = el.getAttribute("data-event");
    const url = EVENTBRITE[id] || EVENTBRITE_ORG;
    el.setAttribute("href", url);
    el.setAttribute("target", "_blank");
    el.setAttribute("rel", "noopener");
  });

  // Wire donate buttons
  document.querySelectorAll("[data-donate]").forEach((el) => {
    el.setAttribute("href", DONATE_URL);
  });

  // Classifieds (opportunities)
  document.querySelectorAll(".classified").forEach((c) => {
    const btn = c.querySelector("[data-toggle-classified]");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const isOpen = c.classList.toggle("open");
      btn.querySelector(".lbl").textContent = isOpen ? "Hide details" : "Read & apply";
      btn.querySelector(".ar").textContent = isOpen ? "↑" : "↓";
    });
  });

  // Donate calculator
  initDonate();

  // Concert filter tabs
  initConcertTabs();

  // Transparent masthead → solid on scroll past hero
  initTransparentMasthead();

  // Bio version tabs
  initBioTabs();

  // Archive "View Program" modals
  initArchiveModals();

  // Archive cards: full-card click target
  initArchiveCardLinks();

  // Video modal (media page)
  initVideoModal();

  // "Show all photos" modal (archive subpages)
  initAllPhotosModal();

  // Mobile gallery counter (event-media carousel)
  initEventMediaCounter();

  // Composer roster cards open a bio modal
  initComposerRoster();
});

function initEventMediaCounter() {
  // Selector covers archive event carousels AND the Media-page Photographs grid
  const targets = [
    { gridSel: ".event-media .g-grid",  containerSel: ".event-media", itemSel: ".g-item" },
    { gridSel: ".photo-cat .photo-row", containerSel: ".photo-cat",   itemSel: ":scope > div" },
  ];
  targets.forEach((t) => attachCounter(t.gridSel, t.containerSel, t.itemSel));
}

function attachCounter(gridSel, containerSel, itemSel) {
  document.querySelectorAll(gridSel).forEach((grid) => {
    const items = grid.querySelectorAll(itemSel);
    if (items.length < 2) return;
    const section = grid.closest(containerSel);
    if (!section) return;
    // Need a positioned container for the absolute counter
    const cs = getComputedStyle(section);
    if (cs.position === "static") section.style.position = "relative";
    // Add counter pill
    const counter = document.createElement("div");
    counter.className = "g-counter";
    counter.textContent = "1 / " + items.length;
    section.appendChild(counter);
    // Update on scroll
    let raf = null;
    grid.addEventListener("scroll", () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = null;
        const center = grid.scrollLeft + grid.clientWidth / 2;
        let active = 0;
        let bestDist = Infinity;
        items.forEach((it, i) => {
          const mid = it.offsetLeft + it.clientWidth / 2;
          const d = Math.abs(mid - center);
          if (d < bestDist) { bestDist = d; active = i; }
        });
        counter.textContent = (active + 1) + " / " + items.length;
      });
    }, { passive: true });
  });
}

function initPagePills() {
  // Build a horizontal pill sub-nav for the current page from its
  // dropdown submenu. Mobile-only (CSS hides it on desktop).
  const main = document.querySelector("main");
  if (!main) return;
  // Skip pages that already have their own functional sub-nav
  // (e.g. concerts.html filter tabs) — page-pills would duplicate them.
  if (main.querySelector("[data-concert-tab]")) return;
  // Find the nav-item whose top-level link is marked active.
  let activeItem = null;
  document.querySelectorAll(".nav-strip-inner .nav-item").forEach((item) => {
    const top = item.querySelector(":scope > a");
    if (top && top.classList.contains("active")) activeItem = item;
  });
  if (!activeItem) return;
  const links = activeItem.querySelectorAll(".submenu a");
  if (!links.length) return;

  const nav = document.createElement("nav");
  nav.className = "page-pills";
  const row = document.createElement("div");
  row.className = "page-pills-row";
  links.forEach((a) => {
    const pill = document.createElement("a");
    pill.href = a.getAttribute("href");
    pill.textContent = a.textContent.trim();
    if (a.target) { pill.target = a.target; pill.rel = a.rel || "noopener"; }
    row.appendChild(pill);
  });
  nav.appendChild(row);
  main.insertBefore(nav, main.firstChild);
}

function initMemberCards() {
  const articles = document.querySelectorAll("#ensemble article");
  if (!articles.length) return;

  // Build the modal once
  const modal = document.createElement("div");
  modal.className = "member-modal";
  modal.setAttribute("aria-hidden", "true");
  modal.setAttribute("role", "dialog");
  modal.innerHTML =
    '<div class="member-modal-bg" data-mm-close></div>' +
    '<div class="member-modal-content">' +
      '<button class="member-modal-close" data-mm-close aria-label="Close">×</button>' +
      '<div class="member-modal-body"></div>' +
    '</div>';
  document.body.appendChild(modal);
  const body = modal.querySelector(".member-modal-body");
  const mql = window.matchMedia("(max-width: 860px)");

  function close() {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }
  function open(article) {
    body.innerHTML = article.innerHTML;
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const content = modal.querySelector(".member-modal-content");
    if (content) content.scrollTop = 0;
  }
  modal.querySelectorAll("[data-mm-close]").forEach((el) =>
    el.addEventListener("click", close)
  );
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("open")) close();
  });

  articles.forEach((art) => {
    // Promote the role label into an instrument chip on the photo
    const labelEl = art.querySelector(".label");
    const fig = art.querySelector("figure");
    if (labelEl && fig && !fig.querySelector(".member-instrument")) {
      const instrument = (labelEl.textContent.split("·")[0] || "").trim();
      if (instrument) {
        const chip = document.createElement("div");
        chip.className = "member-instrument";
        chip.textContent = instrument;
        fig.appendChild(chip);
      }
    }
    // Make the entire card a tap target on mobile (role=button for a11y)
    art.setAttribute("tabindex", "0");
    art.setAttribute("role", "button");
    const handler = (e) => {
      if (!mql.matches) return;
      if (e.target.closest("a, button")) return;
      e.preventDefault();
      open(art);
    };
    art.addEventListener("click", handler);
    art.addEventListener("keydown", (e) => {
      if (!mql.matches) return;
      if (e.key === "Enter" || e.key === " ") {
        if (e.target.closest("a, button")) return;
        e.preventDefault();
        open(art);
      }
    });
  });
}

function initBioCopy() {
  const buttons = document.querySelectorAll(".bio-copy");
  if (!buttons.length) return;
  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const key = btn.getAttribute("data-bio-copy");
      const version = document.querySelector(
        '[data-bio-version="' + key + '"]'
      );
      if (!version) return;
      // Pull plain text from the inner paragraphs, preserving paragraph breaks
      const paras = Array.from(version.querySelectorAll("p")).map((p) =>
        p.textContent.replace(/\s+/g, " ").trim()
      );
      const text = paras.join("\n\n");
      const label = btn.querySelector(".bc-label");
      const original = label ? label.textContent : "Copy bio";
      let ok = false;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(text);
          ok = true;
        } else {
          // Fallback for older browsers / non-https
          const ta = document.createElement("textarea");
          ta.value = text;
          ta.setAttribute("readonly", "");
          ta.style.position = "fixed";
          ta.style.opacity = "0";
          document.body.appendChild(ta);
          ta.select();
          ok = document.execCommand("copy");
          document.body.removeChild(ta);
        }
      } catch (_) { ok = false; }
      btn.classList.add("copied");
      if (label) label.textContent = ok ? "Copied" : "Copy failed";
      setTimeout(() => {
        btn.classList.remove("copied");
        if (label) label.textContent = original;
      }, 2000);
    });
  });
}

function initAllPhotosModal() {
  const btn = document.getElementById("allphotos-btn");
  const modal = document.getElementById("allphotos-modal");
  if (!btn || !modal) return;
  function open() {
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function close() {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }
  btn.addEventListener("click", open);
  modal.querySelectorAll("[data-allphotos-close]").forEach((el) => {
    el.addEventListener("click", close);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("open")) close();
  });
}

function initVideoModal() {
  const modal = document.getElementById("video-modal");
  if (!modal) return;
  const frame = modal.querySelector(".video-modal-frame");
  const caption = modal.querySelector(".video-modal-caption");
  let hlsInstance = null;

  function loadHlsLib() {
    return new Promise((resolve) => {
      if (window.Hls) return resolve(window.Hls);
      const s = document.createElement("script");
      s.src = "https://cdn.jsdelivr.net/npm/hls.js@1.5.13/dist/hls.min.js";
      s.onload = () => resolve(window.Hls);
      s.onerror = () => resolve(null);
      document.head.appendChild(s);
    });
  }

  async function playHls(url) {
    const video = document.createElement("video");
    video.controls = true;
    video.autoplay = true;
    video.playsInline = true;
    frame.innerHTML = "";
    frame.appendChild(video);
    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = url;
    } else {
      const Hls = await loadHlsLib();
      if (Hls && Hls.isSupported()) {
        hlsInstance = new Hls();
        hlsInstance.loadSource(url);
        hlsInstance.attachMedia(video);
      } else {
        video.src = url;
      }
    }
  }

  function open(btn) {
    const src = btn.getAttribute("data-video-src");
    const yt = btn.getAttribute("data-video-yt");
    const title = btn.getAttribute("data-video-title") || "";

    if (src && /\.m3u8(\?|$)/i.test(src)) {
      playHls(src);
    } else if (src && /\.(mp4|webm)(\?|$)/i.test(src)) {
      frame.innerHTML = '<video src="' + src + '" controls autoplay playsinline></video>';
    } else if (src) {
      frame.innerHTML = '<iframe src="' + src + '" allow="autoplay; fullscreen; picture-in-picture; encrypted-media" allowfullscreen></iframe>';
    } else if (yt) {
      const embedUrl = "https://www.youtube-nocookie.com/embed/" + yt + "?autoplay=1&rel=0";
      frame.innerHTML = '<iframe src="' + embedUrl + '" allow="autoplay; fullscreen; picture-in-picture; encrypted-media" allowfullscreen></iframe>';
    } else {
      return;
    }
    caption.textContent = title;
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function close() {
    if (hlsInstance) { hlsInstance.destroy(); hlsInstance = null; }
    frame.innerHTML = "";
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  document.querySelectorAll(".video-trigger").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      open(btn);
    });
  });
  modal.querySelectorAll("[data-video-close]").forEach((el) => {
    el.addEventListener("click", close);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("open")) close();
  });
}

function initArchiveCardLinks() {
  document.querySelectorAll(".eventpast").forEach((card) => {
    const link = card.querySelector(".explore a.button");
    const modalBtn = card.querySelector(".myBtn_multi");
    if (!link && !modalBtn) return;
    card.classList.add("eventpast-linked");
    card.style.cursor = "pointer";
    card.addEventListener("click", (e) => {
      // Let clicks on actual links, buttons, or inside a modal pass through
      if (e.target.closest("a, button, .modal")) return;
      if (link) {
        if (e.metaKey || e.ctrlKey || e.button === 1) {
          window.open(link.href, "_blank");
        } else {
          window.location.href = link.href;
        }
      } else if (modalBtn) {
        modalBtn.click();
      }
    });
    card.setAttribute("tabindex", "0");
    card.setAttribute("role", "link");
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        if (link) {
          window.location.href = link.href;
        } else if (modalBtn) {
          modalBtn.click();
        }
      }
    });
  });
}

function initArchiveModals() {
  const btns = document.querySelectorAll(".myBtn_multi");
  if (!btns.length) return;
  btns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const modal = btn.nextElementSibling && btn.nextElementSibling.classList.contains("modal")
        ? btn.nextElementSibling
        : btn.parentElement.querySelector(".modal");
      if (modal) {
        modal.style.display = "block";
        document.body.style.overflow = "hidden";
      }
    });
  });
  document.querySelectorAll(".close_multi").forEach((c) => {
    c.addEventListener("click", () => {
      const m = c.closest(".modal");
      if (m) m.style.display = "none";
      document.body.style.overflow = "";
    });
  });
  document.querySelectorAll(".modal").forEach((m) => {
    m.addEventListener("click", (e) => {
      if (e.target === m) {
        m.style.display = "none";
        document.body.style.overflow = "";
      }
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal").forEach((m) => (m.style.display = "none"));
      document.body.style.overflow = "";
    }
  });
}

function initBioTabs() {
  const tabs = document.querySelectorAll("[data-bio-tab]");
  if (!tabs.length) return;
  const versions = document.querySelectorAll("[data-bio-version]");
  const downloads = document.querySelectorAll("[data-bio-download]");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const v = tab.getAttribute("data-bio-tab");
      tabs.forEach((t) => t.classList.toggle("active", t === tab));
      versions.forEach((d) => { d.hidden = d.getAttribute("data-bio-version") !== v; });
      downloads.forEach((d) => { d.style.display = d.getAttribute("data-bio-download") === v ? "" : "none"; });
    });
  });
}

function initTransparentMasthead() {
  if (!document.body.classList.contains("hero-transparent")) return;
  const masthead = document.querySelector(".masthead");
  if (!masthead) return;
  const onScroll = () => {
    const threshold = Math.min(window.innerHeight * 0.6, 540);
    masthead.classList.toggle("scrolled", window.scrollY > threshold);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

/* ----- Donate calculator --------------------------------------------- */
function initDonate() {
  const form = document.querySelector("[data-donate-form]");
  if (!form) return;
  let amount = 250;
  let freq = "once";
  let custom = "";
  const activeAmt = form.querySelector("[data-amt] button.active");
  if (activeAmt) amount = Number(activeAmt.getAttribute("data-val")) || amount;

  const freqBtns = form.querySelectorAll("[data-freq] button");
  const amtBtns = form.querySelectorAll("[data-amt] button");
  const customInput = form.querySelector("[data-custom]");
  const submit = form.querySelector("[data-submit]");
  const rows = document.querySelectorAll("[data-impact-row]");

  function update() {
    const final = Number(custom) || amount || 0;
    submit.querySelector(".lbl").textContent =
      "Give $" + final + (freq !== "once" ? " / " + (freq === "monthly" ? "month" : "year") : "");
    rows.forEach((r) => {
      const min = Number(r.getAttribute("data-impact-min"));
      const active = final >= min;
      r.classList.toggle("inactive", !active);
      const c = r.querySelector(".check");
      if (c) {
        c.classList.toggle("on", active);
        c.textContent = active ? "✓" : "○";
      }
    });
    const base = DONATE_LINKS[freq] || DONATE_URL;
    const sep = base.includes("?") ? "&" : "?";
    submit.setAttribute("href", base + sep + "amount=" + final + "&frequency=" + freq);
  }

  freqBtns.forEach((b) => {
    b.addEventListener("click", () => {
      freq = b.getAttribute("data-val");
      freqBtns.forEach((x) => x.classList.toggle("active", x === b));
      update();
    });
  });
  amtBtns.forEach((b) => {
    b.addEventListener("click", () => {
      amount = Number(b.getAttribute("data-val"));
      custom = "";
      if (customInput) customInput.value = "";
      amtBtns.forEach((x) => x.classList.toggle("active", x === b));
      update();
    });
  });
  if (customInput) {
    customInput.addEventListener("input", (e) => {
      custom = e.target.value;
      amtBtns.forEach((x) => x.classList.remove("active"));
      update();
    });
  }
  update();
}

/* ----- Concert filter tabs ------------------------------------------- */
function initConcertTabs() {
  const tabs = document.querySelectorAll("[data-concert-tab]");
  const rows = document.querySelectorAll("[data-concert-series]");
  if (!tabs.length) return;
  tabs.forEach((t) => {
    t.addEventListener("click", () => {
      const v = t.getAttribute("data-concert-tab");
      tabs.forEach((x) => x.classList.toggle("active", x === t));
      let shown = 0;
      rows.forEach((r) => {
        const series = r.getAttribute("data-concert-series");
        const show = v === "all" || series === v;
        r.style.display = show ? "" : "none";
        if (show) shown++;
      });
      const count = document.querySelector("[data-concert-count]");
      if (count) count.textContent = "Showing " + shown + " of " + rows.length + " concerts";
    });
  });
}

/* ============================================================
   PERSISTENT AUDIO DOCK
   - Track list (#featured-tracks) on the media page selects + plays
   - A single <audio> element lives on every page (created on demand)
   - Playlist + index + currentTime persist across navigation via
     sessionStorage (currentTime) + localStorage (queue + playing state)
   ============================================================ */
const AUDIO_KEY = "cb-audio-v1";
function readAudioState() {
  try {
    const raw = localStorage.getItem(AUDIO_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (_) { return null; }
}
function writeAudioState(s) {
  try { localStorage.setItem(AUDIO_KEY, JSON.stringify(s)); } catch (_) {}
}
function fmtTime(t) {
  if (!isFinite(t) || t < 0) t = 0;
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return m + ":" + (s < 10 ? "0" : "") + s;
}

function initAudioDock() {
  const dock = document.getElementById("audio-dock");
  if (!dock) return;

  // Build the single <audio> tag and reuse it
  let audio = document.getElementById("cb-audio-el");
  if (!audio) {
    audio = document.createElement("audio");
    audio.id = "cb-audio-el";
    audio.preload = "metadata";
    document.body.appendChild(audio);
  }

  // Hydrate queue: prefer the page's track list, else fall back to saved state
  const tracksUI = Array.from(document.querySelectorAll("#featured-tracks .track"));
  let queue = tracksUI.map((li) => ({
    src: li.getAttribute("data-track-src"),
    composer: li.getAttribute("data-track-composer") || "",
    title: li.getAttribute("data-track-title") || "",
    note: li.getAttribute("data-track-note") || "",
  }));
  let saved = readAudioState();
  if (!queue.length && saved && saved.queue) queue = saved.queue;

  let idx = (saved && Number.isInteger(saved.idx)) ? saved.idx : -1;
  // currentTime resumes within the same browser session
  const resumeT = parseFloat(sessionStorage.getItem("cb-audio-t") || "0") || 0;
  let wasPlaying = !!(saved && saved.playing);

  const elComposer = dock.querySelector("[data-ad-composer]");
  const elTitle = dock.querySelector("[data-ad-title]");
  const elFill = dock.querySelector("[data-ad-fill]");
  const elCur = dock.querySelector("[data-ad-t-cur]");
  const elDur = dock.querySelector("[data-ad-t-dur]");
  const btnPlay = dock.querySelector("[data-ad-play]");
  const btnPrev = dock.querySelector("[data-ad-prev]");
  const btnNext = dock.querySelector("[data-ad-next]");
  const btnClose = dock.querySelector("[data-ad-close]");
  const bar = dock.querySelector("[data-ad-progress] .ad-bar");

  function showDock() {
    dock.hidden = false;
    document.body.classList.add("has-audio-dock");
  }
  function hideDock() {
    dock.hidden = true;
    document.body.classList.remove("has-audio-dock");
  }
  function reflectListUI() {
    tracksUI.forEach((li, i) => li.classList.toggle("playing", i === idx && !audio.paused));
  }
  function load(i, autoplay) {
    if (i < 0 || i >= queue.length) return;
    idx = i;
    const t = queue[i];
    if (audio.src !== t.src) audio.src = t.src;
    elComposer.textContent = t.composer || "—";
    elTitle.textContent = t.title || "";
    showDock();
    persist();
    if (autoplay) audio.play().catch(() => {});
  }
  function togglePlay() {
    if (idx < 0 && queue.length) { load(0, true); return; }
    if (audio.paused) audio.play().catch(() => {}); else audio.pause();
  }
  function next() {
    if (idx + 1 < queue.length) load(idx + 1, true);
  }
  function prev() {
    if (audio.currentTime > 3) { audio.currentTime = 0; return; }
    if (idx > 0) load(idx - 1, true);
  }
  function persist() {
    writeAudioState({ queue, idx, playing: !audio.paused });
  }

  // Wire up the page track list (clicks)
  tracksUI.forEach((li, i) => {
    li.addEventListener("click", (e) => {
      e.preventDefault();
      // If clicking the same track that's playing, toggle
      if (i === idx) togglePlay();
      else load(i, true);
    });
    // Also stop propagation on the inner button (kept for a11y)
    const inner = li.querySelector(".track-play");
    if (inner) inner.addEventListener("click", (e) => { e.stopPropagation(); li.click(); });
  });

  // Dock controls
  btnPlay.addEventListener("click", togglePlay);
  btnNext.addEventListener("click", next);
  btnPrev.addEventListener("click", prev);
  btnClose.addEventListener("click", () => {
    audio.pause();
    audio.removeAttribute("src");
    sessionStorage.removeItem("cb-audio-t");
    localStorage.removeItem(AUDIO_KEY);
    hideDock();
  });

  // Progress bar scrubbing
  bar.addEventListener("click", (e) => {
    const r = bar.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    if (isFinite(audio.duration)) audio.currentTime = pct * audio.duration;
  });

  audio.addEventListener("timeupdate", () => {
    if (isFinite(audio.duration) && audio.duration > 0) {
      elFill.style.width = (audio.currentTime / audio.duration * 100) + "%";
    }
    elCur.textContent = fmtTime(audio.currentTime);
    sessionStorage.setItem("cb-audio-t", String(audio.currentTime));
  });
  audio.addEventListener("loadedmetadata", () => { elDur.textContent = fmtTime(audio.duration); });
  audio.addEventListener("play", () => { dock.classList.add("playing"); reflectListUI(); persist(); });
  audio.addEventListener("pause", () => { dock.classList.remove("playing"); reflectListUI(); persist(); });
  audio.addEventListener("ended", () => { next(); });

  // Hydrate UI from saved state on load
  if (queue.length && idx >= 0 && idx < queue.length) {
    load(idx, false);
    if (resumeT > 0) audio.currentTime = resumeT;
    if (wasPlaying) {
      // Show an in-dock "Resuming your audio…" loading state, then
      // morph into the normal player view once playback resumes.
      const overlay = document.createElement("div");
      overlay.className = "ad-resuming-overlay";
      overlay.innerHTML =
        '<span class="ad-resuming-label">Resuming your audio</span>' +
        '<span class="ad-resuming-dots"><i></i><i></i><i></i></span>' +
        '<span class="ad-resuming-bar"><i></i></span>';
      dock.appendChild(overlay);
      dock.classList.add("ad-is-resuming");

      let cleared = false;
      const clear = () => {
        if (cleared) return;
        cleared = true;
        dock.classList.remove("ad-is-resuming");
        overlay.classList.add("ad-resuming-out");
        setTimeout(() => overlay.remove(), 320);
      };
      // Clear when audio is actually rolling — or after a safety timeout.
      audio.addEventListener("playing", clear, { once: true });
      setTimeout(clear, 2400);

      const playPromise = audio.play();
      if (playPromise && typeof playPromise.then === "function") {
        playPromise.catch(() => {
          // Autoplay blocked — turn the loader into a hint
          overlay.querySelector(".ad-resuming-label").textContent = "Tap play to resume";
          overlay.querySelector(".ad-resuming-bar").style.display = "none";
          overlay.querySelector(".ad-resuming-dots").style.display = "none";
        });
      }
    }
  }
}

/* === Composer roster: tap a name to open a bio modal ================= */
const COMPOSERS = {
  "Brittney Benton": {
    photo: "https://images.squarespace-cdn.com/content/v1/61882168ea70585aab41a750/c201892f-260d-41e0-8529-61fc9ccee630/Brittney+Benton+Headshot.png",
    website: "https://brittneybentonmusic.wixsite.com/composer",
    base: "Las Vegas, NV",
    bio: "Driven by storytelling and imagery, Brittney Benton's music takes listeners through a lush melodic and harmonic soundscape filled with personality. She holds a Bachelor's degree in Music Composition with a Minor in Music Technology from the University of Nevada, Las Vegas. Her works have been performed by the Bellevue Chamber Chorus, ZOFO, the Beo String Quartet, the Lowell Chamber Orchestra, and the Armenian State Symphony Orchestra."
  },
  "Alex Burtzos": {
    photo: "https://images.squarespace-cdn.com/content/v1/57630abfbe659492f03a09d1/797ad90a-8d2a-4c04-b72e-6a179863ffae/Alex+Burtzos+2024+-+3.jpg",
    website: "https://alexburtzosmusic.com",
    base: "New York City / Orlando",
    bio: "Alex Burtzos is an American composer, conductor, and educator based in New York City and Orlando whose music has been performed across four continents by leading contemporary soloists and ensembles. He is the founder and artistic director of ICEBERG New Music, a NYC composer collective established in 2016, and serves as Associate Professor and Endowed Chair of Composition at the University of Central Florida."
  },
  "Oliver Caplan": {
    photo: "https://www.olivercaplan.com/images/oliver.jpg",
    website: "https://www.olivercaplan.com/",
    base: "Medford, Massachusetts",
    bio: "Oliver Caplan is an award-winning American composer who offers a voice of hope in an uncertain world. Inspired by the resiliency of the human spirit and the beauty of the natural world, his music celebrates stories of social justice, conservation, and community."
  },
  "Luke Carlson": {
    photo: "https://www.lukecarlsonmusic.com/css/images/headshot-1.jpg",
    website: "https://www.lukecarlsonmusic.com/",
    base: "Branson, Missouri",
    bio: "Luke Carlson (b. 1983) is an American composer and conductor whose music has been praised by the New York Times as \"personal and strong,\" by the Philadelphia Inquirer as \"magical\" and \"otherworldly,\" and by the Washington Classical Review for its \"fascinating timbres.\" He serves as Associate Professor of Music at the College of the Ozarks."
  },
  "Devin Cholodenko": {
    photo: "https://images.squarespace-cdn.com/content/v1/60528ee1b13334437997346f/b2efdd45-30a2-4891-8617-d1dd4334e66d/Devin+Cholodenko+Portraits.jpg",
    website: "https://www.devincholodenko.com/",
    base: "Miami, Florida",
    bio: "Devin Cholodenko is a composer of eclectic taste and signature style whose work centers on introspection and inner emotional experience, drawing inspiration from time, memory, nature, classical mythology, and identity. His music has been performed by ensembles including the JACK Quartet, HUB New Music, and Momenta Quartet."
  },
  "Gilad Cohen": {
    photo: "https://images.squarespace-cdn.com/content/v1/5ec82ae63a4a862322e61ce6/1590602918491-9VN9GPR2SW5BOZCBBCAS/headshot.giladcohen.jpg",
    website: "https://giladcohen.com/",
    base: "New Jersey",
    bio: "Gilad Cohen (b. 1980) is a composer, performer, and theorist whose work spans concert music, rock, and theater. His compositions draw on a wide range of influences, blending rock rhythms, impressionism, klezmer, and Arabic musical traditions. He holds a Ph.D. in Composition from Princeton University and serves as Associate Professor of Music at Ramapo College of New Jersey."
  },
  "Yurui (Rain) Hou": {
    photo: "https://www.newyorkcomposerscircle.org/composers/images/yurui-rain-hou/2025%20Yurui%20Rain%20Hou-1-topaz.jpg",
    website: null,
    base: "New York City",
    bio: "Yurui \"Rain\" Hou is a composer and fiction writer based in New York City, currently a student at Columbia University majoring in creative writing and minoring in music, while also studying composition with Melinda Wagner at The Juilliard School. Her works have been recognized as a finalist of the ASCAP Foundation Morton Gould Young Composer Competition and first-place winner of the Belvedere Chamber Music Festival 2024 Composition Contest."
  },
  "Eric Moe": {
    photo: "https://www.music.pitt.edu/sites/default/files/person-images/moe.jpg",
    website: "https://www.ericmoe.net/",
    base: "Pittsburgh, Pennsylvania",
    bio: "Eric Moe is the Andrew W. Mellon Professor of Composition and codirector of Music on the Edge at the University of Pittsburgh. A composer and pianist whose work the New York Times has praised for its \"winning exuberance,\" he writes acoustic and electroacoustic music that often incorporates theatrical elements such as video, text, and staging."
  },
  "Paul Novak": {
    photo: "https://paulnovakmusic.com/uploads/5/8/8/4/58843725/dsc-0569-v2_orig.jpg",
    website: "https://paulnovakmusic.com",
    base: "Chicago",
    bio: "Paul Novak is a Chicago-based composer and flutist whose \"spellbinding\" (Washington Post) music immerses listeners in shimmering, subtly crafted worlds of color, motion, light, and magic. His recent projects engage with dreams and memory, queer identity, climate change and the natural world, and psychosomatic illness."
  },
  "Zygmund de Somogyi": {
    photo: "https://static.wixstatic.com/media/555625_347f5c70bc7f4c2e8e3c97e892f4836c~mv2.jpeg",
    website: "https://www.zdscomposer.co.uk/",
    base: "London, UK",
    bio: "Zygmund de Somogyi is a British-Filipino composer and interdisciplinary artist whose work draws on punk rock influences and DIY ethics. They compose across contemporary classical, opera, theatre, film, and electronic music, exploring themes of online folklore, collaborative worldbuilding, queer identity, and metamodern aesthetics."
  },
  "Eli Tausen á Lava": {
    photo: "https://images.squarespace-cdn.com/content/v1/5c54a0eb92441b3bc683209a/77892be6-bd3a-4170-beab-d3bdfaacc6b4/Eli_Tausen_%C3%A1_Lava_Promo_Export_AKHC+1.jpg",
    website: "https://elitausenalava.com/",
    base: "Tórshavn, Faroe Islands",
    bio: "Eli Tausen á Lava is a Faroese composer, producer, pianist, and electronic musician, and a Nordic Council Music Prize nominee. Classically trained at the Malmö Academy of Music with a Master's from NYU, he has collaborated with the BBC Scottish Symphony Orchestra, George Enescu Philharmonic, and Helsingborg Symphony Orchestra."
  }
};

function initComposerRoster() {
  const roots = document.querySelectorAll(".roster-list li, .season-names span");
  if (!roots.length) return;

  // Build the modal once per page
  let modal = document.querySelector(".composer-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.className = "composer-modal";
    modal.setAttribute("aria-hidden", "true");
    modal.setAttribute("role", "dialog");
    modal.innerHTML =
      '<div class="composer-modal-bg" data-cm-close></div>' +
      '<div class="composer-modal-content">' +
        '<button class="composer-modal-close" data-cm-close aria-label="Close">×</button>' +
        '<div class="composer-modal-body"></div>' +
      '</div>';
    document.body.appendChild(modal);
    modal.querySelectorAll("[data-cm-close]").forEach((el) =>
      el.addEventListener("click", close)
    );
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("open")) close();
    });
  }
  const body = modal.querySelector(".composer-modal-body");

  function close() {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }
  function open(name, data) {
    const photoHtml = data.photo
      ? '<div class="cm-photo"><img src="' + data.photo + '" alt="' + name + '" loading="lazy"></div>'
      : '';
    const baseHtml = data.base
      ? '<div class="cm-meta">' + data.base + '</div>'
      : '';
    const websiteHtml = data.website
      ? '<a class="cm-link" href="' + data.website + '" target="_blank" rel="noopener">Visit website <span class="ar">→</span></a>'
      : '';
    body.innerHTML =
      photoHtml +
      '<div class="cm-text">' +
        '<h3 class="cm-name">' + name + '</h3>' +
        baseHtml +
        '<p class="cm-bio">' + data.bio + '</p>' +
        websiteHtml +
      '</div>';
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const content = modal.querySelector(".composer-modal-content");
    if (content) content.scrollTop = 0;
  }

  roots.forEach((el) => {
    // Use the name span inside .roster-list li, or the span text directly
    const nameEl = el.querySelector(".rl-name") || el;
    const name = (nameEl.textContent || "").trim();
    const data = COMPOSERS[name];
    if (!data) return;

    el.classList.add("has-composer-bio");
    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "button");

    // Inject thumbnail photo into the roster row (about §04 only)
    if (el.matches(".roster-list li") && data.photo && !el.querySelector(".rl-thumb")) {
      const thumb = document.createElement("span");
      thumb.className = "rl-thumb";
      thumb.innerHTML = '<img src="' + data.photo + '" alt="" loading="lazy">';
      el.prepend(thumb);
    }

    const onActivate = (e) => {
      e.preventDefault();
      open(name, data);
    };
    el.addEventListener("click", onActivate);
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") onActivate(e);
    });
  });
}
