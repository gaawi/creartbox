#!/usr/bin/env python3
"""Build the news section from the posts in news/_posts.

    python3 tools/build_news.py            # render and write
    python3 tools/build_news.py --check    # fail if out of date

A post is one Markdown file, news/_posts/YYYY-MM-DD-slug.md, opening
with a short block of keys:

    ---
    title: What happened
    date: 2026-09-29
    dek: One sentence under the headline.
    tag: Season
    image: assets/img/ensemble.jpg
    alt: What the photograph shows
    caption: The line printed under it.
    link: Read about Currents | concerts/currents-2026.html
    ---

    The body, in Markdown: paragraphs, ## headings, - lists,
    > quotations, **bold**, *italic*, and [links](https://example.com).

Everything else is generated: the index at news.html, one page per post
under news/, and the RSS feed at feed.xml. The News item in the
navigation and in the footer is put there by tools/sync_nav.py.
"""

import datetime
import glob
import html
import os
import re
import sys

SITE = "https://creartbox.nyc"
POSTS_DIR = "news/_posts"
OUT_DIR = "news"
INDEX = "news.html"
FEED = "feed.xml"
CSS = "assets/styles.css?v=131"
JS = "assets/site.js?v=43"
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# ----------------------------------------------------------------- reading

def read_post(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n?(.*)", raw, re.S)
    if not m:
        raise SystemExit("  !! no key block in " + path)
    meta = {"link": []}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key == "link":
            meta["link"].append(value)
        else:
            meta[key] = value
    for required in ("title", "date", "dek"):
        if not meta.get(required):
            raise SystemExit("  !! %s is missing '%s'" % (path, required))
    meta["slug"] = os.path.basename(path)[11:-3]     # strip date and .md
    meta["body"] = m.group(2).strip()
    y, mo, d = (int(x) for x in meta["date"].split("-"))
    meta["dt"] = datetime.date(y, mo, d)
    return meta


def posts():
    found = [read_post(p) for p in sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")))]
    found.sort(key=lambda p: (p["dt"], p["slug"]), reverse=True)
    return found


def long_date(d):
    return "%s %d, %d" % (MONTHS[d.month - 1], d.day, d.year)


def short_date(d):
    return "%s %d" % (MONTHS[d.month - 1][:3], d.year)


# --------------------------------------------------------------- Markdown

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
IMAGE_RE = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)$')
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITAL_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def inline(text, prefix):
    out = html.escape(text.strip(), quote=True)

    def link(m):
        label, url = m.group(1), m.group(2)
        if url.startswith("http"):
            return '<a href="{}" target="_blank" rel="noopener">{}</a>'.format(url, label)
        if url.startswith(("#", "mailto:")):
            return '<a href="{}">{}</a>'.format(url, label)
        return '<a href="{}{}">{}</a>'.format(prefix, url, label)

    out = LINK_RE.sub(link, out)
    out = BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = ITAL_RE.sub(r"<em>\1</em>", out)
    return out


def markdown(body, prefix):
    """The small part of Markdown a news post actually needs."""
    blocks, lines = [], body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("## "):
            blocks.append('<h2 class="news-h2">%s</h2>' % inline(line[3:], prefix))
            i += 1
        elif IMAGE_RE.match(line.strip()):
            alt, src, cap = IMAGE_RE.match(line.strip()).groups()
            blocks.append(
                '<figure class="news-fig"><img src="{p}{src}" alt="{alt}" loading="lazy">{cap}'
                '</figure>'.format(
                    p=prefix, src=src, alt=html.escape(alt, quote=True),
                    cap=('<figcaption class="cap">%s</figcaption>' % inline(cap, prefix))
                    if cap else ""))
            i += 1
        elif line.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:].strip())
                i += 1
            blocks.append('<blockquote class="news-quote"><p>%s</p></blockquote>'
                          % inline(" ".join(quote), prefix))
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append("<li>%s</li>" % inline(lines[i][2:], prefix))
                i += 1
            blocks.append('<ul class="news-ul">%s</ul>' % "".join(items))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("## ", "- ", "> ", "![")):
                para.append(lines[i].strip())
                i += 1
            blocks.append("<p>%s</p>" % inline(" ".join(para), prefix))
    return "\n        ".join(blocks)


# ----------------------------------------------------------------- pieces

def head(title, description, canonical, prefix, image=""):
    social = ""
    if image:
        social = ('<meta property="og:image" content="{site}/{img}">\n'
                  .format(site=SITE, img=image))
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
{social}<link rel="alternate" type="application/rss+xml" title="CreArtBox news" href="{site}/feed.xml">
<link rel="icon" type="image/svg+xml" href="{p}brand/mark-wedge-box.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}{css}">
<script id="cb-theme-init">document.documentElement.setAttribute("data-theme","dark");</script>
</head>
<body>

<header class="masthead">
  <div class="masthead-inner">
    <div class="masthead-left"><button class="nav-burger" aria-label="Menu">Menu</button><span class="established">Established 2013, New York City</span></div>
    <a class="masthead-title" href="{p}index.html"><img class="logo-img" src="{p}brand/logo-creartbox-reversed.svg" alt="CreArtBox"></a>
    <div class="masthead-right"><a class="masthead-tickets" href="{p}concerts.html">Get tickets</a></div>
  </div>
  <nav class="nav-strip">
    <div class="nav-strip-inner">
      <div class="nav-item"><a href="{p}index.html">Home</a></div>
      <div class="nav-item"><a href="{p}about.html">About</a></div>
      <div class="nav-item"><a href="{p}concerts.html">Calendar</a></div>
      <div class="nav-item"><a href="{p}archive.html">Archive</a></div>
      <div class="nav-item"><a href="{p}projects.html">Projects</a></div>
      <div class="nav-item"><a href="{p}opportunities.html">Opportunities</a></div>
      <div class="nav-item"><a href="{p}media.html">Media</a></div>
      <div class="nav-item"><a href="{p}news.html" class="active">News</a></div>
      <div class="nav-item"><a href="{p}support.html">Donate</a></div>
    </div>
  </nav>
</header>

<main>
""".format(title=html.escape(title, quote=True),
           description=html.escape(description, quote=True),
           canonical=canonical, p=prefix, css=CSS, site=SITE, social=social)


def foot(prefix):
    return """
</main>

<footer class="colophon">
  <div class="wrap">
    <div class="colophon-grid">
      <div>
        <div class="colophon-mark"><img src="{p}brand/mark-wedge-amber.svg" alt="CreArtBox" width="52" height="24"></div>
        <p class="colophon-bio">A 501(c)(3) non-profit chamber music and multimedia ensemble. New York &#183; Asturias.</p>
        <p class="colophon-addr">info@creartbox.nyc &#183; 10&#8211;48 47th Road, Unit 1, Queens, NY 11101</p>
        <div class="colophon-social">
          <a href="https://www.instagram.com/creartboxnyc/" target="_blank" rel="noopener">Instagram</a>
          <a href="https://www.youtube.com/creartbox" target="_blank" rel="noopener">YouTube</a>
          <a href="https://www.facebook.com/creartbox" target="_blank" rel="noopener">Facebook</a>
          <a href="https://www.tiktok.com/@creartbox" target="_blank" rel="noopener">TikTok</a>
          <a href="https://x.com/creartbox" target="_blank" rel="noopener">X</a>
        </div>
      </div>
      <div><h4>Program</h4><ul><li><a href="{p}concerts.html">Calendar</a></li><li><a href="{p}archive.html">Archive of Performances</a></li><li><a href="{p}projects.html">Productions</a></li><li><a href="https://festivaladar.com" target="_blank" rel="noopener">Festival ADAR</a></li><li><a href="https://apps.apple.com/us/app/creartbox/id6746415261" target="_blank" rel="noopener">iOS app &#183; App Store</a></li></ul></div>
      <div><h4>The Organization</h4><ul><li><a href="{p}about.html">About</a></li><li><a href="{p}news.html">News</a></li><li><a href="{p}opportunities.html">Opportunities</a></li><li><a href="{p}brand.html">Brand &amp; press kit</a></li><li><a href="{p}media.html#magazine">CreArt Magazine</a></li></ul></div>
      <div><h4>Give</h4><ul><li><a href="{p}support.html">Donate</a></li></ul></div>
    </div>
    <div class="colophon-bot"><span>&#169; CreArtBox, Inc. 2013&#8211;2027 &#183; 501(c)(3) non-profit</span></div>
  </div>
</footer>

<script src="{p}{js}"></script>
</body>
</html>
""".format(p=prefix, js=JS)


def card(post, prefix, featured=False):
    img = ""
    if post.get("image"):
        img = ('<a class="news-card-media" href="{p}news/{slug}.html">'
               '<img src="{p}{src}" alt="{alt}" loading="lazy"></a>'.format(
                   p=prefix, slug=post["slug"], src=post["image"],
                   alt=html.escape(post.get("alt", ""), quote=True)))
    return ('      <article class="news-card{big}">\n'
            '        {img}\n'
            '        <div class="news-card-text">\n'
            '          <div class="news-meta"><span class="news-tag">{tag}</span>'
            '<time datetime="{iso}">{date}</time></div>\n'
            '          <h3 class="news-card-title"><a href="{p}news/{slug}.html">{title}</a></h3>\n'
            '          <p class="news-dek">{dek}</p>\n'
            '          <a class="news-more" href="{p}news/{slug}.html">Read on '
            '<span class="ar">&#8594;</span></a>\n'
            '        </div>\n'
            '      </article>'.format(
                big=" news-card-big" if featured else "", img=img, p=prefix,
                tag=html.escape(post.get("tag", "News"), quote=True),
                iso=post["date"], date=long_date(post["dt"]),
                slug=post["slug"], title=inline(post["title"], prefix),
                dek=inline(post["dek"], prefix)))


# ------------------------------------------------------------------ pages

def index_page(all_posts):
    lead = card(all_posts[0], "", featured=True) if all_posts else ""
    rest = "\n".join(card(p, "") for p in all_posts[1:])
    return (head("News · CreArtBox",
                 "Season announcements, notes from the road, and what the "
                 "ensemble is working on now.",
                 SITE + "/news.html", "")
            + """
<section style="padding:64px 0 24px">
  <div class="wrap">
    <span class="folio left">CreArtBox &#183; News</span>
    <span class="folio right">{count}</span>

    <div class="page-folio-head">
      <span class="label">News</span>
      <hr class="rule" style="width:100%">
      <span class="label ital">Updated as things happen</span>
    </div>
    <h1 class="h-mast" style="margin-top:32px;max-width:15ch;">
      <em>News</em> and notes.
    </h1>
    <p class="lede" style="margin-top:40px">
      Season announcements, what the ensemble is rehearsing, where it is playing, and
      the work that reaches us through the open call. Written here first, before it
      goes out by email.
    </p>
  </div>
</section>

<section class="section news-page" style="padding-top:20px">
  <div class="wrap">
    <div class="news-lead">
{lead}
    </div>

    <div class="news-list">
{rest}
    </div>

    <p class="news-feed"><a href="{site}/feed.xml">Follow by RSS</a> &#183; or write to
      <a href="mailto:info@creartbox.nyc">info@creartbox.nyc</a> to join the mailing list.</p>
  </div>
</section>
""".format(lead=lead, rest=rest, site=SITE,
           count="%d note%s" % (len(all_posts), "" if len(all_posts) == 1 else "s"))
            + foot(""))


def post_page(post, others):
    prefix = "../"
    hero = ""
    if post.get("image"):
        cap = post.get("caption", "")
        hero = ('    <figure class="news-hero"><img src="{p}{src}" alt="{alt}">{cap}</figure>\n'
                .format(p=prefix, src=post["image"],
                        alt=html.escape(post.get("alt", ""), quote=True),
                        cap=('<figcaption class="cap">%s</figcaption>' % inline(cap, prefix))
                        if cap else ""))

    links = ""
    if post["link"]:
        rows = []
        for entry in post["link"]:
            label, _, url = entry.partition("|")
            label, url = label.strip(), url.strip()
            ext = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
            href = url if url.startswith(("http", "mailto:")) else prefix + url
            rows.append('<a class="btn" href="{}"{}>{} <span class="ar">&#8594;</span></a>'
                        .format(href, ext, html.escape(label, quote=True)))
        links = ('      <div class="news-links">{}</div>\n'.format("".join(rows)))

    more = ""
    if others:
        more = ('\n<section class="section tinted news-more-wrap">\n  <div class="wrap">\n'
                '    <div class="section-title"><hr class="rule">'
                '<div class="head"><span class="label">More news</span><span class="bar"></span>'
                '<span class="label ital">Also <em>this season</em>.</span></div>'
                '<hr class="rule"></div>\n'
                '    <div class="news-list">\n{}\n    </div>\n'
                '    <p class="news-feed"><a href="{}news.html">All news '
                '<span class="ar">&#8594;</span></a></p>\n  </div>\n</section>\n'.format(
                    "\n".join(card(p, prefix) for p in others), prefix))

    return (head(post["title"] + " · CreArtBox", post["dek"],
                 "%s/news/%s.html" % (SITE, post["slug"]), prefix,
                 post.get("image", ""))
            + """
<section class="section news-article">
  <div class="wrap">
    <a href="{p}news.html" class="back-to-archive">&#8592; News</a>

    <header class="news-head">
      <div class="news-meta"><span class="news-tag">{tag}</span>
        <time datetime="{iso}">{date}</time></div>
      <h1 class="news-title">{title}</h1>
      <p class="news-dek">{dek}</p>
    </header>

{hero}
    <div class="news-body">
        {body}
    </div>

{links}  </div>
</section>
{more}""".format(p=prefix, tag=html.escape(post.get("tag", "News"), quote=True),
                 iso=post["date"], date=long_date(post["dt"]),
                 title=inline(post["title"], prefix), dek=inline(post["dek"], prefix),
                 hero=hero, body=markdown(post["body"], prefix), links=links, more=more)
            + foot(prefix))


def feed(all_posts):
    items = []
    for post in all_posts:
        url = "%s/news/%s.html" % (SITE, post["slug"])
        stamp = datetime.datetime(post["dt"].year, post["dt"].month, post["dt"].day, 12)
        items.append(
            "    <item>\n"
            "      <title>{title}</title>\n"
            "      <link>{url}</link>\n"
            "      <guid isPermaLink=\"true\">{url}</guid>\n"
            "      <pubDate>{date}</pubDate>\n"
            "      <description>{dek}</description>\n"
            "    </item>".format(
                title=html.escape(post["title"]), url=url,
                date=stamp.strftime("%a, %d %b %Y %H:%M:%S +0000"),
                dek=html.escape(post["dek"])))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0">\n'
            '  <channel>\n'
            '    <title>CreArtBox · News</title>\n'
            '    <link>{site}/news.html</link>\n'
            '    <description>Season announcements, notes from the road, and what the '
            'ensemble is working on now.</description>\n'
            '    <language>en-us</language>\n'
            '{items}\n'
            '  </channel>\n'
            '</rss>\n'.format(site=SITE, items="\n".join(items)))


# ------------------------------------------------------------- the home page

HOME_RE = re.compile(r"(<!-- NEWS · generated by tools/build_news\.py -->\n).*?(<!-- /NEWS -->)", re.S)


def home_block(all_posts):
    rows = []
    for post in all_posts[:3]:
        rows.append(
            '      <a class="hnews-item" href="news/{slug}.html">\n'
            '        <div class="news-meta"><span class="news-tag">{tag}</span>'
            '<time datetime="{iso}">{date}</time></div>\n'
            '        <h3>{title}</h3>\n'
            '        <p>{dek}</p>\n'
            '      </a>'.format(
                slug=post["slug"], tag=html.escape(post.get("tag", "News"), quote=True),
                iso=post["date"], date=long_date(post["dt"]),
                title=inline(post["title"], ""), dek=inline(post["dek"], "")))
    return ('<section class="section home-news">\n'
            '  <div class="wrap">\n'
            '    <div class="section-title"><hr class="rule">'
            '<div class="head"><span class="label">News</span><span class="bar"></span>'
            '<span class="label ital">Lately, from <em>the ensemble</em>.</span></div>'
            '<hr class="rule"></div>\n'
            '    <div class="hnews-grid">\n{rows}\n    </div>\n'
            '    <div class="hnews-foot"><a class="btn" href="news.html">All news '
            '<span class="ar">&#8594;</span></a></div>\n'
            '  </div>\n'
            '</section>\n'.format(rows="\n".join(rows)))


def sync_home(all_posts, check):
    src = open("index.html", encoding="utf-8").read()
    if not HOME_RE.search(src):
        print("  !! no news block on the home page; add the markers first")
        return []
    out = HOME_RE.sub(lambda m: m.group(1) + home_block(all_posts) + m.group(2), src, count=1)
    if out == src:
        return []
    if not check:
        open("index.html", "w", encoding="utf-8").write(out)
    return ["index.html"]


# -------------------------------------------------------------------- main

def write(path, wanted, check, stale):
    current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    if current == wanted:
        return
    stale.append(path)
    if not check:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(path, "w", encoding="utf-8").write(wanted)


def main():
    check = "--check" in sys.argv
    stale = []
    all_posts = posts()
    if not all_posts:
        print("no posts in " + POSTS_DIR)
        return 1

    for post in all_posts:
        others = [p for p in all_posts if p["slug"] != post["slug"]][:3]
        write(os.path.join(OUT_DIR, post["slug"] + ".html"),
              post_page(post, others), check, stale)

    write(INDEX, index_page(all_posts), check, stale)
    write(FEED, feed(all_posts), check, stale)
    stale += sync_home(all_posts, check)

    # a page left over from a post that was deleted or renamed
    keep = {p["slug"] + ".html" for p in all_posts}
    for name in sorted(os.listdir(OUT_DIR)):
        if name.endswith(".html") and name not in keep:
            stale.append(os.path.join(OUT_DIR, name))
            if not check:
                os.remove(os.path.join(OUT_DIR, name))

    if check:
        if stale:
            print("news out of date ({} file(s)):".format(len(stale)))
            for p in stale[:6]:
                print("  -", p)
            print("\nRun: python3 tools/build_news.py")
            return 1
        print("news up to date: %d post(s)" % len(all_posts))
    else:
        print("news: %d post(s), %d file(s) written" % (len(all_posts), len(stale)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
