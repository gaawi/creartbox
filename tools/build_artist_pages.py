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

Each page offers the biography at three lengths - full, medium and short
- and the switch in the sidebar picks one. An artist who writes their own
three gets those, in "versions"; for everyone else the shorter two are
the opening of the full text, cut at a sentence break. Either way a press
desk can take any of them and quote it as the artist wrote it.

The script also keeps the ensemble cards on about.html in step: one
paragraph, the name linking through to the page, and no list of
affiliations under it.
"""

import html
import os
import re
import sys

SITE = "https://creartbox.nyc"

ARTISTS = [
    {
        "slug": "guillermo-laporta",
        "contact": ("guillermolaporta.com", "https://guillermolaporta.com"),
        "card": (
            "Guillermo Laporta is a Spanish flutist, composer, and designer based in New "
            "York City, co-founder and Artistic Director of CreArtBox and of Festival ADAR."),
        "anchor": "member-laporta",
        "name": "Guillermo Laporta",
        "role": "Flute · Executive Director",
        "photo": "assets/img/guillermo-laporta.png",
        "links": [("Website", "https://guillermolaporta.com")],
        "short": [],
        "long": [],
        # three texts of his own, not cuts of one another
        "versions": {
            "short": [
                "Guillermo Laporta is a Spanish flutist, composer, and designer based in New York "
                "City. He is co-founder and Artistic Director of CreArtBox, a New York-based piano "
                "quintet with an established concert season and touring activity, and Festival ADAR, "
                "dedicated to developing the arts in rural communities in Asturias. His work expands "
                "the flute repertoire through transcriptions and new music, while his operas and "
                "&quot;visual concerts&quot; combine classical music with visual storytelling.",
            ],
            "medium": [
                "Guillermo Laporta is a Spanish flutist, composer, and designer based in New York "
                "City. His artistic practice brings together classical music and visual storytelling. "
                "As a composer, he has written operas and multidisciplinary works including "
                "<em>Architecture of a Common Man</em> (2023) and <em>Two Roads</em> (2019), "
                "alongside productions he defines as &quot;visual concerts,&quot; integrating video, "
                "projection, lighting, and theatrical design into live classical music. Critics have "
                "praised his &quot;impressive staging&quot; (<em>El País</em>) and &quot;unique take "
                "on classical music&quot; (<em>Times Ledger</em>).",
                "Laporta co-founded CreArtBox with pianist Josefina Urraca in 2013 and serves as its "
                "Executive and Co-Artistic Director. CreArtBox is a New York-based piano quintet with "
                "an established concert season, touring activity, new commissions, and a growing "
                "network of artistic and institutional partnerships. They also founded Festival ADAR "
                "in rural Asturias, presenting concerts, residencies, and site-specific "
                "installations.",
                "Expanding the flute repertoire is a central part of Laporta&#x27;s work, reimagining "
                "works by composers such as Janáček, Sibelius, Respighi, and Dvořák for the flute, "
                "while contributing new works and commissions to the contemporary flute repertoire. "
                "This work is documented across three studio albums. As a performer, he has appeared "
                "with ensembles including the BBC Orchestra and at Carnegie Hall and Lincoln Center, "
                "with recording credits on Warner Music, EMI, and Naxos.",
                "Laporta studied at the Royal College of Music in London with flutist and conductor "
                "Jaime Martín.",
            ],
            "long": [
                "Guillermo Laporta is a Spanish flutist, composer, designer, and cultural producer "
                "based in New York City. His artistic practice brings together classical music and "
                "visual storytelling, exploring how music, video, projection, lighting, and "
                "theatrical design can become part of a unified live experience.",
                "As a composer and multidisciplinary artist, Laporta has created works including "
                "<em>Architecture of a Common Man</em> (2023), an opera-ballet-film for which he "
                "served as composer, dramaturg, librettist, and designer, and <em>Two Roads</em> "
                "(2019), an opera-ballet featured as a Critics&#x27; Pick in <em>The New Yorker</em>. "
                "Alongside these works, he has developed numerous productions he defines as "
                "&quot;visual concerts,&quot; integrating video, projection, lighting, and theatrical "
                "design into live classical music. Critics have praised his &quot;impressive "
                "staging&quot; (<em>El País</em>), &quot;unique take on classical music&quot; "
                "(<em>Times Ledger</em>), and &quot;full-scale set design with a unique visual "
                "approach&quot; (<em>I Care if You Listen</em>).",
                "Laporta began developing this multidisciplinary approach in Europe in 2006, when he "
                "co-founded Cre.Art Project with clarinetist and performance creator Tagore González. "
                "That same year, he received the Montehermoso Contemporary Creation Award, supporting "
                "an early chamber music production integrating electroacoustic music, video art, and "
                "choreography. During the following years, he developed increasingly ambitious "
                "productions including <em>London: The Show</em> (2009) and <em>Noctum</em> (2011), "
                "establishing the foundations of the artistic language that would later define his "
                "work in New York.",
                "In 2013, Laporta co-founded CreArtBox in New York City with pianist Josefina Urraca "
                "and serves as its Executive Director and Co-Artistic Director. Over more than a "
                "decade, he has helped develop CreArtBox into a New York-based piano quintet and "
                "multidisciplinary performing arts organization with an established concert season in "
                "the city, an active touring schedule, new commissions, and a growing network of "
                "artistic and institutional partnerships.",
                "Through CreArtBox, Laporta has conceived, curated, designed, and produced "
                "performances across New York and internationally. Projects such as <em>AWAVE</em> "
                "(2018-19), a collection of original works for flute, piano, electronics, and video "
                "presented in New York and Tokyo; <em>Queens Preludes</em> (2021), presented in New "
                "York, Madrid, and Tokyo; and the visual concert trilogy <em>Fragile Form</em> (2022) "
                "explore different relationships between live music and visual media.",
                "CreArtBox has presented performances at venues including The DiMenna Center for "
                "Classical Music, Mark Morris Dance Center, The William Vale, Culture Lab LIC, "
                "Greenwich House, and the New York Society for Ethical Culture, while developing "
                "collaborations and community partnerships across New York. The organization has "
                "received support from the New York State Council on the Arts and recognition from "
                "<em>The New Yorker</em>, <em>BroadwayWorld</em>, and <em>Time Out</em>.",
                "In 2020, Laporta and Urraca founded the Association for the Development of the Arts "
                "in Rural Areas (ADAR) in Asturias, Spain. Through its flagship Festival ADAR, they "
                "bring chamber music, new commissions, artist residencies, talks, visual "
                "installations, and site-specific projects to villages and landscapes outside "
                "traditional cultural centers. The project connects professional artists and "
                "international artistic exchange with rural communities and the cultural and natural "
                "heritage of Asturias.",
                "Expanding the flute repertoire is a central part of Laporta&#x27;s work, reimagining "
                "works by composers such as Janáček, Sibelius, Respighi, and Dvořák for the flute, "
                "while contributing new works and commissions to the contemporary flute repertoire. "
                "His catalogue includes original chamber and electroacoustic works such as "
                "<em>AWAVE</em>, <em>Twelve Preludes</em>, <em>Queens Log</em>, and <em>Música de "
                "Cristal</em>, alongside transcriptions and arrangements of repertoire originally "
                "written for other instruments and ensembles.",
                "This work is documented across three studio albums: <em>Debussy &amp; Respighi "
                "Violin Sonatas: Transcriptions for Flute and Piano</em>, <em>AWAVE</em>, and <em>12 "
                "Preludes</em>, combining his work as a flutist, composer, and arranger.",
                "As a performer, Laporta served as Co-Principal Flute of the Oviedo Filarmonía "
                "(2009-12), Principal Flute of the Herald Chamber Orchestra (2012-15), and Principal "
                "Flute of the New York International Chamber Orchestra (2013-18). He has also "
                "performed with ensembles including the BBC Orchestra, Orquesta Sinfónica del "
                "Principado de Asturias, Orquesta Sinfónica de Euskadi, and Le Train Bleu.",
                "He has performed at venues including Carnegie Hall and Lincoln Center and shared the "
                "stage with musicians and conductors including Sir Roger Norrington, Andrew Litton, "
                "Pablo González, Vladimir Ashkenazy, Truls Mørk, Natalia Gutman, the Labèque sisters, "
                "Ainhoa Arteta, Jirí Bárta, and Heinrich Schiff. His recording credits include Warner "
                "Music, EMI, and Naxos.",
                "Beyond his own productions, Laporta has developed an extensive body of work in "
                "visual and theatrical design. His credits include lighting and set design for Laura "
                "Kaminsky&#x27;s opera <em>As One</em> at the 14th Street Y Theater, <em>8 Million "
                "Protagonists</em> at HERE Arts Center, <em>Pedro Pan</em> in New York and Toronto, "
                "and <em>Painted Alice</em> at the Robert Moss Theater. He has also composed music "
                "and created sound design for virtual-reality and interactive-media projects.",
                "His work as a cultural producer extends beyond CreArtBox and ADAR. Over the course "
                "of his career, Laporta has founded and directed concert series and festivals, "
                "developed institutional partnerships, commissioned new works, and created platforms "
                "connecting musicians, composers, visual artists, venues, and audiences in the United "
                "States and Europe.",
                "Laporta studied flute performance at Musikene in San Sebastián and at the Royal "
                "College of Music in London, where he earned degrees in performance and advanced "
                "performance and studied with Jaime Martín, Paul Edmund-Davies, and Sue Thomas. He "
                "also holds a Master&#x27;s degree in Arts Management from the University of Alcalá "
                "de Henares.",
                "Across his work as a flutist, composer, designer, cultural producer, and artistic "
                "director, Laporta continues to explore new possibilities for classical music, from "
                "expanding the repertoire of the flute to developing new formats for live performance "
                "and building artistic organizations that connect musicians, artists, institutions, "
                "and audiences.",
            ],
        },
        "note": "As published on guillermolaporta.com.",
    },
    {
        "slug": "josefina-urraca",
        "contact": ("josefinaurraca.com", "https://josefinaurraca.com"),
        "card": (
            "Josefina Urraca is a Spanish pianist and co-director of CreArtBox and the "
            "Festival ADAR. Her playing has been praised by <em>Mundo Clásico</em> for its "
            "blend of &quot;introspection and musical abandon&quot; - a balance between "
            "precision and emotional risk that defines her work both on stage and behind it."),
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
        "contact": ("emilieannegendron.com", "https://www.emilieannegendron.com"),
        "card": (
            "Lauded by <em>The Strad</em> for her &quot;marvelous and lyrical playing,&quot; NYC- "
            "based violinist Emilie-Anne Gendron appears with Orpheus, Momenta Quartet, Toomai "
            "Quintet, Musicians from Marlboro, Orchestra of St. Luke&#x27;s, The Knights, Talea "
            "Ensemble, A Far Cry and Gamut Bach Ensemble, among others."),
        "anchor": "member-gendron",
        "name": "Emilie-Anne Gendron",
        "role": "Violin",
        "photo": "assets/img/emilie-gendron.webp",
        "links": [("Website", "https://www.emilieannegendron.com"),
                  ("Instagram", "https://www.instagram.com/elgendron/")],
        "short": [],
        "long": [],
        # her own three, confirmed by her
        "versions": {
            "short": [
                "Lauded by <em>The Strad</em> for her &quot;marvelous and lyrical playing,&quot; NYC- "
                "based violinist Emilie-Anne Gendron appears with Orpheus, Momenta Quartet, Toomai "
                "Quintet, Musicians from Marlboro, Orchestra of St. Luke&#x27;s, The Knights, Talea "
                "Ensemble, A Far Cry and Gamut Bach Ensemble, among others. A U.S.-Canadian citizen, "
                "she holds a B.A. from Columbia and Master of Music and Artist Diploma from "
                "Juilliard. She plays a 1673 Jacob Stainer violin on loan from the Englewood Chamber "
                "Players.",
            ],
            "medium": [
                "Violinist Emilie-Anne Gendron, lauded by the <em>New York Times</em> as a "
                "&quot;brilliant soloist&quot; and by <em>The Strad</em> for her &quot;marvelous and "
                "lyrical playing,&quot; enjoys a multifaceted career based in NYC. She is a member of "
                "the Orpheus Chamber Orchestra; the Momenta Quartet, championing contemporary music "
                "of all backgrounds alongside great music from the past; and the Toomai Quintet, "
                "devoted to a variety of styles from around the world. Ms. Gendron also collaborates "
                "with Musicians from Marlboro, Orchestra of St. Luke&#x27;s, The Knights, Talea "
                "Ensemble, A Far Cry, Sejong and Gamut Bach Ensemble. Her broad musical interests "
                "have led her everywhere from soloing in Carnegie Hall, to backing up The Roots on "
                "Jimmy Fallon, to helping develop music workshops with incarcerated men at Sing Sing "
                "Correctional Facility, to performing live on Radiolab at BAM. Internationally, Ms. "
                "Gendron&#x27;s appearances have included recitals across Sweden and at the Louvre in "
                "Paris; festivals in Mexico, Russia, Finland and Jordan; and major venues in China, "
                "South Korea, Indonesia, Bolivia and Chile, to name a few.",
                "A U.S.-Canadian citizen, Ms. Gendron trained at Juilliard under Won-Bin Yim, Dorothy "
                "DeLay, David Chan and Hyo Kang. She holds a B.A. in Classics and Ancient Studies "
                "from Columbia University (<em>magna cum laude</em>, Phi Beta Kappa) and a Master of "
                "Music degree and the coveted Artist Diploma from Juilliard. She plays on a 1673 "
                "Jacob Stainer violin on generous loan from the Englewood Chamber Players.",
            ],
            "long": [
                "Violinist Emilie-Anne Gendron, lauded by the <em>New York Times</em> as a "
                "&quot;brilliant soloist&quot; and by <em>The Strad</em> for her &quot;marvelous and "
                "lyrical playing,&quot; enjoys a dynamic career based in New York City. A deeply "
                "committed chamber musician, Ms. Gendron is a longtime member of the Momenta Quartet, "
                "in residence at Binghamton University, and whose vision encompasses contemporary "
                "music of all backgrounds alongside great music from the past. She is a member and "
                "one of the concertmasters of the acclaimed Orpheus Chamber Orchestra and also has "
                "collaborated with groups such as A Far Cry, Argento Chamber Ensemble, Chamber Music "
                "Society of Lincoln Center, Chamber Orchestra of Philadelphia, CreArtBox, INTERWOVEN, "
                "Iris Collective (as one of its concertmasters), Marlboro Music Festival/Musicians "
                "From Marlboro, New Asia Chamber Music Society, Orchestra of St. Luke&#x27;s, Talea "
                "Ensemble, The Knights, and Sejong. She is a founding member of Ensemble Échappé, a "
                "new-music sinfonietta, and of Gamut Bach Ensemble, in residence at the Philadelphia "
                "Chamber Music Society.",
                "Ms. Gendron is also a sought-after educator and clinician. She has been one of the "
                "violinists of the Toomai String Quintet, devoted to a variety of styles from around "
                "the world and specializing in educational outreach and community engagement, since "
                "2009. Toomai (one of the original pilot ensembles in Carnegie Hall&#x27;s "
                "&quot;Musical Connections&quot; program) helped design composition and performance "
                "workshops with incarcerated men at Sing Sing Correctional Facility; has worked with "
                "student composers in the New York Philharmonic&#x27;s Very Young Composers Program "
                "and with NYC public school students through the &quot;Midori and Friends&quot; "
                "initiative; and presents at institutions across the U.S. ranging from grade school "
                "to university level. As a member of the Momenta Quartet, Ms. Gendron gives "
                "masterclasses and coachings on their educational-performing circuit of nearly 40 "
                "institutions ranging from public and arts schools, universities, and conservatories "
                "in the U.S. and as far afield as Bolivia, Hong Kong, Indonesia, and Mexico. Ms. "
                "Gendron has also served as guest chamber music coach for the Juilliard School&#x27;s "
                "Music Advancement Program and at the Longy School of Music; as violin specialist for "
                "student composers at Juilliard&#x27;s Evening Division, NYU, and Fordham University; "
                "and as a coach and performer at the annual Composers Conference.",
                "Ms. Gendron&#x27;s extensively varied international appearances have included "
                "recitals in Sweden and at the Louvre in Paris; festivals in Russia, Finland, "
                "Indonesia, South Korea, and Jordan; and major venues across the Americas, Europe, "
                "and Asia. Her performances have been broadcast over radio and television in the "
                "U.S., U.K., Switzerland, New Zealand, Canada, Denmark, Japan, and South Korea. She "
                "is a past winner of the Stulberg String Competition and took 2nd Prize and the "
                "Audience Prize at the Sion-Valais (formerly Tibor Varga) International Violin "
                "Competition.",
                "A dual citizen of the U.S. and Canada, Ms. Gendron trained at the Juilliard School "
                "with Dorothy DeLay, Won-Bin Yim, Hyo Kang, and David Chan. She holds a B.A. in "
                "Classics and Ancient Studies (<em>magna cum laude</em> and with Phi Beta Kappa "
                "honors) from Columbia and a Master of Music degree and the coveted Artist Diploma "
                "from Juilliard. Outside her profession, she enjoys salsa dancing, fitness training, "
                "and exploring the many museums and galleries New York has to offer. She is not "
                "related to the famed 20th-century cellist Maurice Gendron.",
                "Ms. Gendron plays on a 1673 Jacob Stainer violin on generous loan from the Englewood "
                "Chamber Players.",
            ],
        },
        "note": "As supplied by the artist.",
    },
    {
        "slug": "matthew-cohen",
        "contact": ("cohenviola.com", "https://www.cohenviola.com"),
        "card": (
            "Ukrainian-American violist Matthew Cohen is a dynamic and versatile artist whose "
            "captivating performances have made him one of the most sought-after violists of his "
            "generation. He was a special prize winner at the prestigious Primrose International "
            "Viola Competition."),
        "anchor": "member-cohen",
        "name": "Matthew Cohen",
        "role": "Viola",
        "photo": "assets/img/matthew-cohen.jpg",
        "links": [("Website", "https://www.cohenviola.com"),
                  ("Instagram", "https://www.instagram.com/mcohenviola/")],
        "short": [],
        "long": [],
        # his own three, September 2026, marked not to be altered
        "versions": {
            "short": [
                "Matthew Cohen was a special prize winner at the Primrose International Viola "
                "Competition and has appeared as a soloist with orchestras such as the Gstaad "
                "Festival Orchestra, I Virtuosi Italiani, The Juilliard Orchestra, Symphony in C, the "
                "North Shore Symphony Orchestra, the Colburn Orchestra, and the Los Angeles Jewish "
                "Symphony for the world premiere of Garry Schyman&#x27;s viola concerto. Recent "
                "engagements include recitals in Memphis, Philadelphia, Washington D.C., New York, "
                "Chicago and Vancouver.",
            ],
            "medium": [
                "Ukrainian-American violist Matthew Cohen is a dynamic and versatile artist whose "
                "captivating performances have made him one of the most sought-after violists of his "
                "generation. He was a special prize winner at the prestigious Primrose International "
                "Viola Competition as well as garnering top prizes at the Citta di Cremona "
                "International Viola Competition, Vivo International Music Competition and the Art of "
                "Duo International Competition. Particularly interested in advocating for the viola "
                "as a unique voice, he has concertized as a soloist with orchestras such as the "
                "Gstaad Festival Orchestra, I Virtuosi Italiani, The Juilliard Orchestra, Symphony in "
                "C, the North Shore Symphony Orchestra, the Colburn Orchestra, the Oregon "
                "Sinfonietta, and gave the world premiere of Garry Schyman&#x27;s viola concerto "
                "&quot;Zingaro&quot; with the Los Angeles Jewish Symphony. Recent engagements include "
                "performances at Philadelphia Chamber Music Society, Taipei&#x27;s National Concert "
                "Hall and recitals in Philadelphia, Washington D.C., New York, Chicago and Vancouver. "
                "Upcoming projects include recording Mozart&#x27;s Sinfonia Concertante with the "
                "Edmonton Chamber Orchestra and a solo album on the Centaur label titled &quot;Viola "
                "Americana&quot; featuring works by American composers as well as composers who "
                "emigrated to America. A passionate chamber musician, Cohen is a member of the Li- "
                "Cohen Duo and is the co-founder and Artistic Director of Opus 71 Concerts, a "
                "multidisciplinary concert series near New York&#x27;s Lincoln Center.",
            ],
            "long": [
                "Ukrainian-American violist Matthew Cohen is a dynamic and versatile artist whose "
                "captivating performances have made him one of the most sought-after violists of his "
                "generation. He was a special prize winner at the prestigious Primrose International "
                "Viola Competition as well as garnering top prizes at the Citta di Cremona "
                "International Viola Competition in Italy, Vivo International Music Competition and "
                "the Art of Duo International Competition. Particularly interested in advocating for "
                "the viola as a unique voice, he is challenging the misconception that the viola has "
                "a limited repertoire by bringing attention to lesser-known gems as well as "
                "arrangements of other masterworks.",
                "Since his first performance in Carnegie Hall&#x27;s Stern Auditorium at the age of "
                "15 as a soloist in the New York premiere of Tomas Svoboda&#x27;s Sonata No. 2 for "
                "orchestra and solo string quartet, Cohen has concertized as a soloist with "
                "orchestras such as the Gstaad Festival Orchestra, I Virtuosi Italiani, the Juilliard "
                "Orchestra, Symphony in C, the North Shore Symphony Orchestra, the Colburn Orchestra, "
                "the Oregon Sinfonietta and gave the world premiere of internationally recognized "
                "video game score composer Garry Schyman&#x27;s viola concerto &quot;Zingaro&quot; "
                "with the Los Angeles Jewish Symphony. Recent engagements include performances at "
                "Philadelphia Chamber Music Society and Taipei&#x27;s National Concert Hall and "
                "recitals in Memphis, Philadelphia, Washington D.C., New York, Chicago and Vancouver. "
                "Upcoming projects include recording Mozart&#x27;s Sinfonia Concertante with the "
                "Edmonton Chamber Orchestra and a viola and piano album on the Centaur label titled "
                "&quot;Viola Americana&quot; featuring works by American composers as well as "
                "composers who emigrated to America.",
                "A passionate chamber musician, Cohen is a member of the Li-Cohen Duo and has "
                "performed alongside members of ensembles such as the Aeolus, Borromeo, Guarneri, "
                "Jasper, Orion, Parker, Tokyo, and Vermeer string quartets and the Beaux Arts, "
                "Horszowski and Tempest piano trios. He is on the artist roster of CreArtBox and New "
                "Asia Chamber Music Society in New York City and is the co-founder and Artistic "
                "Director of Opus 71 Concerts, a multidisciplinary concert series near New "
                "York&#x27;s Lincoln Center.",
                "As a graduate of the Juilliard School&#x27;s Master of Music program, he was the "
                "proud recipient of a Kovner Fellowship following studies at the Colburn Conservatory "
                "and Cleveland Institute of Music where his principal teachers included Misha Amory, "
                "Heidi Castleman, Paul Coletti, Jeffrey Irvine, and Cynthia Phelps.",
                "His recording of York Bowen&#x27;s <em>Phantasy</em> for viola and piano was "
                "released on the Soundset label. In addition to his musical activities, he enjoys "
                "public speaking and has acted in a number of plays including various works of "
                "Shakespeare, <em>Peter Pan</em>, <em>Auntie Mame</em>, and the musical <em>Bugsy "
                "Malone</em>.",
            ],
        },
        "note": "As supplied by the artist. Reproduced without alteration at his request.",
    },
    {
        "slug": "julia-yang",
        "contact": ("juliayangcello.com", "https://www.juliayangcello.com"),
        "card": (
            "Praised for &quot;her sense of joyful virtuosity&quot; as concerto soloist "
            "(<em>South Florida Classical Review</em>), Julia Yang is a courageous and soulful "
            "cellist, multi-faceted performer, and founding member of the Naumburg-winning "
            "Merz Trio and of the clarinet-cello-piano ensemble Trio Phōs."),
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

# How long "short" and "medium" are, counted in characters of plain text
# (tags and entities do not count). A version never cuts mid-sentence: it
# takes as many of the artist's own sentences as fit, and stops.
SHORT_CHARS = 500
MEDIUM_CHARS = 1500

# a full stop that ends a sentence, rather than one inside an abbreviation
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z&<\u201c\u0022(])")
ABBREV_RE = re.compile(
    r"\b(?:Ms|Mr|Mrs|Dr|Prof|St|No|Op|Vol|Jr|Sr|vs|etc|Inc|Mus|"
    r"[A-Z])\.\Z")


def plain_text(fragment):
    """The visible text, for measuring: no tags, entities resolved."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragment))


def sentences(paragraph):
    """Split a paragraph, keeping abbreviations whole."""
    parts = SENTENCE_RE.split(paragraph)
    out = []
    for part in parts:
        if out and ABBREV_RE.search(plain_text(out[-1]).strip()):
            out[-1] = out[-1] + " " + part
        else:
            out.append(part)
    return out


def trim(paragraphs, limit):
    """The opening of a biography, cut to a length, on a sentence break."""
    kept, used = [], 0
    for paragraph in paragraphs:
        taken = []
        for sentence in sentences(paragraph):
            length = len(plain_text(sentence))
            if taken or kept:
                length += 1        # the space or break before it
            if used + length > limit:
                break
            taken.append(sentence)
            used += length
        if taken:
            kept.append(" ".join(taken))
        if len(taken) != len(sentences(paragraph)):
            break
    # never return nothing: one sentence is better than an empty version
    if not kept and paragraphs:
        kept = [sentences(paragraphs[0])[0]]
    return kept


CARD_RE_TEMPLATE = r'(<article id="{anchor}".*?)(</article>)'
BIO_RE = re.compile(r'(<p class="body-l"[^>]*>)(.*?)(</p>)', re.S)
TAGS_RE = re.compile(r'\s*<ul style="list-style:none;padding:0;margin:18px 0 0;'
                     r'display:flex;flex-wrap:wrap;gap:18px;font-style:italic;'
                     r'color:var\(--ink-soft\)">.*?</ul>', re.S)
BUTTONS_RE = re.compile(r'(<div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">)(.*?)(</div>)', re.S)
FULL_BIO_RE = re.compile(r'\s*<a href="artists/[^"]+" class="btn btn-s btn-stamp">.*?</a>', re.S)
NAME_RE = re.compile(r'(<h3 class="member-name">)(.*?)(</h3>)', re.S)
# a card whose only button is a bare link, with no row around it
BARE_BTN_RE = re.compile(
    r'\s*<a href="([^"]*)" class="btn btn-s" style="margin-top:16px">(.*?)</a>', re.S)
EMPTY_ROW_RE = re.compile(
    r'\s*<div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">\s*</div>', re.S)
ROW_OPEN = '<div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">' 
NAME_LINK_RE = re.compile(r'(<h3 class="member-name">)<a href="artists/[^"]+">(.*?)</a>(?=</h3>)', re.S)


def versions(artist):
    """Short, medium and full, longest last so it is the one shown.

    An artist who writes their own three gets those, untouched. For
    everyone else the shorter two are the opening of the long one, cut at
    a sentence break.
    """
    if artist.get("versions"):
        v = artist["versions"]
        return [("short", v["short"]), ("medium", v["medium"]), ("full", v["long"])]
    if not artist["long"]:
        return [("full", artist["short"])]
    return [
        ("short", trim(artist["long"], SHORT_CHARS)),
        ("medium", trim(artist["long"], MEDIUM_CHARS)),
        ("full", artist["long"]),
    ]


LENGTH_LABEL = {"short": "Short", "medium": "Medium", "full": "Full"}


def page(artist):
    links = "".join(
        '<a class="btn" href="{url}" target="_blank" rel="noopener">{label} '
        '<span class="ar">&#8594;</span></a>'.format(label=label, url=url)
        for label, url in artist["links"])

    blocks, picks = [], []
    for name, paragraphs in versions(artist):
        chars = sum(len(plain_text(x)) for x in paragraphs)
        body = "\n".join("            <p>{}</p>".format(x) for x in paragraphs)
        blocks.append(
            '          <div class="bio-version" data-bio="{name}"{hide}>\n{body}\n'
            '          </div>'.format(
                name=name, body=body,
                hide="" if name == "full" else " hidden"))
        picks.append(
            '          <button type="button" data-bio-pick="{name}" '
            'aria-pressed="{on}">{label}<span>{chars} characters</span></button>'.format(
                name=name, label=LENGTH_LABEL[name], chars=chars,
                on="true" if name == "full" else "false"))

    switch = ""
    if len(picks) > 1:
        switch = ('        <div class="bio-switch" role="group" '
                  'aria-label="Length of biography">\n'
                  '          <span class="label">Biography</span>\n'
                  + "\n".join(picks) + "\n        </div>\n")

    label, url = artist["contact"]
    external = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
    note = (
        '          <p class="bio-note">These biographies are published as the artist '
        'wrote them and are not to be altered. For another version, or for a longer one, '
        'write to {name} directly: <a href="{url}"{ext}>{label}</a>.</p>'.format(
            name=html.escape(artist["name"].split()[0]), url=url, ext=external, label=label))
    bio = ('        <section class="artist-bio" data-bio-set>\n'
           + "\n".join(blocks) + "\n" + note + "\n        </section>")

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
<link rel="stylesheet" href="../assets/styles.css?v=126">
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
{bio}
      </div>
      <aside class="event-sidebar">
        <figure class="artist-portrait"><img src="../{photo}" alt="{name}, {role_plain}"></figure>
{switch}        <div class="artist-links">{links}
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

<script src="../assets/site.js?v=42"></script>
</body>
</html>
""".format(name=html.escape(artist["name"]), role=artist["role"],
           role_plain=artist["role"].split(" · ")[0].lower(),
           slug=artist["slug"], photo=artist["photo"], site=SITE,
           bio=bio, switch=switch, links=links)


def sync_card(src, artist):
    """The about page carries the short bio, and a way through to the rest."""
    card = re.search(CARD_RE_TEMPLATE.format(anchor=artist["anchor"]), src, re.S)
    if not card:
        print("  !! no card for", artist["name"])
        return src
    body = card.group(1)

    # a card is a card: one paragraph, not the whole short biography
    body = BIO_RE.sub(lambda m: m.group(1) + artist["card"] + m.group(3), body, count=1)
    # the name itself is the way through, not only the button below it
    body = NAME_LINK_RE.sub(r"\1\2", body)
    body = NAME_RE.sub(
        lambda m: '{}<a href="artists/{}.html">{}</a>{}'.format(
            m.group(1), artist["slug"], m.group(2), m.group(3)),
        body, count=1)
    # the list of affiliations under it goes
    body = TAGS_RE.sub("", body)

    link = ('<a href="artists/{}.html" class="btn btn-s btn-stamp">Full biography '
            '<span class="ar">&#8594;</span></a>'.format(artist["slug"]))

    # start from a card with none of our buttons in it, wherever a previous
    # run left one, so re-running cannot strand a row outside the column
    body = FULL_BIO_RE.sub("", body)
    body = EMPTY_ROW_RE.sub("", body)

    buttons = BUTTONS_RE.search(body)
    if buttons:
        body = body.replace(
            buttons.group(0),
            buttons.group(1) + link + buttons.group(2) + buttons.group(3), 1)
    else:
        # Laporta and Urraca carry one bare link instead of a row of them.
        # Adding a row after the text column dropped the button into the
        # article's grid as a third cell, on a line of its own; it goes in
        # a row with the link already there.
        bare = BARE_BTN_RE.search(body)
        if not bare:
            print("  !! nowhere to put the link on", artist["name"])
            return src.replace(card.group(0), body + card.group(2), 1)
        row = (ROW_OPEN + link
               + '<a href="{}" class="btn btn-s">{}</a>'.format(bare.group(1), bare.group(2))
               + "</div>")
        body = body.replace(bare.group(0), "\n        " + row, 1)
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
