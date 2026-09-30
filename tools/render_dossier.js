// Render the presenters page to the programme dossier PDF.
//
//   node tools/render_dossier.js
//
// The page's own @media print rules decide what the dossier keeps, so
// the PDF and the page cannot say different things.

const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const fs = require("fs");
const path = require("path");

// The brand faces come from Google Fonts. A sandbox without a route to
// them would print the PDF in a fallback face, so the renderer serves a
// local cache when there is one: FONT_CACHE holds fonts.css and the
// woff2 files it names. Refill it with:
//   curl "https://fonts.googleapis.com/css2?..." -o fonts.css && ...
const FONT_CACHE = process.env.CB_FONT_CACHE || "";

const PAGE = "presenters.html";
const OUT = "downloads/creartbox-program-dossier.pdf";

(async () => {
  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });

  if (FONT_CACHE && fs.existsSync(path.join(FONT_CACHE, "fonts.css"))) {
    await page.route("https://fonts.googleapis.com/**", (route) =>
      route.fulfill({ contentType: "text/css",
                      body: fs.readFileSync(path.join(FONT_CACHE, "fonts.css")) }));
    await page.route("https://fonts.gstatic.com/**", (route) => {
      const file = path.join(FONT_CACHE, path.basename(new URL(route.request().url()).pathname));
      if (!fs.existsSync(file)) return route.abort();
      return route.fulfill({ contentType: "font/woff2", body: fs.readFileSync(file) });
    });
  } else {
    // No cache: do not let a hanging font request hold up the render.
    await page.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
  }
  const problems = [];
  page.on("pageerror", (e) => problems.push(String(e).slice(0, 140)));
  await page.goto("file://" + path.resolve(PAGE), { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  // Portraits and the ensemble photograph are lazy: below the fold they
  // never start loading, so the PDF would print empty boxes. Ask for
  // them eagerly, then wait for them, but never for ever.
  await page.evaluate(() => {
    document.querySelectorAll("img[loading=lazy]").forEach((i) => { i.loading = "eager"; });
    return Promise.race([
      Promise.all([...document.images]
        .filter((i) => !i.complete)
        .map((i) => new Promise((r) => { i.onload = i.onerror = r; }))),
      new Promise((r) => setTimeout(r, 6000)),
    ]);
  });
  await page.waitForTimeout(300);
  await page.emulateMedia({ media: "print" });

  const rule = "border-bottom:0.5pt solid #bbb;padding-bottom:4px;";
  await page.pdf({
    path: OUT,
    format: "A4",
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate:
      '<div style="width:100%;margin:0 16mm;font-family:Helvetica,Arial,sans-serif;' +
      'font-size:7pt;color:#777;letter-spacing:.08em;text-transform:uppercase;' + rule +
      'display:flex;justify-content:space-between;">' +
      "<span>CreArtBox &#183; Concert programme dossier</span>" +
      "<span>2026 / 27</span></div>",
    footerTemplate:
      '<div style="width:100%;margin:0 16mm;font-family:Helvetica,Arial,sans-serif;' +
      'font-size:7pt;color:#777;display:flex;justify-content:space-between;">' +
      "<span>info@creartbox.nyc &#183; creartbox.nyc/presenters.html</span>" +
      '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>' +
      "</div>",
    margin: { top: "20mm", right: "16mm", bottom: "16mm", left: "16mm" },
  });

  const broken = await page.evaluate(() =>
    [...document.images]
      .filter((i) => i.getClientRects().length > 0)
      .filter((i) => !i.complete || i.naturalWidth === 0)
      .map((i) => i.getAttribute("src")));
  await browser.close();
  console.log("wrote " + OUT
    + (broken.length ? "   BROKEN IMAGES: " + broken.join(", ") : "")
    + (problems.length ? "   JS: " + problems.join(" | ") : ""));
})();
