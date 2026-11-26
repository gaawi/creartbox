// Where Chromium lives today.
//
// Every render_*.js used to carry the literal path
// /opt/pw-browsers/chromium-1194/chrome-linux/chrome. That number is the
// build of Chromium the machine happened to have, and it changes under us:
// when it did, all five renderers stopped with "executable doesn't exist"
// and the posters quietly went unbuilt. So look it up instead.
//
// Order: whatever CHROMIUM_PATH says, then the stable symlink the image
// keeps, then the newest chromium-<build> directory, and finally nothing,
// which hands the question back to Playwright and its own copy.

const fs = require("fs");
const path = require("path");

const ROOT = "/opt/pw-browsers";

function candidates() {
  const out = [];
  if (process.env.CHROMIUM_PATH) out.push(process.env.CHROMIUM_PATH);
  out.push(path.join(ROOT, "chromium"));
  let dirs = [];
  try {
    dirs = fs.readdirSync(ROOT).filter((d) => /^chromium-\d+$/.test(d));
  } catch (e) {
    dirs = [];
  }
  // newest build first
  dirs.sort((a, b) => Number(b.split("-")[1]) - Number(a.split("-")[1]));
  for (const d of dirs) out.push(path.join(ROOT, d, "chrome-linux", "chrome"));
  return out;
}

// An executable file, or undefined so Playwright picks its own.
module.exports = function chromiumPath() {
  for (const p of candidates()) {
    try {
      const st = fs.statSync(p);
      if (st.isFile()) return p;
    } catch (e) {
      // not there, try the next one
    }
  }
  return undefined;
};
