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

/* ----- Theme - default is dark, toggle persists in localStorage --------- */
(function theme() {
  const KEY = "cb-theme";
  const saved = localStorage.getItem(KEY);
  // Default to dark when no preference saved; only "paper" opts out.
  if (saved !== "paper") document.documentElement.setAttribute("data-theme", "dark");
  window.toggleTheme = function () {
    const cur = document.documentElement.getAttribute("data-theme");
    if (cur === "dark") {
      document.documentElement.removeAttribute("data-theme");
      localStorage.setItem(KEY, "paper");
    } else {
      document.documentElement.setAttribute("data-theme", "dark");
      localStorage.setItem(KEY, "dark");
    }
    const btn = document.querySelector(".themetoggle");
    if (btn) btn.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "☼" : "☾";
  };
})();

document.addEventListener("DOMContentLoaded", function () {
  // Theme toggle init label
  const tt = document.querySelector(".themetoggle");
  if (tt) {
    tt.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "☼" : "☾";
    tt.addEventListener("click", window.toggleTheme);
  }

  // Mobile menu
  const burger = document.querySelector(".nav-burger");
  const navInner = document.querySelector(".nav-strip-inner");
  if (burger && navInner) {
    burger.addEventListener("click", () => navInner.classList.toggle("open"));
  }

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
});

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
