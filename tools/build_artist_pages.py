#!/usr/bin/env python3
"""A page for each member of the ensemble, with both biographies.

    python3 tools/build_artist_pages.py            # write artists/*.html
    python3 tools/build_artist_pages.py --check    # fail if out of date

Every word below is the artist's own. The long biography is reproduced
exactly as it stands on their website, or in the case of Matthew Cohen
exactly as his own press document has it - his file asks that it not be
altered, and that holds here. The short biography is theirs too: where
they publish one, it is that; where they do not, it is their own
sentences with the lists trimmed, never a new claim.

Nothing here may be embellished. If a fact is not in the source it does
not go on the page; ask the artist instead.

The script also keeps the ensemble cards on about.html in step: the short
biography, a link to the full page, and no list of affiliations under it.
"""

import html
import os
import re
import sys

SITE = "https://creartbox.nyc"

ARTISTS = [
    {
        "slug": "guillermo-laporta",
        "anchor": "member-laporta",
        "name": "Guillermo Laporta",
        "role": "Flute · Executive Director",
        "photo": "assets/img/guillermo-laporta.png",
        "links": [],
        # CreArtBox's own text. He publishes no personal biography.
        "short": [
            "Flutist, composer, and multimedia creator. Executive Director of CreArtBox "
            "and Festival ADAR. At the heart of his practice lies the concept of the "
            "&quot;visual concert&quot; - multimedia performances that weave visual art and "
            "theatrical design into live chamber music. His work has been praised by "
            "<em>The New Yorker</em>, <em>Time Out</em>, and <em>Broadway World</em>."
        ],
        "long": [],
        "note": "Guillermo Laporta has no published long biography.",
    },
    {
        "slug": "josefina-urraca",
        "anchor": "member-urraca",
        "name": "Josefina Urraca",
        "role": "Piano · Co-Director",
        "photo": "assets/img/josefina-urraca.png",
        "links": [("Website", "https://josefinaurraca.com")],
        "short": [
            "Josefina Urraca is a Spanish pianist and co-director of CreArtBox and the "
            "Festival ADAR. Her playing has been praised by <em>Mundo Clásico</em> for its "
            "blend of &quot;introspection and musical abandon&quot; - a balance between "
            "precision and emotional risk that defines her work both on stage and behind it.",
            "She has performed at the Salle Cortot in Paris, the Collège d&#x27;Espagne at "
            "the Cité Internationale Universitaire de Paris, the Sony Auditorium in Madrid, "
            "Carnegie Hall in New York, among others.",
        ],
        "long": [
            "Josefina Urraca is a Spanish pianist and co-director of CreArtBox and the "
            "Festival ADAR. Her playing has been praised by <em>Mundo Clásico</em> for its "
            "blend of &quot;introspection and musical abandon&quot; - a balance between "
            "precision and emotional risk that defines her work both on stage and behind it.",
            "She has performed at the Salle Cortot in Paris, the Collège d&#x27;Espagne at "
            "the Cité Internationale Universitaire de Paris, the Sony Auditorium in Madrid, "
            "Carnegie Hall in New York, among others. Her work has also reached wider "
            "audiences through appearances on Spanish television and radio.",
            "In 2013, alongside flutist Guillermo Laporta, she co-founded CreArtBox, a New "
            "York-based chamber music ensemble that fuses live performance with visual art, "
            "projection, and theatrical staging. Over the past decade, she has led its "
            "artistic direction - designing programs, commissioning new work, and building "
            "collaborations with composers and visual artists. The ensemble has been "
            "recognized by <em>The New Yorker</em> as one of its top picks for art and music, "
            "and by <em>Time Out New York</em> as &quot;a group dedicated to multidisciplinary "
            "events.&quot;",
            "Since 2021, together with Laporta, she has co-directed Festival ADAR, a "
            "traveling arts festival in rural Asturias that weaves classical concerts, "
            "commissioned works, artist talks, and site-specific installations into the "
            "landscape of small villages. The festival has become a model for how "
            "contemporary art can revitalize rural heritage.",
            "Over fifteen years, her work has received support from institutions including "
            "the New York State Council on the Arts, the NYC Department of Cultural Affairs, "
            "the Amphion Foundation, the Copland Foundation, and the Alice M. Ditson Fund, "
            "the Government of Asturias, the Queens Council on the Arts, the Spanish Embassy, "
            "Caja Madrid, the Luis Galvé Foundation, the Albéniz Foundation, and Caja Rural. "
            "She has been recognized in competitions including the Savvy Musicians in Action "
            "International Competition, INJUVE, Montehermoso Contemporary Creation, the "
            "Ciudad de Carlet International Competition, and the Rotary Club awards.",
            "Her training took shape across the Salamanca Conservatory, the University of "
            "Alcalá de Henares in Madrid, the École Normale de Musique &quot;Alfred "
            "Cortot&quot; in Paris, the Reina Sofía School of Music in Madrid, and the "
            "Manhattan School of Music in New York. She has studied with Dmitri Bashkirov, "
            "Maria João Pires, Ferenc Rados, Patrín García-Barredo, Josep Colom, Claudio "
            "Martínez-Mehner, Kennedy Moretti, Eldar Nebolsin, Marc Silverman, Márta Gulyás "
            "and Frank Wibaut.",
            "Born into a family of professional musicians in Palencia, she divides her life "
            "between New York and Leiguarda, a small village in Asturias, where she lives "
            "with her husband Guillermo and their son and daughter Eliot and Emilia.",
        ],
        "note": "As published on josefinaurraca.com.",
    },
    {
        "slug": "emilie-anne-gendron",
        "anchor": "member-gendron",
        "name": "Emilie-Anne Gendron",
        "role": "Violin",
        "photo": "assets/img/emilie-gendron.webp",
        "links": [("Website", "https://www.emilieannegendron.com"),
                  ("Instagram", "https://www.instagram.com/elgendron/")],
        "short": [
            "Violinist Emilie-Anne Gendron, lauded by the <em>New York Times</em> as a "
            "&quot;brilliant soloist&quot; and by <em>Strad Magazine</em> for her "
            "&quot;marvelous and lyrical playing,&quot; enjoys a dynamic career based in New "
            "York City. A deeply committed chamber musician, she is a longtime member of the "
            "Momenta Quartet, and a member and one of the concertmasters of the acclaimed "
            "Orpheus Chamber Orchestra.",
            "She is a founding member of Ensemble Échappé, a new-music sinfonietta, and of "
            "Gamut Bach Ensemble. She holds a B.A. in Classics and Ancient Studies from "
            "Columbia University, and a Master of Music degree and the coveted Artist Diploma "
            "from Juilliard. She plays on a 1673 Jacob Stainer violin on generous loan from "
            "the Englewood Chamber Players.",
        ],
        "long": [
            "Violinist Emilie-Anne Gendron, lauded by the <em>New York Times</em> as a "
            "&quot;brilliant soloist&quot; and by <em>Strad Magazine</em> for her "
            "&quot;marvelous and lyrical playing,&quot; enjoys a dynamic career based in New "
            "York City. A deeply committed chamber musician, Ms. Gendron is a longtime member "
            "of the Momenta Quartet, currently quartet-in-residence at Binghamton University, "
            "and whose vision encompasses contemporary music of all backgrounds alongside "
            "great music from the past. She is a member and one of the concertmasters of the "
            "acclaimed Orpheus Chamber Orchestra and also collaborates with groups such as A "
            "Far Cry, Argento Chamber Ensemble, Chamber Music Society of Lincoln Center, "
            "Chamber Orchestra of Philadelphia, CreArtBox, INTERWOVEN, Iris Collective (as one "
            "of its concertmasters), Marlboro Music Festival / Musicians From Marlboro, New "
            "Asia Chamber Music Society, Orchestra of St. Luke&#x27;s, Talea Ensemble, The "
            "Knights, and Sejong. She is a founding member of Ensemble Échappé, a new-music "
            "sinfonietta, and of Gamut Bach Ensemble, in residence with the Philadelphia "
            "Chamber Music Society. Other regular collaborations include the Melody and "
            "Company chamber series with pianist Melody Fader and the longstanding G-Sharp "
            "Duo, founded with pianist Yelena Grinberg in 2003.",
            "Ms. Gendron is also a sought-after educator and clinician. She has been one of "
            "the violinists of the Toomai String Quintet, devoted to a variety of styles from "
            "around the world and specializing in educational outreach and community "
            "engagement, since 2009. Toomai (one of the original pilot ensembles in Carnegie "
            "Hall&#x27;s &quot;Musical Connections&quot; program) helped design composition "
            "and performance workshops with incarcerated men at Sing Sing Correctional "
            "Facility; has worked with student composers in the New York Philharmonic&#x27;s "
            "Very Young Composers Program and with NYC public school students through the "
            "&quot;Midori and Friends&quot; initiative; and presents at institutions across "
            "the U.S. ranging from grade school to university level. As a member of the "
            "Momenta Quartet, Ms. Gendron gives masterclasses and coachings on their "
            "educational-performing circuit of nearly 40 institutions ranging from public and "
            "arts schools, universities, and conservatories in the U.S. and as far afield as "
            "Bolivia, Hong Kong, Indonesia, and Mexico. Ms. Gendron has also served as guest "
            "chamber music coach for the Juilliard School&#x27;s Music Advancement Program and "
            "at the Longy School of Music; as violin specialist for student composers at "
            "Juilliard&#x27;s Evening Division, NYU, and Fordham University; and as a coach "
            "and performer at the annual Composers Conference.",
            "Ms. Gendron&#x27;s extensively varied international appearances have included "
            "recitals in Sweden and at the Louvre in Paris; festivals in Russia, Finland, "
            "Indonesia, South Korea, and Jordan; and major venues across the Americas, Europe, "
            "and Asia. Her performances have been broadcast over radio and television in the "
            "U.S., U.K., Switzerland, New Zealand, Canada, Denmark, Japan, and South Korea. "
            "She is a past winner of the Stulberg String Competition and took 2nd Prize and "
            "the Audience Prize at the Sion-Valais (formerly Tibor Varga) International Violin "
            "Competition.",
            "Born in the U.S. to Japanese and French-Canadian parents, and a dual citizen of "
            "the U.S. and Canada, Ms. Gendron began her violin studies at age 4 with Carl "
            "Shugart and Carol Sykes. Her subsequent training at the Juilliard School was "
            "overseen by teachers Dorothy DeLay, Won-Bin Yim, Hyo Kang, and David Chan. Ms. "
            "Gendron holds the distinction of being the first person in Juilliard&#x27;s "
            "history to be accepted simultaneously to its two most selective courses of study, "
            "both the Doctor of Musical Arts and the Artist Diploma. She holds a B.A. in "
            "Classics and Ancient Studies (<em>magna cum laude</em> and with Phi Beta Kappa "
            "honors) from Columbia University, and a Master of Music degree and the coveted "
            "Artist Diploma from Juilliard.",
            "Outside her profession, Ms. Gendron enjoys salsa dancing, fitness training, and "
            "exploring the many museums and galleries New York has to offer. She is not "
            "related to the famed 20th-century cellist Maurice Gendron.",
            "Ms. Gendron plays on a 1673 Jacob Stainer violin on generous loan from the "
            "Englewood Chamber Players.",
        ],
        "note": "As published on emilieannegendron.com.",
    },
    {
        "slug": "matthew-cohen",
        "anchor": "member-cohen",
        "name": "Matthew Cohen",
        "role": "Viola",
        "photo": "assets/img/matthew-cohen.jpg",
        "links": [("Website", "https://www.cohenviola.com"),
                  ("Instagram", "https://www.instagram.com/mcohenviola/")],
        "short": [
            "Ukrainian-American violist Matthew Cohen is a dynamic and versatile artist whose "
            "captivating performances have made him one of the most sought-after violists of "
            "his generation. Recently appointed as the violist of the Formosa Quartet and a "
            "founding member of Ensemble Elatós, he was a special prize winner at the "
            "prestigious Primrose International Viola Competition as well as garnering top "
            "prizes at the Citta di Cremona International Viola Competition in Italy, Vivo "
            "International Music Competition and the Art of Duo International Competition. "
            "Particularly interested in advocating for the viola as a unique voice, he is "
            "challenging the misconception that the viola has a limited repertoire by bringing "
            "attention to lesser-known gems as well as arrangements of other masterworks.",
            "Recent solo engagements include his Lincoln Center debut performing Bartok&#x27;s "
            "Viola Concerto with the Juilliard Orchestra in Alice Tully Hall, Hummel&#x27;s "
            "Potpourri with the Gstaad Festival Orchestra, Bartok&#x27;s Viola Concerto with I "
            "Virtuosi Italiani in Cremona, Italy, and presenting the world premiere of Garry "
            "Schyman&#x27;s viola concerto &quot;Zingaro&quot; with the Los Angeles Jewish "
            "Symphony. Upcoming appearances include performances at Philadelphia Chamber Music "
            "Society, Irvine Philharmonic Society, Music Mondays - Toronto, the University of "
            "Houston, and recitals for the Performing Arts Consortium in Hilton Head, South "
            "Carolina and Core Memory Music in Wakefield, Rhode Island.",
            "Cohen is a graduate of the Juilliard School&#x27;s Master of Music program where "
            "he was the proud recipient of a Kovner Fellowship. He has served as a member of "
            "the chamber music faculty at the National Youth Orchestra of Canada and the "
            "Heifetz Institute and is the co-founder and Artistic Director of Opus 71 "
            "Concerts, a multidisciplinary concert series near New York&#x27;s Lincoln Center. "
            "His recording of York Bowen&#x27;s <em>Phantasy</em> for viola and piano with "
            "acclaimed pianist Vivian Fan is available on the Soundset label.",
            "In addition to his musical activities, he enjoys public speaking and has acted in "
            "a number of plays including various works of Shakespeare, <em>Peter Pan</em>, "
            "<em>Auntie Mame</em>, and the musical <em>Bugsy Malone</em>.",
        ],
        "long": [
            "Ukrainian-American violist Matthew Cohen is a dynamic and versatile artist whose "
            "captivating performances have made him one of the most sought-after violists of "
            "his generation. Recently appointed as the violist of the Formosa Quartet and a "
            "founding member of Ensemble Elatós, he was a special prize winner at the "
            "prestigious Primrose International Viola Competition as well as garnering top "
            "prizes at the Citta di Cremona International Viola Competition in Italy, Vivo "
            "International Music Competition and the Art of Duo International Competition. "
            "Particularly interested in advocating for the viola as a unique voice, he is "
            "challenging the misconception that the viola has a limited repertoire by bringing "
            "attention to lesser-known gems as well as arrangements of other masterworks.",
            "Since his first performance in Carnegie Hall&#x27;s Stern Auditorium at the age "
            "of 15 as a soloist in the New York premiere of Tomas Svoboda&#x27;s Sonata No. 2 "
            "for orchestra and solo string quartet, Cohen has concertized as a soloist with "
            "orchestras such as the Gstaad Festival Orchestra, I Virtuosi Italiani, The "
            "Juilliard Orchestra, Symphony in C, the North Shore Symphony Orchestra, the "
            "Colburn Orchestra, Oregon Sinfonietta, the MetroArts Inc. Orchestra, and gave the "
            "world premiere of internationally recognized video game score composer Garry "
            "Schyman&#x27;s viola concerto &quot;Zingaro&quot; with the Los Angeles Jewish "
            "Symphony. Upcoming engagements include performances at Philadelphia Chamber Music "
            "Society, Irvine Philharmonic Society, Kitchener-Waterloo Chamber Music Society, "
            "Music Mondays - Toronto, and recitals at the Bacon House in Washington, D.C. and "
            "for the Performing Arts Consortium in Hilton Head, South Carolina.",
            "A passionate chamber musician, Cohen has performed alongside many distinguished "
            "artists including members of ensembles such as the Aeolus, Borromeo, Guarneri, "
            "Jasper, Orion, Parker, Tokyo, and Vermeer string quartets and the Beaux Arts, "
            "Horszowski and Tempest piano trios, and has been featured by numerous concert "
            "series and festivals including Bargemusic, Camerata Pacifica, ChamberFest "
            "Cleveland, the Colburn Chamber Music Society, Heifetz Celebrity Series, Jupiter "
            "Symphony Chamber Players, Methow Valley Chamber Music Festival, Olmos Ensemble, "
            "Ringwood Friends of Chamber Music, and Ravinia&#x27;s Steans Music Institute. He "
            "has served as a member of the chamber music faculty at the National Youth "
            "Orchestra of Canada and the Heifetz Institute&#x27;s Junior Division and is the "
            "co-founder and Artistic Director of Opus 71 Concerts, a multidisciplinary concert "
            "series near New York&#x27;s Lincoln Center",
            "As a graduate of the Juilliard School&#x27;s Master of Music program, he was the "
            "proud recipient of a Kovner Fellowship; he earned his Bachelor of Music degree "
            "from Cleveland Institute of Music and received an Artist Diploma from Colburn "
            "Conservatory where he studied with Misha Amory, Heidi Castleman, Paul Coletti, "
            "Jeffrey Irvine, and Cynthia Phelps.",
            "His recording of York Bowen&#x27;s <em>Phantasy</em> for viola and piano with "
            "acclaimed pianist Vivian Fan is available on the Soundset label. In addition to "
            "his musical activities, he enjoys public speaking and has acted in a number of "
            "plays including various works of Shakespeare, <em>Peter Pan</em>, <em>Auntie "
            "Mame</em>, and the musical <em>Bugsy Malone</em>.",
        ],
        "note": "As supplied by the artist. Reproduced without alteration at his request.",
    },
    {
        "slug": "julia-yang",
        "anchor": "member-yang",
        "name": "Julia Yang",
        "role": "Cello",
        "photo": "assets/img/julia-yang.jpg",
        "links": [("Website", "https://www.juliayangcello.com"),
                  ("Instagram", "https://www.instagram.com/juliayangcello/")],
        "short": [
            "Praised for &quot;her sense of joyful virtuosity&quot; as concerto soloist "
            "(<em>South Florida Classical Review</em>), Julia Yang is a courageous and soulful "
            "cellist, multi-faceted performer, and founding member of the "
            "&quot;riveting&quot; (<em>Reading Eagle</em>) and &quot;impeccably elegant&quot; "
            "Merz Trio (<em>All About the Arts</em>) and freshly minted clarinet-cello-piano "
            "ensemble, Trio Phōs.",
            "Yang&#x27;s Merz Trio are first prize winners of the prestigious Naumburg Chamber "
            "Music Prize as well as of the Concert Artists Guild, Fischoff and Chesapeake "
            "International Chamber Music competitions. She has collaborated in chamber music "
            "with numerous artists including Jonathan Biss, Mitsuko Uchida, and Kim "
            "Kashkashian at festivals such as the Marlboro Music Festival, Yellow Barn and "
            "Tippet Rise. Yang holds degrees from Northwestern University and the New England "
            "Conservatory.",
        ],
        "long": [
            "Praised for &quot;her sense of joyful virtuosity&quot; as concerto soloist "
            "(<em>South Florida Classical Review</em>), Julia Yang is a courageous and soulful "
            "cellist, multi-faceted performer, and founding member of the "
            "&quot;riveting&quot; (<em>Reading Eagle</em>) and &quot;impeccably elegant&quot; "
            "Merz Trio (<em>All About the Arts</em>) and freshly minted clarinet-cello-piano "
            "ensemble, Trio Phōs.",
            "On stage, Yang has been described as the &quot;stunning find of the evening&quot; "
            "(<em>New York Classical Review</em>) and has been noted for her &quot;dark, "
            "voluminous tone&quot; and &quot;utterly compelling&quot; performances (<em>South "
            "Florida Classical Review</em>). Recent and upcoming concerto highlights include "
            "Haydn C major, Brahms Double Concerto and Dvořák concerto performances as well "
            "the premiere and recording of a new cello concerto by Jeffrey Mumford.",
            "Yang&#x27;s Merz Trio are first prize winners of the prestigious Naumburg Chamber "
            "Music Prize as well as of the Concert Artists Guild, Fischoff and Chesapeake "
            "International Chamber Music competitions. The Trio presents innovative "
            "multidisciplinary concert experiences that interweave repertoire of the "
            "traditional piano trio genre with diverse art forms ranging from the visual arts, "
            "literature and dance to theatre and the culinary arts. With the Trio, Yang "
            "released a debut album <em>INK</em> (August 2021), described as "
            "&quot;entrancing&quot; (<em>BBC</em>), which brings together the words and music "
            "of Parisian composers and writers around 1914. Merz Trio is managed by Dinin Arts.",
            "Yang maintains an active concertizing schedule with highlights on The Belvedere "
            "Series, Tippet Rise, NYC&#x27;s People&#x27;s Symphony Concerts, "
            "Philadelphia&#x27;s Chamber Music Society and San Miguel De Allende&#x27;s Pro "
            "Musica. She has performed throughout the United States and internationally in "
            "Europe, South America, Australia, Canada and Mexico and has been featured as a "
            "Young Artist in Residence on <em>Performance Today</em> with Fred Child. Top "
            "prizes at solo competitions include the Lennox International Competition and the "
            "Union League of Chicago&#x27;s Young Artist Competition.",
            "Yang has collaborated in chamber music with numerous artists including Jonathan "
            "Biss, Mitsuko Uchida, and Kim Kashkashian at festivals such as the Marlboro Music "
            "Festival (Marlboro VT), Lake Champlain Chamber Music Festival (Burlington, VT), "
            "Yellow Barn (Putney, VT), The Valley of the Moon Festival (Sonoma, CA), At the "
            "World&#x27;s Edge Festival (Chicago, IL), Tippet Rise (Fishtail, MT) and "
            "Poland&#x27;s Krzyzowa-Music. Her solo and chamber music performances have been "
            "broadcast on national radio throughout the United States as well as in the "
            "Netherlands, Germany, Poland, and BBC Radio 3.",
            "Yang&#x27;s orchestral leadership experience includes serving as principal "
            "cellist of the Colorado Music Festival under Peter Oundjian, performing with "
            "conductor-less orchestras such as A Far Cry and East Coast Chamber Orchestra "
            "(ECCO) and touring as principal of the New World Symphony where she was a fellow "
            "for two seasons. In addition, she has performed as principal cellist under "
            "conductors such as Michael Tilson Thomas, Susanna Mälkki, James Gaffigan, John "
            "Adams, and Leonard Slatkin and many others in halls including Carnegie Hall, "
            "Boston&#x27;s Symphony Hall, the Kennedy Center and Miami&#x27;s New World Center "
            "and Arsht Center.",
            "As educator and pedagogue, Yang finds particular joy in working with the younger "
            "generation of musicians. She regularly gives masterclasses and has held "
            "residencies at numerous college and graduate programs including MIT, Rice "
            "University&#x27;s Shepherd School of Music, Duke University, Florida State "
            "University and the University of North Texas. Currently, she co-directs "
            "Avant-Garden, the University of Oklahoma&#x27;s contemporary chamber music "
            "ensemble. From 2024-26, she served as the Visiting Assistant Professor of Cello "
            "at the Ohio State University. Yang has been an invited guest performer and coach "
            "at the New World Symphony, held educational residencies as a guest artist for New "
            "England Conservatory&#x27;s Prep Division and as guest artist faculty at the Lyra "
            "Music Festival, the Four Seasons Chamber Music Institute and as an Interactive "
            "Performance Coach at Carnegie Hall&#x27;s Audience Engagement Intensive. While a "
            "fellow of Carnegie Hall&#x27;s Ensemble Connect (2016-18), Yang worked with NYC "
            "public schools&#x27; music programs and gave dozens of interactive performances "
            "for wide-ranging communities.",
            "Yang holds degrees from Northwestern University and the New England Conservatory, "
            "studying with Hans Jørgen Jensen, Laurence Lesser and Yeesun Kim, as well as "
            "former teachers Greg Sauer and Lubomir Georgiev. Away from the cello, you&#x27;ll "
            "find her reading or checking out the local arts scene, enjoying the outdoors, or "
            "cooking and crafting cocktails.",
        ],
        "note": "As published on juliayangcello.com.",
    },
]

CARD_RE_TEMPLATE = r'(<article id="{anchor}".*?)(</article>)'
BIO_RE = re.compile(r'(<p class="body-l"[^>]*>)(.*?)(</p>)', re.S)
TAGS_RE = re.compile(r'\s*<ul style="list-style:none;padding:0;margin:18px 0 0;'
                     r'display:flex;flex-wrap:wrap;gap:18px;font-style:italic;'
                     r'color:var\(--ink-soft\)">.*?</ul>', re.S)
BUTTONS_RE = re.compile(r'(<div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">)(.*?)(</div>)', re.S)
FULL_BIO_RE = re.compile(r'\s*<a href="artists/[^"]+" class="btn btn-s btn-stamp">.*?</a>', re.S)


def page(artist):
    links = "".join(
        '<a class="btn" href="{url}" target="_blank" rel="noopener">{label} '
        '<span class="ar">&#8594;</span></a>'.format(label=label, url=url)
        for label, url in artist["links"])
    short = "\n".join("        <p>{}</p>".format(p) for p in artist["short"])
    if artist["long"]:
        body = "\n".join("          <p>{}</p>".format(p) for p in artist["long"])
        long_block = (
            '        <section class="artist-bio">\n'
            '          <h2 class="event-h2">Biography</h2>\n'
            + body + "\n"
            '          <p class="artist-source">{}</p>\n'
            '        </section>'.format(artist["note"]))
    else:
        long_block = ""

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} · {role} · CreArtBox</title>
<meta name="description" content="{name}, {role_plain}. Biography and performances with CreArtBox.">
<link rel="canonical" href="{site}/artists/{slug}.html">
<link rel="icon" type="image/svg+xml" href="../brand/mark-wedge-box.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,300..700;1,300..700&family=Literata:ital,opsz,wght@0,7..72,300..700;1,7..72,300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/styles.css?v=120">
<script id="cb-theme-init">document.documentElement.setAttribute("data-theme","dark");</script>
</head>
<body>

<header class="masthead">
  <div class="masthead-inner">
    <div class="masthead-left"><button class="nav-burger" aria-label="Menu">Menu</button><span class="established">Established 2013, New York City</span></div>
    <a class="masthead-title" href="../index.html"><img class="logo-img" src="../brand/logo-creartbox-reversed.svg" alt="CreArtBox"></a>
    <div class="masthead-right"><a class="masthead-tickets" href="../concerts.html">Get tickets</a></div>
  </div>
  <nav class="nav-strip">
    <div class="nav-strip-inner">
      <div class="nav-item"><a href="../index.html">Home</a></div>
      <div class="nav-item"><a href="../about.html" class="active">About</a></div>
      <div class="nav-item"><a href="../concerts.html">Calendar</a></div>
      <div class="nav-item"><a href="../archive.html">Archive</a></div>
      <div class="nav-item"><a href="../projects.html">Projects</a></div>
      <div class="nav-item"><a href="../opportunities.html">Opportunities</a></div>
      <div class="nav-item"><a href="../media.html">Media</a></div>
      <div class="nav-item"><a href="../support.html">Donate</a></div>
    </div>
  </nav>
</header>

<main>

<section class="event-page artist-page">
  <div class="wrap">
    <a href="../about.html#ensemble" class="back-to-archive">&#8592; The ensemble</a>

    <header class="event-header">
      <div class="event-series">{role}</div>
      <h1 class="event-title">{name}</h1>
    </header>

    <div class="event-layout">
      <div class="event-main">
        <section class="artist-lede">
{short}
        </section>
{long_block}
      </div>
      <aside class="event-sidebar">
        <figure class="artist-portrait"><img src="../{photo}" alt="{name}, {role_plain}"></figure>
        <div class="artist-links">{links}
          <a class="btn" href="../concerts.html">Upcoming concerts</a>
        </div>
        <div class="event-foot">
          <a href="../about.html#ensemble" class="btn">&#8592; The ensemble</a>
        </div>
      </aside>
    </div>
  </div>
</section>

</main>

<footer class="colophon">
  <div class="wrap">
    <div class="colophon-grid">
      <div>
        <div class="colophon-mark"><img src="../brand/mark-wedge-amber.svg" alt="CreArtBox" width="52" height="24"></div>
        <p class="colophon-bio">A 501(c)(3) non-profit chamber music and multimedia ensemble. New York · Asturias.</p>
        <p class="colophon-addr">info@creartbox.nyc · 10–48 47th Road, Unit 1, Queens, NY 11101</p>
      </div>
      <div><h4>Program</h4><ul><li><a href="../concerts.html">Calendar</a></li><li><a href="../archive.html">Archive of Performances</a></li><li><a href="../projects.html">Productions</a></li><li><a href="https://festivaladar.com" target="_blank" rel="noopener">Festival ADAR</a></li><li><a href="https://apps.apple.com/us/app/creartbox/id6746415261" target="_blank" rel="noopener">iOS app · App Store</a></li></ul></div>
      <div><h4>The Organization</h4><ul><li><a href="../about.html">About</a></li><li><a href="../opportunities.html">Opportunities</a></li><li><a href="../brand.html">Brand &amp; press kit</a></li><li><a href="../media.html#magazine">CreArt Magazine</a></li></ul></div>
      <div><h4>Give</h4><ul><li><a href="../support.html">Donate</a></li></ul></div>
    </div>
    <div class="colophon-bot"><span>© CreArtBox, Inc. 2013–2027 · 501(c)(3) non-profit</span></div>
  </div>
</footer>

<script src="../assets/site.js?v=38"></script>
</body>
</html>
""".format(name=html.escape(artist["name"]), role=artist["role"],
           role_plain=artist["role"].split(" · ")[0].lower(),
           slug=artist["slug"], photo=artist["photo"], site=SITE,
           short=short, long_block=long_block, links=links)


def sync_card(src, artist):
    """The about page carries the short bio, and a way through to the rest."""
    card = re.search(CARD_RE_TEMPLATE.format(anchor=artist["anchor"]), src, re.S)
    if not card:
        print("  !! no card for", artist["name"])
        return src
    body = card.group(1)

    # the short biography, as one paragraph
    short = " ".join(artist["short"])
    body = BIO_RE.sub(lambda m: m.group(1) + short + m.group(3), body, count=1)
    # the list of affiliations under it goes
    body = TAGS_RE.sub("", body)

    buttons = BUTTONS_RE.search(body)
    link = ('<a href="artists/{}.html" class="btn btn-s btn-stamp">Full biography '
            '<span class="ar">&#8594;</span></a>'.format(artist["slug"]))
    if buttons:
        inner = FULL_BIO_RE.sub("", buttons.group(2))
        body = body.replace(buttons.group(0),
                            buttons.group(1) + link + inner + buttons.group(3), 1)
    else:
        body += ('\n        <div style="margin-top:16px;display:flex;gap:8px;'
                 'flex-wrap:wrap">' + link + "</div>\n      ")
    return src.replace(card.group(0), body + card.group(2), 1)


def main():
    check = "--check" in sys.argv
    stale = []

    for artist in ARTISTS:
        path = os.path.join("artists", artist["slug"] + ".html")
        wanted = page(artist)
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if current != wanted:
            stale.append(path)
            if not check:
                os.makedirs("artists", exist_ok=True)
                open(path, "w", encoding="utf-8").write(wanted)

    src = open("about.html", encoding="utf-8").read()
    out = src
    for artist in ARTISTS:
        out = sync_card(out, artist)
    if out != src:
        stale.append("about.html")
        if not check:
            open("about.html", "w", encoding="utf-8").write(out)

    if check:
        if stale:
            print("artist pages out of date ({}):".format(len(stale)))
            for p in stale:
                print("  -", p)
            print("\nRun: python3 tools/build_artist_pages.py")
            return 1
        print("artist pages up to date: {}".format(len(ARTISTS)))
        return 0

    print("wrote {} artist page(s)".format(len(ARTISTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
