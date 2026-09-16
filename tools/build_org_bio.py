#!/usr/bin/env python3
"""The CreArtBox biography, at three lengths, from one source.

    python3 tools/build_org_bio.py            # write the page and the .txt files
    python3 tools/build_org_bio.py --check    # fail if out of date

The same text appears on about.html and in the press downloads, so it is
written once here and pushed to all of them. Run
`node tools/render_press_bios.js` afterwards to rebuild the PDFs.

The lengths match the artist pages: short at most 500 characters, medium
at most 1500, long unbounded. The script refuses to write a version that
is over its limit rather than trimming one silently, because these are
three separate texts a press desk chooses between, not cuts of each
other.

Every figure here is checkable against the rest of the site: the season
count, the productions, the composers and what they have won.
"""

import html
import os
import re
import sys

LIMITS = {"short": 500, "medium": 1500, "long": None}

PRESS = ('Recognized by <em>The New Yorker</em> as one of its "art and music top picks," '
         'praised by <em>Time Out</em> as "an ensemble devoted to multidisciplinary events," '
         'and described by <em>BroadwayWorld</em> as "wholly authentic, visually and aurally '
         'compelling," CreArtBox is celebrated for its ability to enhance the listening '
         'experience of live music through theatrical design while preserving the integrity '
         'of each composition.')

BIOS = {
    "short": [
        'CreArtBox is a New York chamber music and multimedia ensemble founded in 2013 by '
        'flutist <em>Guillermo Laporta</em> and pianist <em>Josefina Urraca</em>, now in its '
        '13th season. Recognized by <em>The New Yorker</em> as one of its "art and music top '
        'picks" and praised by <em>Time Out</em> as "an ensemble devoted to multidisciplinary '
        'events," it merges classical and contemporary music with original stage design and '
        'visual art.',
    ],
    "medium": [
        'CreArtBox is a New York chamber music and multimedia ensemble founded in 2013 by '
        'flutist <em>Guillermo Laporta</em> and pianist <em>Josefina Urraca</em>, with core '
        'members Emilie-Anne Gendron, Matthew Cohen, and Julia Yang. Now in its 13th season, '
        'it gives its New York Series at The DiMenna Center for Classical Music and tours '
        'nationally and internationally.',
        'Recognized by <em>The New Yorker</em> as one of its "art and music top picks," '
        'praised by <em>Time Out</em> as "an ensemble devoted to multidisciplinary events," '
        'and described by <em>BroadwayWorld</em> as "wholly authentic, visually and aurally '
        'compelling," CreArtBox merges classical and contemporary music with original stage '
        'design and visual art.',
        'The ensemble has run an open Call for Scores since its first season: eleven works in '
        'the 2026/27 season reached the programme through it, and one April evening is given '
        'over to it entirely. Its work is supported by the New York State Council on the Arts, '
        'the NYC Department of Cultural Affairs, the Amphion Foundation, the Alice M. Ditson '
        'Fund, and the Aaron Copland Fund for Music. Each August it co-produces Festival ADAR '
        'in rural Asturias, Spain.',
    ],
    "long": [
        'CreArtBox is a chamber music and multimedia ensemble based in New York City, founded '
        'in 2013 by flutist <em>Guillermo Laporta</em> and pianist <em>Josefina Urraca</em> and '
        'now in its 13th season. It gives its New York Series at The DiMenna Center for '
        'Classical Music, tours nationally with recurring engagements on the West Coast, and '
        'performs internationally in countries such as Japan, Spain, and the United Kingdom.',
        PRESS,
        'The 2026/27 season runs from October to August: four productions at The DiMenna '
        'Center, eleven works drawn from the ensemble&#x27;s open Call for Scores, one world '
        'premiere, touring dates in Illinois, Kentucky and the Hudson Valley, a residency at '
        'the Kuopio Conservatory in Finland, and the seventh Festival ADAR in Asturias.',
        'CreArtBox has run an open Call for Scores since its first season, alongside a composer '
        'residency program, fostering the creation of new works and mentoring emerging voices. '
        'Over the past decade it has presented works by Pulitzer Prize winners Caroline Shaw '
        'and David Lang and by Timo Andres, Anna Clyne, Nico Muhly, Joshua Penman, Andrea '
        'Casarrubios, Hannah Selin, Dai Wei, Brian Wysocki, Annamaria Kowalsky and Cullyn '
        'Murphy, among many others.',
        'Composers reaching the current season through the call include Eric Moe, a Guggenheim '
        'fellow honoured by the American Academy of Arts and Letters; Zygmund de Somogyi, a '
        'Royal Philharmonic Society composer for 2025 and Festival ADAR&#x27;s composer in '
        'residence; Eli Tausen á Lava, nominated for the 2026 Nordic Council Music Prize; and '
        'Paul Novak and Sam Wu, both winners of the ASCAP Foundation&#x27;s Morton Gould Young '
        'Composer Award.',
        'Each core member brings a distinctive artistic trajectory: Laporta has combined a '
        'career as a flutist with theater directing and lighting design; Urraca is an acclaimed '
        'solo and chamber pianist with deep ties to Spanish repertoire; Gendron is a longtime '
        'member of the Momenta Quartet and one of the concertmasters of the Orpheus Chamber '
        'Orchestra; Cohen is a special prize winner at the Primrose International Viola '
        'Competition; and Yang is a founding member of the Naumburg-winning Merz Trio.',
        'The project was originally conceived in 2006 in Europe as Cre.Art Project by Laporta '
        'and clarinetist/performance creator Tagore González, and re-established in New York '
        'City in 2013. Since then CreArtBox has produced a series of theatrical and '
        'interdisciplinary works, including <em>Architecture of a Common Man</em> (2023), the '
        'opera-ballet <em>Two Roads</em> (2020), <em>Visuality</em> (2012/14), the opera '
        '<em>Noctum</em> (2011), the musical <em>London: The Show</em> (2009), and <em>Cre.Art '
        'Project I</em> (2006).',
        'The ensemble has been awarded the Queens Council on the Arts New Work Grant and the '
        'New York Foundation for the Arts Fellowship, and is supported by the New York State '
        'Council on the Arts, the NYC Department of Cultural Affairs, the Amphion Foundation, '
        'the Alice M. Ditson Fund, and the Aaron Copland Fund for Music. In addition to its '
        'American-based activities, CreArtBox co-produces Festival ADAR, an international arts '
        'festival held since 2021 in Asturias, Spain, dedicated to revitalizing rural '
        'communities through music, contemporary creation, artist residencies, and '
        'site-specific projects.',
    ],
}

ABOUT = "about.html"
TXT = "assets/press/creartbox-bio-{}.txt"


def plain(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", fragment))).strip()


def length(version):
    return len(" ".join(plain(p) for p in BIOS[version]))


def block(version, src):
    """Rewrite one version in place, keeping the wrapper the page uses."""
    start = src.find('data-bio-version="%s"' % version)
    if start < 0:
        sys.exit("no %s biography block in %s" % (version, ABOUT))
    open_div = src.index(">", start) + 1
    end = src.index('<button type="button" class="bio-copy"', start)
    inner = src[open_div:end]
    wrapper = re.search(r'(\s*<div[^>]*>)(.*)(</div>\s*)', inner, re.S)
    body = "\n".join("            <p{}>{}</p>".format(
        ' class="dropcap"' if i == 0 else "", p) for i, p in enumerate(BIOS[version]))
    return src[:open_div] + wrapper.group(1) + "\n" + body + "\n          " + wrapper.group(3) + src[end:]


def main():
    check = "--check" in sys.argv

    over = [v for v, limit in LIMITS.items() if limit and length(v) > limit]
    if over:
        for v in over:
            print("  !! the %s biography is %d characters, over its %d limit"
                  % (v, length(v), LIMITS[v]))
        return 1

    src = open(ABOUT, encoding="utf-8").read()
    out = src
    for version in ("long", "medium", "short"):
        out = block(version, out)
        # the tab says how long its version is, as the artist pages do
        tag = '<span class="bt-meta" data-bio-count="%s">' % version
        i = out.index(tag) + len(tag)
        out = out[:i] + "{} characters".format(length(version)) + out[out.index("</span>", i):]

    stale = []
    if out != src:
        stale.append(ABOUT)
        if not check:
            open(ABOUT, "w", encoding="utf-8").write(out)

    for version in BIOS:
        path = TXT.format(version)
        wanted = "CreArtBox\nBiography ({})\n\n{}\n\ncreartbox.nyc · info@creartbox.nyc\n".format(
            version, "\n\n".join(plain(p) for p in BIOS[version]))
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if current != wanted:
            stale.append(path)
            if not check:
                open(path, "w", encoding="utf-8").write(wanted)

    if check:
        if stale:
            print("organisation biography out of date ({}):".format(len(stale)))
            for p in stale:
                print("  -", p)
            print("\nRun: python3 tools/build_org_bio.py && node tools/render_press_bios.js")
            return 1
        print("organisation biography up to date: " + ", ".join(
            "{} {}".format(v, length(v)) for v in ("short", "medium", "long")))
        return 0

    for v in ("short", "medium", "long"):
        print("%-7s %4d characters%s" % (
            v, length(v), "" if not LIMITS[v] else " (limit %d)" % LIMITS[v]))
    print("\nNow run: node tools/render_press_bios.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
