// Render the season press release to a PDF for sending to press.
//
//   node tools/render_press.js
//
// The page's own @media print rules do the work, so the PDF and the web
// page cannot say different things.

const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const path = require("path");

const PAGE = "press/season-2026-27.html";
const OUT = "downloads/creartbox-season-2026-27.pdf";

(async () => {
  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage({ viewport: { width: 900, height: 1200 } });
  const problems = [];
  page.on("pageerror", (e) => problems.push(String(e).slice(0, 140)));
  await page.goto("file://" + path.resolve(PAGE), { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  await page.emulateMedia({ media: "print" });
  // A running head and a page count, which is what a desk needs once a
  // release runs past one sheet. Chromium draws these itself, so they
  // need their own inline styles and an absolute font size.
  const rule = "border-bottom:0.5pt solid #bbb;padding-bottom:4px;";
  await page.pdf({
    path: OUT,
    format: "A4",
    printBackground: false,
    displayHeaderFooter: true,
    headerTemplate:
      '<div style="width:100%;margin:0 18mm;font-family:Helvetica,Arial,sans-serif;' +
      'font-size:7pt;color:#777;letter-spacing:.08em;text-transform:uppercase;' + rule +
      'display:flex;justify-content:space-between;">' +
      "<span>CreArtBox &#183; 2026 / 27 season</span>" +
      "<span>Press release</span></div>",
    footerTemplate:
      '<div style="width:100%;margin:0 18mm;font-family:Helvetica,Arial,sans-serif;' +
      'font-size:7pt;color:#777;display:flex;justify-content:space-between;">' +
      "<span>marketing@creartbox.nyc &#183; creartbox.nyc</span>" +
      '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>' +
      "</div>",
    margin: { top: "22mm", right: "18mm", bottom: "18mm", left: "18mm" },
  });
  // An image the print stylesheet hides never loads, and is not broken:
  // the press photographs are on the page for the web, not for the PDF.
  const broken = await page.evaluate(() =>
    [...document.images]
      .filter((i) => i.getClientRects().length > 0)
      .filter((i) => !i.complete || i.naturalWidth === 0)
      .map((i) => i.getAttribute("src")));
  await browser.close();
  console.log("wrote " + OUT + (broken.length ? "   BROKEN IMAGES: " + broken.join(", ") : "")
    + (problems.length ? "   JS: " + problems.join(" | ") : ""));
})();
