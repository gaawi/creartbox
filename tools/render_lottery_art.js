// Render the ticket-lottery graphics to JPEG.
//
//   python3 tools/build_lottery_art.py   # writes promo/lottery-*.html
//   node tools/render_lottery_art.js     # this
//
// Each one is captured at twice its size and brought back down, so the
// type is clean at the size it is actually posted at. Web fonts are
// waited on explicitly: a graphic captured in the fallback face is worse
// than no graphic, and it fails silently.

const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const SRC = "promo";
const DST = path.join("assets", "img", "promo");

// slug -> the size it is posted at
const SIZES = {
  square: [1080, 1080],
  portrait: [1080, 1350],
  story: [1080, 1920],
  landscape: [1200, 628],
};

(async () => {
  const files = fs.readdirSync(SRC).filter((f) => /^lottery-.*\.html$/.test(f));
  if (!files.length) {
    console.log("nothing to render - run tools/build_lottery_art.py first");
    process.exit(1);
  }
  fs.mkdirSync(DST, { recursive: true });

  const browser = await chromium.launch({ args: ["--no-sandbox"] });
  let bad = 0;

  for (const file of files.sort()) {
    const slug = path.basename(file, ".html").replace(/^lottery-/, "");
    const [w, h] = SIZES[slug] || [1080, 1080];
    const page = await browser.newPage({
      viewport: { width: w, height: h },
      deviceScaleFactor: 2,
    });
    const problems = [];
    page.on("pageerror", (e) => problems.push(String(e).slice(0, 140)));
    page.on("requestfailed", (r) =>
      problems.push("failed: " + r.url().slice(0, 90)));

    await page.goto("file://" + path.resolve(SRC, file), {
      waitUntil: "networkidle",
    });
    await page.evaluate(() => document.fonts.ready);
    // the photograph comes off the CDN; do not capture a grey rectangle
    const shotOk = await page.evaluate(() => {
      const i = document.querySelector("img.shot");
      return !!i && i.complete && i.naturalWidth > 0;
    });
    const faces = await page.evaluate(() =>
      [...document.fonts].filter((f) => f.status === "loaded").length);
    await page.waitForTimeout(250);

    const out = path.join(DST, "winterlight-lottery-" + slug + ".jpg");
    await page.screenshot({ path: out, type: "jpeg", quality: 90 });
    await page.close();

    // captured at 2x; bring it down to the size it is posted at, which
    // is what keeps a story under a megabyte without softening the type
    const { execFileSync } = require("child_process");
    execFileSync("python3", ["-c",
      "import sys;from PIL import Image;" +
      "p=sys.argv[1];w=int(sys.argv[2]);h=int(sys.argv[3]);" +
      "im=Image.open(p).convert('RGB').resize((w,h), Image.LANCZOS);" +
      "im.save(p, 'JPEG', quality=88, optimize=True, progressive=True)",
      out, String(w), String(h)]);

    const kb = (fs.statSync(out).size / 1024).toFixed(0);
    const flag = shotOk && faces > 0 && !problems.length ? "ok " : "!! ";
    if (flag === "!! ") bad++;
    console.log(
      `${flag}${out.padEnd(48)} ${w}x${h} @2  ${kb}KB  photo=${shotOk} fonts=${faces}` +
        (problems.length ? "\n     " + problems.join("\n     ") : "")
    );
  }

  await browser.close();
  process.exit(bad ? 1 : 0);
})();
