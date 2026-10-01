// Render the presenters page to the programme dossier PDF.
//
//   node tools/render_dossier.js
//
// The page's own @media print rules decide what the dossier keeps, so
// the PDF and the page cannot say different things.

const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const fs = require("fs");
const path = require("path");

// The brand faces come from Google Fonts. Where there is no route to
// them, CB_FONT_CACHE points at a directory holding fonts.css and the
// woff2 files it names, and they are served from there instead.
const FONT_CACHE = process.env.CB_FONT_CACHE || "";

async function serveFonts(page) {
  if (FONT_CACHE && fs.existsSync(path.join(FONT_CACHE, "fonts.css"))) {
    await page.route("https://fonts.googleapis.com/**", (route) =>
      route.fulfill({ contentType: "text/css",
                      body: fs.readFileSync(path.join(FONT_CACHE, "fonts.css")) }));
    await page.route("https://fonts.gstatic.com/**", (route) => {
      const file = path.join(FONT_CACHE, path.basename(new URL(route.request().url()).pathname));
      if (!fs.existsSync(file)) return route.abort();
      return route.fulfill({ contentType: "font/woff2", body: fs.readFileSync(file) });
    });
    return;
  }
  // No cache: a hanging font request must not hold up the render.
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
}

const PAGE = "presenters.html";
const OUT = "downloads/creartbox-program-dossier.pdf";

(async () => {
  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });

  await serveFonts(page);
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
  const header = (title) =>
    '<div style="width:100%;margin:0 16mm;font-family:Helvetica,Arial,sans-serif;' +
    'font-size:7pt;color:#777;letter-spacing:.08em;text-transform:uppercase;' + rule +
    'display:flex;justify-content:space-between;">' +
    "<span>CreArtBox &#183; " + title + "</span><span>2026 / 27</span></div>";
  const footer =
    '<div style="width:100%;margin:0 16mm;font-family:Helvetica,Arial,sans-serif;' +
    'font-size:7pt;color:#777;display:flex;justify-content:space-between;">' +
    "<span>info@creartbox.nyc &#183; creartbox.nyc/presenters.html</span>" +
    '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>' +
    "</div>";
  const paper = {
    format: "A4",
    printBackground: true,
    displayHeaderFooter: true,
    footerTemplate: footer,
    margin: { top: "20mm", right: "16mm", bottom: "16mm", left: "16mm" },
  };

  await page.pdf({
    ...paper,
    path: OUT,
    headerTemplate: header("Concert programme dossier"),
  });

  // One proposal per programme: the same page with the other programme
  // hidden, so a presenter can be sent the one that interests them.
  const programs = await page.evaluate(() =>
    [...document.querySelectorAll(".offer")].map((o) => ({
      slug: o.dataset.program,
      title: o.querySelector(".offer-title").textContent.trim(),
    })));
  for (const { slug, title } of programs) {
    await page.evaluate((keep) => {
      document.querySelectorAll(".offer").forEach((o) => {
        o.style.display = o.dataset.program === keep ? "" : "none";
      });
      document.querySelector(".offer-grid").style.gridTemplateColumns = "1fr";
    }, slug);
    const out = "downloads/creartbox-" + slug + ".pdf";
    await page.pdf({ ...paper, path: out, headerTemplate: header(title) });
    console.log("wrote " + out);
  }
  await page.evaluate(() => {
    document.querySelectorAll(".offer").forEach((o) => { o.style.display = ""; });
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
