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
  await page.pdf({
    path: OUT,
    format: "A4",
    printBackground: false,
    margin: { top: "18mm", right: "18mm", bottom: "18mm", left: "18mm" },
  });
  const broken = await page.evaluate(() =>
    [...document.images].filter((i) => !i.complete || i.naturalWidth === 0)
      .map((i) => i.getAttribute("src")));
  await browser.close();
  console.log("wrote " + OUT + (broken.length ? "   BROKEN IMAGES: " + broken.join(", ") : "")
    + (problems.length ? "   JS: " + problems.join(" | ") : ""));
})();
