/* The three CreArtBox biographies as A4 PDFs, taken from about.html so
 * the download and the page can never say different things.
 *
 *   node tools/render_press_bios.js
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("/opt/node22/lib/node_modules/playwright");

const ABOUT = fs.readFileSync("about.html", "utf8");
const LABEL = { long: "Long biography", medium: "Medium biography", short: "Short biography" };

function paragraphs(version) {
  const start = ABOUT.indexOf(`data-bio-version="${version}"`);
  const end = ABOUT.indexOf('<button type="button" class="bio-copy"', start);
  const block = ABOUT.slice(start, end);
  return [...block.matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g)].map((m) => m[1].trim());
}

function sheet(version) {
  const paras = paragraphs(version);
  const chars = paras
    .map((p) => p.replace(/<[^>]+>/g, ""))
    .join(" ")
    .replace(/&#x27;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim().length;
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,300..700&family=Archivo:wght@400;600&display=swap" rel="stylesheet">
<style>
  @page { size: A4; margin: 22mm 20mm; }
  body { margin: 0; font-family: "Literata", Georgia, serif; color: #111; }
  .name { font-size: 26pt; font-weight: 600; letter-spacing: -0.01em; }
  .sub { font-family: "Archivo", Arial, sans-serif; font-size: 9pt; color: #555;
         margin-top: 4pt; }
  .kind { font-family: "Archivo", Arial, sans-serif; font-size: 8pt; letter-spacing: .16em;
          text-transform: uppercase; color: #777; margin: 22pt 0 6pt;
          border-top: 1px solid #111; padding-top: 8pt; }
  h1 { font-size: 15pt; font-weight: 600; margin: 0 0 14pt; }
  p { font-size: 10.5pt; line-height: 1.6; margin: 0 0 10pt; }
  em { font-style: italic; }
  .foot { font-family: "Archivo", Arial, sans-serif; font-size: 8.5pt; color: #666;
          margin-top: 26pt; border-top: 1px solid #ccc; padding-top: 8pt; }
</style></head><body>
  <div class="name">CreArtBox</div>
  <div class="sub">Chamber music ensemble - New York City - since 2013</div>
  <div class="kind">Biography &#183; ${chars} characters</div>
  <h1>${LABEL[version]}</h1>
  ${paras.map((p) => `<p>${p}</p>`).join("\n  ")}
  <p class="foot">creartbox.nyc &#183; info@creartbox.nyc</p>
</body></html>`;
}


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

(async () => {
  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
  });
  const page = await browser.newPage();
  await serveFonts(page);
  for (const version of ["long", "web", "medium", "short"]) {
    const tmp = path.join("/tmp", `cb-bio-${version}.html`);
    fs.writeFileSync(tmp, sheet(version));
    await page.goto("file://" + tmp, { waitUntil: "load" });
    await page.emulateMedia({ media: "print" });
    const out = `assets/press/creartbox-bio-${version}.pdf`;
    await page.pdf({ path: out, format: "A4", printBackground: true });
    console.log("wrote", out);
  }
  await browser.close();
})();
