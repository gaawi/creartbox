// Render every poster in posters/ to print PDF and to PNG.
//
//   node tools/render_posters.js
//
// The HTML is written by tools/build_posters.py from the concert pages;
// this step only needs a browser. Web fonts are waited on explicitly, so
// a poster is never captured in the fallback face.

const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const fs = require("fs");
const path = require("path");

const DIR = "posters";
// A3 portrait in CSS pixels: 297x420mm at the browser's 96dpi. Sizing the
// viewport in 150dpi pixels instead leaves the poster laid out at 96dpi in
// the corner of a much larger canvas - the scale factor is what raises the
// resolution, not the viewport.
const A3_CSS = { width: 1123, height: 1587 };
const DPI = 150;

(async () => {
  const pages = fs.readdirSync(DIR).filter((f) => f.endsWith(".html"));
  if (!pages.length) {
    console.log("no posters to render - run tools/build_posters.py first");
    return;
  }

  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    args: ["--no-sandbox"],
  });

  for (const file of pages.sort()) {
    const slug = path.basename(file, ".html");
    const page = await browser.newPage({
      viewport: A3_CSS,
      deviceScaleFactor: DPI / 96,
    });
    const problems = [];
    page.on("pageerror", (e) => problems.push(String(e).slice(0, 140)));

    await page.goto("file://" + path.resolve(DIR, file), { waitUntil: "load" });
    // the poster is set in Literata and Archivo; do not shoot it early
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(400);

    const broken = await page.evaluate(() =>
      [...document.images].filter((i) => !i.complete || i.naturalWidth === 0)
        .map((i) => i.getAttribute("src")));
    const usedFallback = await page.evaluate(() =>
      !document.fonts.check('300 26mm "Literata"'));

    await page.pdf({
      path: path.join(DIR, slug + ".pdf"),
      format: "A3",
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
    });
    await page.screenshot({
      path: path.join(DIR, slug + ".png"),
      fullPage: false,
    });
    await page.close();

    const flags = [];
    if (broken.length) flags.push("BROKEN IMAGES: " + broken.join(", "));
    if (usedFallback) flags.push("LITERATA DID NOT LOAD");
    if (problems.length) flags.push("JS: " + problems.join(" | "));
    console.log(
      "  " + slug.padEnd(30) + " pdf + png" + (flags.length ? "   " + flags.join("   ") : ""));
  }

  await browser.close();
  console.log("\n" + pages.length + " poster(s) rendered into " + DIR + "/");
})();
