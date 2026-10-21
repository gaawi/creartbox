// Render each Call for Scores to a PDF a composer can keep.
//
//   node tools/render_calls.js
//
// The page's own @media print rules decide what the document keeps, so
// the PDF and the guidelines on the site cannot say different things.

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
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
}

const CALLS = [
  { page: "calls/scores-international.html", out: "downloads/creartbox-ca1-2026.pdf",
    head: "CA1/2026 &#183; Call for Scores &#183; International composers" },
  { page: "calls/scores-american.html", out: "downloads/creartbox-ca2-2026.pdf",
    head: "CA2/2026 &#183; Call for Scores &#183; American composers" },
];

(async () => {
  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });
  await serveFonts(page);
  const problems = [];
  page.on("pageerror", (e) => problems.push(String(e).slice(0, 140)));

  const rule = "border-bottom:0.5pt solid #bbb;padding-bottom:4px;";
  for (const call of CALLS) {
    await page.goto("file://" + path.resolve(call.page), { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    // the production photograph is lazy and sits below the fold
    await page.evaluate(() => {
      document.querySelectorAll("img[loading=lazy]").forEach((i) => { i.loading = "eager"; });
      return Promise.race([
        Promise.all([...document.images].filter((i) => !i.complete)
          .map((i) => new Promise((r) => { i.onload = i.onerror = r; }))),
        new Promise((r) => setTimeout(r, 6000)),
      ]);
    });
    await page.emulateMedia({ media: "print" });
    await page.pdf({
      path: call.out,
      format: "A4",
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate:
        '<div style="width:100%;margin:0 16mm;font-family:Helvetica,Arial,sans-serif;' +
        'font-size:7pt;color:#777;letter-spacing:.08em;text-transform:uppercase;' + rule +
        'display:flex;justify-content:space-between;">' +
        "<span>CreArtBox &#183; " + call.head + "</span><span>2027 / 28</span></div>",
      footerTemplate:
        '<div style="width:100%;margin:0 16mm;font-family:Helvetica,Arial,sans-serif;' +
        'font-size:7pt;color:#777;display:flex;justify-content:space-between;">' +
        "<span>Deadline 15 December 2026 &#183; tally.so/r/o9boab &#183; info@creartbox.nyc</span>" +
        '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>' +
        "</div>",
      margin: { top: "20mm", right: "16mm", bottom: "16mm", left: "16mm" },
    });
    console.log("wrote " + call.out);
  }

  await browser.close();
  if (problems.length) console.log("   JS: " + problems.join(" | "));
})();
