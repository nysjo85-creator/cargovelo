#!/usr/bin/env python3
"""Builds the multi-page v2 from tools/v2_onepage.html (the one-page prototype used as a component library).
Run from the repo root:  python3 tools/build_v2.py
Every page gets its own title, description, breadcrumb and FAQ/Service markup, shared nav, footer and script."""
import re, os, json, posixpath, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, "tools", "v2_onepage.html"), encoding="utf-8").read()
V2 = os.path.join(ROOT, "v2")

# ---------------------------------------------------------------- source pieces
def section(id_):
    m = re.search(rf'<section[^>]*\bid="{id_}"', SRC)
    i = m.start()
    j = SRC.index("</section>", i) + len("</section>")
    return SRC[i:j]

STYLE = re.search(r"<style>.*?</style>", SRC, re.S).group(0)
STYLE = STYLE.replace(".nav .wrap{", ".nav>.wrap{")
JS_ALL = re.search(r"<script>\n\(function\(\)\{.*?\}\)\(\);\n</script>", SRC, re.S).group(0)

def chunk(a, b):
    i = JS_ALL.index(a); j = JS_ALL.index(b, i) if b else len(JS_ALL)
    return JS_ALL[i:j]

PRE = JS_ALL[: JS_ALL.index("// video:")]
J_VIDEO = chunk("// video:", "// reveal-once")
J_REVEAL = chunk("// reveal-once", "// ---- booking form")
J_FORM = chunk("// ---- booking form", "// mega menu")
J_MEGA = chunk("// mega menu", "// city explorer")
J_CITY = chunk("// city explorer", "// CTA buttons")
J_CTA = chunk("// CTA buttons", None).replace("})();\n</script>", "")

SEC = {k: section(k) for k in ["klanten", "oplossingen", "wie", "steden", "haast", "medisch", "biotech", "reviews", "duurzaam", "mensen", "boeken"]}
SEC["boeken"] = SEC["boeken"].replace("<li>Klantenservice: maandag tot vrijdag, 8u tot 17u</li>", '<li id="dispatch-status">Klantenservice: maandag tot vrijdag, 8u tot 17u</li>').replace("Je gegevens worden alleen gebruikt om je aanvraag te beantwoorden.", "Je gegevens worden alleen gebruikt om je aanvraag te beantwoorden. We noteren ook welke pagina's van deze site je bekeek, zodat we je beter kunnen helpen.")
MEER = section("meer")
k = MEER.index('<div class="sens"')
BENTO = MEER[:k] + "</div></section>"
SENS = '<section class="light" style="padding-top:72px;padding-bottom:72px"><div class="wrap">' + MEER[k:]
SEC_PROMISE = SRC[SRC.index('<section class="promise light">'):SRC.index("</section>", SRC.index('<section class="promise light">')) + 10]
SEC_TEAM_FORM = SEC["boeken"]

I = {}
for m in re.finditer(r'https://cargovelo\.be/content/uploads/yootheme/cache/[a-z0-9]+/([A-Za-z0-9_\-]+?)-[a-f0-9]{8}\.webp', SRC):
    I.setdefault(m.group(1), m.group(0))
EXTRA_IMG = {
    "Header-duurzaamheid": "https://cargovelo.be/content/uploads/yootheme/cache/80/Header-duurzaamheid-80336ffa.webp",
    "DRIESLUYTEN": "https://cargovelo.be/content/uploads/yootheme/cache/c1/CARGOVELO_DRIESLUYTEN-6-scaled-c1add074.webp",
    "femalecare-76": "https://cargovelo.be/content/uploads/yootheme/cache/17/Kopie-van-2024-11-28-CargoVelo_BXL_femalecare-76-scaled-1799f7ad.webp",
}
def img(name):
    for key, v in I.items():
        if name in key: return v
    return EXTRA_IMG[name]
IMG = dict(
    doorstep=img("Header-winkels"), health=img("Header-health"), lab=img("femalecare-44"), samples=img("femalecare-54"),
    handoff=img("femalecare-72"), street=img("DSC_9253"), ramp=img("Header-bezorgdiensten"), bxl=img("Header-duurzaamheid"),
    flowers=img("CargoVelo-135"), bridge=img("141-1"), p14=img("portretten-14"), p42=img("portretten-42"), p23=img("portretten-23"),
    team=img("DRIESLUYTEN"), fc76=img("femalecare-76"), poster="__POSTER__",
)

# ---------------------------------------------------------------- pages
PAGES = [
 ("", "Home"),
 ("webshops-en-retail", "Webshops en retail"),
 ("haast", "Haast"),
 ("medische-stalen", "Medische stalen"),
 ("dna-en-biotech", "DNA en biotech"),
 ("gevoelige-leveringen", "Gevoelige leveringen"),
 ("vaste-rondes-en-bevoorrading", "Vaste rondes en bevoorrading"),
 ("logistieke-partners", "Logistieke partners"),
 ("steden", "Gent, Antwerpen en Brussel"),
 ("steden/gent", "Gent"),
 ("steden/antwerpen", "Antwerpen"),
 ("steden/brussel", "Brussel"),
 ("klanten", "Klanten en reviews"),
 ("duurzaamheid", "Duurzaamheid"),
 ("over-ons", "Over ons"),
 ("contact", "Plan je levering"),
]
TITLE = dict(PAGES)
ANCHOR_PAGE = {
 "oplossingen": "webshops-en-retail", "wie": "webshops-en-retail", "steden": "steden", "haast": "haast", "medisch": "medische-stalen",
 "biotech": "dna-en-biotech", "meer": "vaste-rondes-en-bevoorrading", "gevoelig": "gevoelige-leveringen", "duurzaam": "duurzaamheid",
 "reviews": "klanten", "klanten": "klanten", "mensen": "over-ons", "boeken": "contact",
}
SERVICE_ID = {"haast": "haast", "medisch": "medisch", "biotech": "biotech", "pakketten": "pakketten", "andere": "andere"}

def url(frm, to):
    a = posixpath.dirname(frm + "/x") if frm else "."
    depth = 0 if not frm else frm.count("/") + 1
    prefix = "../" * depth
    return (prefix + to + "/") if to else (prefix or "./")

ORG = {"@type": "LocalBusiness", "@id": "https://cargovelo.be/#org", "name": "Cargo Velo", "url": "https://cargovelo.be/", "telephone": "+32479336899",
       "email": "info@cargovelo.be",
       "address": {"@type": "PostalAddress", "streetAddress": "Zwijnaardsesteenweg 227", "addressLocality": "Gent", "addressCountry": "BE"},
       "areaServed": [{"@type": "City", "name": "Gent"}, {"@type": "City", "name": "Antwerpen"}, {"@type": "City", "name": "Brussel"}],
       "openingHours": "Mo-Fr 08:00-17:00"}

FAQ = {
 "steden": ("In welke steden leveren jullie?", "In Gent, Antwerpen en Brussel, dwars door de stad en tot in de rand eromheen. Tussen de steden rijdt onze shuttle."),
 "intercity": ("Kan ik een zending van Gent naar Brussel of Antwerpen laten brengen?", "Ja. Onze shuttle verbindt de drie steden: je zending reist van stad naar stad en wordt daar door een fietskoerier afgeleverd."),
 "buiten": ("Leveren jullie ook buiten de steden?", "Onze kern is de stad en de rand eromheen. Heb je een zending daarbuiten? Vraag het ons, dan kijken we wat mogelijk is."),
 "haast": ("Wat als het snel moet?", "Bel of boek en je spreekt met ons dispatchteam. Samen zoeken we de snelste oplossing voor jouw zending. Je bereikt ons op 0479 33 68 99."),
 "vandaag": ("Kan ik vandaag nog iets laten bezorgen?", "Neem contact op met ons dispatchteam. Samen zoeken we de snelste oplossing voor jouw zending."),
 "medisch": ("Kunnen jullie medische stalen vervoeren?", "Ja. Al sinds 2015 vervoeren we biologische stalen op kamertemperatuur, gekoeld of ingevroren, in lijn met Europese richtlijnen van FAGG, FAVV, ADR en GDP."),
 "bio": ("Werken jullie voor biotechbedrijven en sequencing-labs?", "Ja. We halen monsters op, bundelen ze in onze hub en zorgen dat ze klaar zijn voor de internationale verzending."),
 "klant": ("Moet ik klant worden om één levering te boeken?", "Verzend je meer dan 100 pakketten per week? Dan is een contract voordeliger, met scherpe tariefformules en extra opties. Voor een enkele levering vraag je een offerte aan."),
 "bewijs": ("Krijg ik een bewijs van levering?", "Ja. Je krijgt track & trace en een duidelijk bezorgbewijs voor elke levering."),
 "klantenservice": ("Wanneer is de klantenservice bereikbaar?", "Van maandag tot vrijdag tussen 8u en 17u, op 0479 33 68 99 of via info@cargovelo.be."),
 "uitstoot": ("Hoe duurzaam zijn jullie leveringen?", "Alle leveringen gebeuren zonder CO₂-uitstoot, met fietskoeriers en cargofietsen. Je krijgt inzicht in je CO₂-besparing voor je duurzaamheidsrapportage."),
 "gevoelig": ("Kunnen jullie vertrouwelijke of waardevolle zendingen vervoeren?", "Ja. Dossiers, binnenpost, kwetsbare en waardevolle zendingen worden persoonlijk en volgens het afgesproken protocol afgegeven, met bezorgbewijs en een vast aanspreekpunt."),
 "partner": ("Kunnen jullie als partner de first en last mile voor ons doen?", "Ja. Wij ondersteunen logistieke partners bij de first en last mile in de stad, met een vaste aanspreekpersoon en een koppeling met ons verzendsysteem."),
 "ronde": ("Kunnen jullie een vaste ronde rijden?", "Ja. We rijden vaste rondes op vaste momenten, bijvoorbeeld wekelijks naar kantoren of tweemaal per dag langs praktijken."),
}

PAGE_META = {
 "": ("Cargo Velo: sneller, slimmer en schoner. Fietskoeriers die je ontzorgen", "Cargo Velo ontzorgt bedrijven en zorginstellingen met emissievrije fietsleveringen in Gent, Antwerpen en Brussel: pakketten, dringende zendingen, medische stalen en DNA-transport.", []),
 "webshops-en-retail": ("Webshops en retail: thuisbezorging en retours per fiets | Cargo Velo", "Thuisbezorging, retours en ship-from-store per fiets in Gent, Antwerpen en Brussel. Je klanten blij, jij ontzorgd.", ["steden", "klant", "bewijs", "vandaag"]),
 "haast": ("Haast? Dringende zendingen per fiets in Gent, Antwerpen en Brussel | Cargo Velo", "Moet iets snel? Ons dispatchteam zoekt samen met jou de snelste oplossing, met fietskoeriers in Gent, Antwerpen en Brussel.", ["haast", "vandaag", "intercity", "bewijs"]),
 "medische-stalen": ("Medische stalen vervoeren in Gent, Antwerpen en Brussel | Cargo Velo", "Zorgvuldig vervoer van medische stalen op kamertemperatuur, gekoeld of ingevroren. Vaste rondes en vaste koeriers, sinds 2015.", ["medisch", "bewijs", "ronde", "steden"]),
 "dna-en-biotech": ("DNA- en biotechtransport: van dropbox tot sequencer | Cargo Velo", "Wij halen DNA- en biotechstalen op bij labs en dropboxes, bundelen ze in onze hub en maken ze klaar voor internationale verzending.", ["bio", "medisch", "intercity", "bewijs"]),
 "gevoelige-leveringen": ("Gevoelige leveringen: vertrouwelijk, waardevol en kwetsbaar | Cargo Velo", "Vertrouwelijke stukken, waardevolle en kwetsbare zendingen, stalen en aanbestedingen: met vertrouwen vervoerd door vaste fietskoeriers.", ["gevoelig", "bewijs", "medisch", "klantenservice"]),
 "vaste-rondes-en-bevoorrading": ("Vaste rondes en bevoorrading per fiets | Cargo Velo", "Vaste rondes, bevoorrading van filialen en horeca, bloemen en food, bedrijfsafval en zware ladingen per cargofiets in Gent, Antwerpen en Brussel.", ["ronde", "steden", "klant", "uitstoot"]),
 "logistieke-partners": ("Logistieke partners: first en last mile per fiets | Cargo Velo", "Cargo Velo ondersteunt logistieke partners bij de first en last mile in Gent, Antwerpen en Brussel, met hubs aan de stadsrand.", ["partner", "steden", "intercity", "uitstoot"]),
 "steden": ("Fietskoerier in Gent, Antwerpen en Brussel | Cargo Velo", "Drie steden, één netwerk: Cargo Velo levert in Gent, Antwerpen en Brussel, tot in de rand eromheen, en verbindt de steden met een shuttle.", ["steden", "intercity", "buiten", "haast"]),
 "steden/gent": ("Fietskoerier in Gent | Cargo Velo", "Fietskoerier in Gent en omgeving: pakketten, medische stalen, DNA-transport en dringende zendingen, zonder uitstoot.", ["steden", "intercity", "vandaag", "medisch"]),
 "steden/antwerpen": ("Fietskoerier in Antwerpen | Cargo Velo", "Fietskoerier in Antwerpen en omgeving: pakketten, catering, last mile en dringende zendingen, zonder uitstoot.", ["steden", "intercity", "vandaag", "partner"]),
 "steden/brussel": ("Fietskoerier in Brussel | Cargo Velo", "Fietskoerier in Brussel en omgeving: vaste labrondes, pakketten, filialen en dringende zendingen, zonder uitstoot.", ["steden", "intercity", "vandaag", "medisch"]),
 "klanten": ("Klanten en reviews | Cargo Velo", "Meer dan 1000 bedrijven, winkels en zorginstellingen laten zich door Cargo Velo ontzorgen. Lees wat klanten zeggen.", ["bewijs", "klant"]),
 "duurzaamheid": ("Duurzame stadslogistiek zonder uitstoot | Cargo Velo", "Verduurzaam moeiteloos: emissievrije leveringen en inzicht in je CO₂-besparing voor je duurzaamheidsrapportage.", ["uitstoot", "steden"]),
 "over-ons": ("Over Cargo Velo en De Fietskoerier | Cargo Velo", "Cargo Velo en De Fietskoerier zijn samen het grootste fietskoeriersbedrijf van België: vaste koeriers die je stad kennen.", ["steden", "klantenservice"]),
 "contact": ("Plan je levering | Cargo Velo", "Zeg wat je kwijt wil, wij ontzorgen de rest. Vraag een levering of offerte aan voor Gent, Antwerpen of Brussel.", ["klant", "haast", "steden", "klantenservice"]),
}

SERVICES = {  # service JSON-LD
 "haast": "Dringende zendingen per fiets", "medische-stalen": "Transport van medische stalen", "dna-en-biotech": "DNA- en biotechtransport",
 "gevoelige-leveringen": "Gevoelige leveringen", "vaste-rondes-en-bevoorrading": "Vaste rondes en bevoorrading", "webshops-en-retail": "Thuisbezorging en retours",
 "logistieke-partners": "First en last mile voor logistieke partners",
}

# ---------------------------------------------------------------- shared components
def nav(slug):
    u = lambda to: url(slug, to)
    return f"""<nav class="nav" id="nav"><div class="wrap">
  <a href="{u('')}" aria-label="Cargo Velo, naar de homepage"><img class="logo" src="https://cargovelo.be/content/uploads/yootheme/cache/5b/Cargo-Velo_5_Horizontal_wit-5bf2c61f.webp" alt="Cargo Velo"></a>
  <div class="links">
    <button class="mt" id="mt" type="button" aria-expanded="false" aria-controls="mega">Bedrijfsoplossingen <svg viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    <a href="{u('steden')}">Steden</a><a href="{u('klanten')}">Klanten</a><a href="{u('duurzaamheid')}">Duurzaamheid</a><a href="{u('over-ons')}">Over ons</a>
  </div>
  <div class="right"><a class="tel" href="tel:+32479336899" data-track="bel">0479 33 68 99</a><a class="btn btn-green" href="{u('contact')}" data-track="cta-nav">Plan je levering</a><button class="burger" id="burger" type="button" aria-expanded="false" aria-controls="mega">Menu</button></div>
</div>
<div class="mega" id="mega" hidden><div class="wrap">
  <div><h4>Wat kunnen we voor je doen?</h4>
    <ul class="cols2">
      <li><a class="it" href="{u('webshops-en-retail')}"><b>Home en Returns</b><span>Thuisbezorging en ophaling aan de voordeur</span></a></li>
      <li><a class="it hot" href="{u('haast')}"><b>Haast?</b><span>Ons dispatchteam denkt mee</span></a></li>
      <li><a class="it" href="{u('medische-stalen')}"><b>Medische stalen</b><span>Gekoeld, hygiënisch, op tijd</span></a></li>
      <li><a class="it" href="{u('dna-en-biotech')}"><b>DNA en biotech</b><span>Van dropbox tot sequencer</span></a></li>
      <li><a class="it" href="{u('gevoelige-leveringen')}"><b>Gevoelige leveringen</b><span>Met discretie en vertrouwen</span></a></li>
      <li><a class="it" href="{u('vaste-rondes-en-bevoorrading')}"><b>Vaste rondes en bevoorrading</b><span>Filialen, horeca, kantoren</span></a></li>
    </ul></div>
  <div><h4>Voor wie?</h4>
    <ul>
      <li><a class="it" href="{u('webshops-en-retail')}"><b>Webshops en retail</b></a></li>
      <li><a class="it" href="{u('medische-stalen')}"><b>Zorg en labo's</b></a></li>
      <li><a class="it" href="{u('dna-en-biotech')}"><b>Biotech en onderzoek</b></a></li>
      <li><a class="it" href="{u('vaste-rondes-en-bevoorrading')}"><b>Horeca, bloemen en food</b></a></li>
      <li><a class="it" href="{u('logistieke-partners')}"><b>Logistieke partners</b></a></li>
    </ul></div>
  <a class="feat" href="{u('contact')}" data-track="cta-mega"><img src="{IMG['doorstep']}" alt="" loading="lazy"><div><b>Zeg wat je kwijt wil. Wij ontzorgen de rest.</b><span class="btn btn-green">Plan je levering</span></div></a>
  <div class="mob"><a href="{u('steden')}">Steden</a><a href="{u('klanten')}">Klanten</a><a href="{u('duurzaamheid')}">Duurzaamheid</a><a href="{u('over-ons')}">Over ons</a></div>
</div></div>
</nav>"""

def footer(slug):
    u = lambda to: url(slug, to)
    v1 = ("../" * (0 if not slug else slug.count("/") + 1)) + "../v1/nl/"
    return f"""<footer><div class="wrap">
  <div class="cols">
    <div><img src="https://cargovelo.be/content/uploads/yootheme/cache/5b/Cargo-Velo_5_Horizontal_wit-5bf2c61f.webp" alt="Cargo Velo"><p style="margin-top:14px;max-width:260px">Gezwind door 3 steden: Gent, Antwerpen en Brussel.</p></div>
    <div><h4>Oplossingen</h4><ul><li><a href="{u('webshops-en-retail')}">Webshops en retail</a></li><li><a href="{u('haast')}">Haast?</a></li><li><a href="{u('medische-stalen')}">Medische stalen</a></li><li><a href="{u('dna-en-biotech')}">DNA en biotech</a></li><li><a href="{u('gevoelige-leveringen')}">Gevoelige leveringen</a></li><li><a href="{u('vaste-rondes-en-bevoorrading')}">Vaste rondes</a></li><li><a href="{u('logistieke-partners')}">Logistieke partners</a></li></ul></div>
    <div><h4>Steden</h4><ul><li><a href="{u('steden/gent')}">Gent</a></li><li><a href="{u('steden/antwerpen')}">Antwerpen</a></li><li><a href="{u('steden/brussel')}">Brussel</a></li><li><a href="{u('steden')}">Het netwerk</a></li></ul></div>
    <div><h4>Cargo Velo</h4><ul><li><a href="{u('klanten')}">Klanten en reviews</a></li><li><a href="{u('duurzaamheid')}">Duurzaamheid</a></li><li><a href="{u('over-ons')}">Over ons</a></li><li><a href="{u('contact')}">Plan je levering</a></li><li>0479 33 68 99</li><li>info@cargovelo.be</li></ul></div>
  </div>
  <div class="legal"><span>Prototype v2: geen officiële Cargo Velo-website. Beelden en klantgegevens komen van cargovelo.be.</span><span><a href="{v1}privacy-policy/">Privacy</a> &nbsp; <a href="{v1}voorwaarden/">Voorwaarden</a> &nbsp; <a href="{'../' * (0 if not slug else slug.count('/') + 1)}strategie/">Strategie (intern)</a></span></div>
</div></footer>"""

def faq_html(keys):
    if not keys: return ""
    items = "".join(f"<details><summary>{html.escape(FAQ[k][0])}</summary><p>{html.escape(FAQ[k][1])}</p></details>" for k in keys)
    return f'<section class="light"><div class="wrap faqwrap"><div class="head" style="margin:0"><h2>Goed om te weten.</h2></div><div>{items}</div></div></section>'

def ctaband(slug, text, service=None, label="Plan je levering"):
    href = url(slug, "contact") + (f"?dienst={service}" if service else "")
    return f'<section class="dark ctaband"><div class="wrap"><h2>{text}</h2><a class="btn btn-green" href="{href}" data-track="cta-band">{label}</a></div></section>'

def crumbs(slug):
    parts = [("Home", url(slug, ""))]
    if "/" in slug:
        parts.append(("Steden", url(slug, "steden")))
    parts.append((TITLE[slug], None))
    return '<nav class="crumbs" aria-label="Kruimelpad">' + " / ".join(f'<a href="{h}">{html.escape(t)}</a>' if h else f"<span>{html.escape(t)}</span>" for t, h in parts) + "</nav>"

def pagehead(slug, h1, lead, image=None, cta=("Plan je levering", None)):
    href = url(slug, "contact") + (f"?dienst={cta[1]}" if cta[1] else "")
    right = f'<div class="ph-img"><img src="{image}" alt="" loading="eager"></div>' if image else ""
    cls = "pagehead dark" + (" has-img" if image else "")
    return f'<header class="{cls}"><div class="wrap">{crumbs(slug)}<div class="ph-grid"><div><h1>{h1}</h1><p class="lead">{lead}</p><div class="row"><a class="btn btn-green" href="{href}" data-track="cta-head">{cta[0]}</a></div></div>{right}</div></div></header>'

def jsonld(slug, faq_keys):
    graph = [ORG]
    title = TITLE[slug]
    crumb = [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://cargovelo.be/"}]
    if slug:
        pos = 2
        if "/" in slug:
            crumb.append({"@type": "ListItem", "position": 2, "name": "Steden", "item": "https://cargovelo.be/steden/"}); pos = 3
        crumb.append({"@type": "ListItem", "position": pos, "name": title})
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumb})
    if slug in SERVICES:
        graph.append({"@type": "Service", "name": SERVICES[slug], "provider": {"@id": "https://cargovelo.be/#org"},
                      "areaServed": ORG["areaServed"], "description": PAGE_META[slug][1]})
    if faq_keys:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": FAQ[k][0], "acceptedAnswer": {"@type": "Answer", "text": FAQ[k][1]}} for k in faq_keys]})
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>"

def fix_links(body, slug):
    ids_here = set(re.findall(r'\bid="([^"]+)"', body))
    def anchor(m):
        a = m.group(1)
        if a in ids_here: return m.group(0)
        if a == "boeken":
            return f'href="{url(slug, "contact")}"'
        if a in ANCHOR_PAGE:
            return f'href="{url(slug, ANCHOR_PAGE[a])}"'
        return m.group(0)
    body = re.sub(r'href="#([a-z\-]+)"', anchor, body)
    # CTA data-service links -> contact page with preselected service
    def svc(m):
        tag = m.group(0)
        sv = re.search(r'data-service="([a-z]+)"', tag).group(1)
        if slug == "" or slug == "contact":
            return tag
        tag = re.sub(r'href="[^"]*"', f'href="{url(slug, "contact")}?dienst={SERVICE_ID.get(sv, sv)}"', tag, count=1)
        if "data-track" not in tag:
            tag = tag[:-1] + f' data-track="cta-{sv}">'
        return tag
    body = re.sub(r'<a [^>]*data-service="[a-z]+"[^>]*>', svc, body)
    # v1 relative links: v2 sections used ../v1/ from /v2/
    depth = 0 if not slug else slug.count("/") + 1
    body = body.replace('href="../v1/', 'href="' + "../" * (depth + 1) + 'v1/').replace('src="img/', 'src="' + "../" * depth + 'img/')
    body = body.replace("__POSTER__", ("../" * depth) + "img/hero-poster.jpg")
    return body

SCRIPT_TAIL = r"""
// ---- who clicks what: page trail + CTA source, shared with the request form ----
try{var tr=JSON.parse(sessionStorage.getItem('cvTrail')||'[]');tr.push({p:location.pathname.replace(/^.*\/v2\//,'v2/'),t:new Date().toISOString().slice(11,19)});sessionStorage.setItem('cvTrail',JSON.stringify(tr.slice(-12)))}catch(e){}
document.addEventListener('click',function(e){var a=e.target.closest('[data-track]');if(!a)return;try{sessionStorage.setItem('cvLastCta',a.dataset.track+' @ '+location.pathname.replace(/^.*\/v2\//,'v2/'))}catch(x){}
 window.dispatchEvent(new CustomEvent('cv:track',{detail:{cta:a.dataset.track,page:location.pathname}}))});
"""

def script(slug, has_form, has_city, has_hero):
    parts = [PRE]
    if has_hero: parts.append(J_VIDEO)
    parts.append(J_REVEAL)
    if has_form:
        form = J_FORM + J_CTA
        form = form.replace("Bron:location.href", "Bron:location.href,Via_pagina:(sessionStorage.getItem('cvLastCta')||'direct'),Bekeken_paginas:(function(){try{return JSON.parse(sessionStorage.getItem('cvTrail')||'[]').map(function(x){return x.p}).join(' > ')}catch(e){return ''}})()")
        form += "\nvar qd=new URLSearchParams(location.search).get('dienst');if(qd&&map[qd]){var rr=document.getElementById(map[qd]);if(rr){rr.checked=true;show(2,false)}}\n"
        parts.append("if(document.getElementById('form')){\n" + form + "\n}\n")
    parts.append(J_MEGA + "window.addEventListener('scroll',function(){if(!mg.hidden&&matchMedia('(min-width:1001px)').matches)mega(false)},{passive:true});\n")
    if has_city: parts.append("if(document.getElementById('cpanel')){\n" + J_CITY + "\n}\n")
    parts.append(J_BTN)
    parts.append(SCRIPT_TAIL)
    parts.append("})();\n</script>")
    return "".join(parts)

# ---------------------------------------------------------------- page bodies
def city_page(slug):
    c = slug.split("/")[1]
    D = {
     "gent": dict(name="Gent", img=IMG["bridge"], lead="Onze thuishaven, met ons adres in Zwijnaarde. Van de binnenstad tot de rand van Gent rijden onze koeriers pakketten, stalen en dringende zendingen rond, zonder uitstoot.",
        proof=[("AZ Sint-Lucas", "Sinds 2015 vervoeren we medische stalen voor de afdelingen van het Gentse ziekenhuis, gekoeld, ingevroren of op kamertemperatuur."), ("Nespresso, Krëfel en Blommm", "Dagelijkse bestellingen vanuit de winkels, nachtelijke bestellingen tot 22:00 voor Krëfel en wekelijkse boeketten voor bedrijven en particulieren."), ("DNA en biotech", "Wij zitten in Gent, vlak bij de biotechcluster van Zwijnaarde.")],
        links=[("haast", "Haast in Gent?", "Ons dispatchteam denkt mee."), ("medische-stalen", "Medische stalen in Gent", "Vaste koeriers en rondes."), ("dna-en-biotech", "DNA en biotech", "Van dropbox tot sequencer."), ("webshops-en-retail", "Webshops en retail", "Thuisbezorging en retours.")],
        faq=["steden", "intercity", "vandaag", "medisch"], to=("Antwerpen", "Brussel")),
     "antwerpen": dict(name="Antwerpen", img=IMG["team"], lead="In Antwerpen fuseerden we met De Fietskoerier. Samen leveren we pakketten, catering en zendingen voor logistieke partners tot aan de Antwerpse voordeur, zonder uitstoot.",
        proof=[("De Fietskoerier en Cargo Velo", "Samen het grootste fietskoeriersbedrijf van België, met vaste koeriers die de stad kennen."), ("Cadix", "Bedrijfslunches en catering: een combinatie van vaste ritten en last-minute bestellingen, dagelijks tientallen klanten in Antwerpen."), ("Nespresso en logistieke partners", "Dagelijkse leveringen vanuit de winkel en first en last mile voor partners.")],
        links=[("webshops-en-retail", "Webshops en retail", "Thuisbezorging en retours."), ("vaste-rondes-en-bevoorrading", "Vaste rondes en catering", "Dezelfde route, op tijd."), ("logistieke-partners", "Logistieke partners", "First en last mile."), ("haast", "Haast in Antwerpen?", "Ons dispatchteam denkt mee.")],
        faq=["steden", "intercity", "vandaag", "partner"], to=("Gent", "Brussel")),
     "brussel": dict(name="Brussel", img=IMG["fc76"], lead="In de Brusselse vijfhoek en de rand erom heen kennen onze koeriers elke straat. Van vaste labrondes tot filialen en dringende zendingen, zonder uitstoot.",
        proof=[("AZORG", "Tweemaal per dag een vaste ronde langs Brusselse praktijken, en 's avonds een shuttle vanaf de stadsrand naar Aalst."), ("COCOF", "Professionele en stipte rondes van en naar kabinetten, met bezorgbewijs tot op het juiste verdiep."), ("Proximus en BRAL", "Bevoorrading van filialen vanuit onze hubs, en tweewekelijkse controle van luchtmeetpunten.")],
        links=[("medische-stalen", "Medische stalen in Brussel", "Vaste rondes met bezorgbewijs."), ("gevoelige-leveringen", "Gevoelige leveringen", "Met discretie en vertrouwen."), ("vaste-rondes-en-bevoorrading", "Filialen en vaste rondes", "Op tijd en gebundeld."), ("haast", "Haast in Brussel?", "Ons dispatchteam denkt mee.")],
        faq=["steden", "intercity", "vandaag", "medisch"], to=("Gent", "Antwerpen")),
    }[c]
    cards = "".join(f'<a class="sc" href="{url(slug, s)}" data-track="stad-{c}-{s}"><div><h4>{t}</h4><p>{d}</p></div></a>' for s, t, d in D["links"])
    proof = "".join(f'<div class="facts-i"><b>{t}</b><span>{d}</span></div>' for t, d in D["proof"])
    shuttle = f'<section class="paper light"><div class="wrap two-col"><div><h2>{D["name"]} is verbonden met {D["to"][0]} en {D["to"][1]}.</h2><p class="big">Tussen de drie steden rijdt onze shuttle. Een zending van {D["name"]} naar {D["to"][0]} of {D["to"][1]} reist mee en wordt daar door een fietskoerier afgeleverd. Zit je net buiten de stad? Vraag het ons, we kijken graag wat mogelijk is.</p><a class="btn btn-black" href="{url(slug, "steden")}">Bekijk het netwerk</a></div><div class="facts-col">{proof}</div></div></section>'
    body = pagehead(slug, f"Fietskoerier in {D['name']}", D["lead"], image=D["img"]) + \
        f'<section class="light"><div class="wrap"><div class="head"><h2>Wat we in {D["name"]} voor je doen.</h2></div><div class="sgrid sgrid-links">{cards}</div></div></section>' + shuttle
    return body, D["faq"]

BODIES = {}
BODIES[""] = (lambda: None)  # built below

def hero_home():
    return f"""<header class="hero">
  <img class="poster" src="{IMG['poster']}" alt="">
  <video id="hv" autoplay muted loop playsinline poster="{IMG['poster']}" aria-hidden="true"><source src="https://cargovelo.be/content/uploads/2025/03/CARGO-VELO-Video-snippet.mp4" type="video/mp4"></video>
  <div class="wrap">
    <h1><i><b>Sneller,</b></i><i><b>slimmer</b></i><i><b>en schoner.</b></i></h1>
    <p class="lead">Cargo Velo ontzorgt bedrijven en zorginstellingen met emissievrije fietsleveringen in Gent, Antwerpen en Brussel, en daartussen.</p>
    <div class="row"><a class="btn btn-green" href="#boeken" data-track="cta-hero">Plan je levering</a><a class="btn btn-line" href="#haast-teaser">Haast? Praat met onze dispatch</a></div>
  </div>
  <button class="vctl" id="vc" type="button" aria-label="Pauzeer de video"><svg viewBox="0 0 16 16" aria-hidden="true"><path id="vcicon" d="M3 2h3.5v12H3zM9.5 2H13v12H9.5z"/></svg></button>
</header>"""

def spotlight():
    def t(slug, name, text, imgk, cls=""):
        return f'<a class="wt {cls}" href="{url("", slug)}" data-track="home-{slug}"><img src="{IMG[imgk]}" alt="" loading="lazy"><div><b>{name}</b><span>{text}</span></div></a>'
    return f'''<section id="haast-teaser" class="light"><div class="wrap"><div class="head"><h2>Waar we het verschil maken.</h2><p>Naast pakketten rijden onze koeriers ook wat niet mag falen. Elk onderwerp heeft zijn eigen pagina.</p></div><div class="wgrid">
{t("haast", "Haast?", "Ons dispatchteam zoekt met jou de snelste oplossing.", "street", "w3")}
{t("medische-stalen", "Medische stalen", "Gekoeld, hygiënisch en op het afgesproken moment.", "health", "w3")}
{t("dna-en-biotech", "DNA en biotech", "Van dropbox tot sequencer.", "lab")}
{t("gevoelige-leveringen", "Gevoelige leveringen", "Met discretie en vertrouwen.", "handoff")}
{t("vaste-rondes-en-bevoorrading", "Vaste rondes", "Dezelfde route, elke dag of week.", "flowers")}
</div></div></section>'''

def home_body():
    wie = SEC["wie"]
    return hero_home() + SEC["klanten"] + "\n" + SEC_PROMISE + "\n" + SEC["oplossingen"] + "\n" + spotlight() + "\n" + SEC["steden"] + "\n" + SEC["reviews"] + "\n" + SEC["boeken"], ["steden", "haast", "klant", "bewijs"]

def webshops_body():
    cards = SEC["oplossingen"]
    body = pagehead("webshops-en-retail", "Je klanten blij, jij ontzorgd.", "Thuisbezorging met een glimlach, retours aan de voordeur en verzenden vanuit je winkel of via een hub aan de stadsrand. Direct tot in de handen van je klant.", image=IMG["doorstep"], cta=("Plan je levering", "pakketten"))
    ship = f"""<section class="light"><div class="wrap"><div class="head"><h2>Zo ontzorgen we je winkel.</h2></div><div class="sgrid sgrid3">
<div class="sc"><h4>Ship-from-store</h4><p>Verzend rechtstreeks vanuit je winkel tot in de handen van je klanten, vandaag, morgen of wanneer jouw klant het verkiest.</p><small>Nespresso verzendt dagelijks vanuit haar winkels in Gent, Brussel en Antwerpen.</small></div>
<div class="sc g"><h4>Ship-from-hub</h4><p>Verzend vanuit je magazijn naar onze hubs aan de stadsrand, en van daar duurzaam naar de voordeur.</p><small>Krëfel: bestellen tot 22:00, de volgende dag bij de klant.</small></div>
<div class="sc"><h4>Track en trace</h4><p>Met realtime inzicht in je pakketstatus en digitale communicatie naar je klant, en één vast aanspreekpunt voor jou.</p><small>99% bij de eerste poging bezorgd.</small></div>
</div></div></section>"""
    return body + SEC["oplossingen"].replace('<section id="oplossingen" class="paper light">', '<section id="oplossingen" class="paper light">') + ship + SEC["reviews"] + ctaband("webshops-en-retail", "Je klanten blij en jij ontzorgd. Zeg ons wat je verzendt.", "pakketten"), ["steden", "klant", "bewijs", "vandaag"]

def simple(slug, h1, lead, image, blocks, cta_text, svc=None, cta_label="Plan je levering"):
    return pagehead(slug, h1, lead, image=image, cta=(cta_label, svc)) + "".join(blocks) + ctaband(slug, cta_text, svc, cta_label)

def promote_h1(block):
    return block.replace("<h2>", "<h1>", 1).replace("</h2>", "</h1>", 1)

def build_body(slug):
    if slug == "": return home_body()
    if slug == "webshops-en-retail": return webshops_body()
    if slug.startswith("steden/"): return city_page(slug)
    meta_faq = PAGE_META[slug][2]
    if slug == "haast":
        return promote_h1(SEC["haast"]).replace('<div class="wrap grid">', '<div class="wrap grid"><nav class="crumbs-in" style="display:none"></nav>', 1).replace("<h1>", "<h1>", 1) + ctaband(slug, "Haast? Spreek met ons dispatchteam.", "haast", "Vraag de dispatch"), meta_faq
    if slug == "medische-stalen":
        how = """<section class="paper light"><div class="wrap"><div class="head"><h2>Zo werkt geconditioneerd transport met Cargo Velo.</h2></div><div class="sgrid sgrid3">
<div class="sc"><h4>Correcte behandeling</h4><p>Zorgvuldige temperatuurcontrole en verpakking, een helder bezorgbewijs en het proactief informeren van de ontvanger.</p></div>
<div class="sc g"><h4>Continue aandacht</h4><p>We monitoren het ophalen en de voortgang nauwgezet. Doet zich een probleem voor? We grijpen meteen in en brengen tot op de juiste afdeling.</p></div>
<div class="sc"><h4>Voor alle type zendingen</h4><p>Labostalen, verse voeding, bloemen, elektronica. Losse pakjes, colli of grote dagelijkse volumes.</p></div>
</div></div></section>"""
        return promote_h1(SEC["medisch"]) + how + ctaband(slug, "Medische stalen? Laat ons meedenken.", "medisch", "Bespreek medische stalen"), meta_faq
    if slug == "dna-en-biotech":
        return promote_h1(SEC["biotech"]) + ctaband(slug, "Biotech-logistiek bespreken? Praat met ons.", "biotech", "Praat met ons"), meta_faq
    if slug == "gevoelige-leveringen":
        return pagehead(slug, "Gevoelige leveringen, met vertrouwen.", "Sommige zendingen mogen je gewoon niet uit handen vallen. Die behandelen we met discretie, zorg en een vast aanspreekpunt, van ophaling tot bewijs.", image=IMG["handoff"], cta=("Bespreek je zending", "andere")) + re.sub(r"<p>Sommige zendingen mogen.*?</p>", "", SENS.replace("<h3>Gevoelige leveringen, met vertrouwen.</h3>", "<h2>Waar we mee omgaan.</h2>"), count=1, flags=re.S).replace('class="sens" id="gevoelig"', 'class="sens" id="gevoelig" style="margin-top:0"').replace('<div class="sens" id="gevoelig">', '<div class="sens" id="gevoelig">') + ctaband(slug, "Een gevoelige zending? Vertel ons wat er mee moet.", "andere", "Bespreek je zending"), meta_faq
    if slug == "vaste-rondes-en-bevoorrading":
        return promote_h1(BENTO) + ctaband(slug, "Een vaste ronde of bevoorrading regelen?", "andere", "Vraag een voorstel"), meta_faq
    if slug == "logistieke-partners":
        body = pagehead(slug, "Word toonaangevend in first en last mile.", "Cargo Velo ondersteunt ambitieuze logistieke partners bij de first en de last mile. Met specialisten en support bied je jouw klanten voortaan ook duurzame distributie in de stad.", image=IMG["ramp"], cta=("Word partner", "andere"))
        blocks = """<section class="light"><div class="wrap"><div class="head"><h2>De one-stop-shop voor kwaliteit.</h2></div><div class="sgrid sgrid3">
<div class="sc"><h4>Last-mile specialist</h4><p>Meer dan tien jaar ervaring in 100% schone stadslogistiek.</p><small>Zorgeloze first en last mile in en uit de stad.</small></div>
<div class="sc g"><h4>Klaar om te schalen</h4><p>Een peloton van 25 koeriers, uitgerust voor grote volumes: honderden pakketjes per dag.</p><small>Cargofietsen en trailers vervoeren tot 150 kilo per rit.</small></div>
<div class="sc"><h4>Thuis in elke stad</h4><p>Actief in Gent, Antwerpen en Brussel, met hubs aan de stadsrand en een shuttle tussen de steden.</p><small>Koppeling met je verzendsysteem.</small></div>
</div></div></section>
<section class="paper light"><div class="wrap"><div class="head"><h2>Focus op je kern, met specialisten en support.</h2><p>Een vaste aanspreekpersoon, kant-en-klaar marketingmateriaal met referenties en het salesverhaal waarmee je prospecten overtuigt, en kennis van aanbestedingen.</p></div>
<div class="sgrid sgrid3"><div class="sc"><h4>Easypost</h4><p>Dagelijks gebundelde postzakken ophalen bij bedrijven, binnen specifieke tijdsvensters.</p></div><div class="sc"><h4>Euro-Sprinters</h4><p>Dringende pakketten met de hoogste kwaliteit en merkervaring bij de ontvanger.</p></div><div class="sc"><h4>DHL</h4><p>Secuur transport van waardevolle items in een grootschalige aanbesteding.</p></div></div></div></section>"""
        return body + blocks + ctaband(slug, "Groei samen met de koploper in duurzame stadsdistributie.", "andere", "Word partner"), meta_faq
    if slug == "steden":
        return promote_h1(SEC["steden"]) + f'<section class="paper light"><div class="wrap"><div class="head"><h2>Kies je stad.</h2></div><div class="sgrid sgrid3">' + "".join(f'<a class="sc" href="{url(slug, "steden/"+c)}" data-track="stad-{c}"><div><h4>Fietskoerier in {n}</h4><p>{d}</p></div></a>' for c, n, d in [("gent", "Gent", "Thuishaven, met AZ Sint-Lucas en de biotechcluster."), ("antwerpen", "Antwerpen", "Samen met De Fietskoerier."), ("brussel", "Brussel", "Vaste labrondes, filialen en zendingen.")]) + "</div></div></section>" + ctaband(slug, "Zit je net buiten onze steden? Vraag het ons.", "andere", "Vraag het ons"), meta_faq
    if slug == "klanten":
        return pagehead(slug, "Meer dan 1000 klanten laten zich ontzorgen.", "Van ziekenhuizen tot koffiebranders en van webshops tot overheden: dit zeggen en ervaren onze klanten.", image=IMG["doorstep"]) + SEC["klanten"] + SEC["reviews"] + ctaband(slug, "Word ook ontzorgd.", None), meta_faq
    if slug == "duurzaamheid":
        return promote_h1(SEC["duurzaam"]) + ctaband(slug, "Verduurzaam je leveringen vandaag.", None), meta_faq
    if slug == "over-ons":
        return pagehead(slug, "Mensen die je stad kennen.", "Cargo Velo en De Fietskoerier zijn samen het grootste fietskoeriersbedrijf van België. Opgeleide, vaste koeriers die de kortste weg kennen en met een glimlach afleveren.", image=IMG["team"], cta=("Plan je levering", None)) + re.sub(r"<p>Cargo Velo en De Fietskoerier zijn samen.*?</p>", "", SEC["mensen"].replace("<h2>Mensen die je stad kennen.</h2>", "<h2>Onze mensen.</h2>"), count=1, flags=re.S) + f'<section class="paper light"><div class="wrap"><p class="big">Meer lezen over ons verhaal, de fusie en werken bij Cargo Velo? <a href="{url(slug, "")}../v1/nl/over-ons/" style="text-decoration:underline">Bekijk de huidige pagina</a> of <a href="{url(slug, "")}../v1/nl/over-ons/word-fietskoerier/" style="text-decoration:underline">word fietskoerier</a>.</p></div></section>' + ctaband(slug, "Maak kennis met je vaste koerier.", None), meta_faq
    if slug == "contact":
        form = SEC["boeken"].replace("<h2>Zeg wat je kwijt wil. Wij ontzorgen de rest.</h2>", "<h1>Zeg wat je kwijt wil. Wij ontzorgen de rest.</h1>")
        return form, meta_faq
    raise KeyError(slug)

J_BTN = '\n// ---- snazzy CTA buttons + live dispatch status ----\n(function(){\n var fine=matchMedia(\'(pointer:fine)\').matches;\n var BIKE=\'<svg class="rd" viewBox="0 0 24 16" aria-hidden="true"><circle cx="4.5" cy="11" r="3.4"/><circle cx="19.5" cy="11" r="3.4"/><path d="M4.5 11l5-7.5h5.5l4.5 7.5M9.5 3.5L13 11"/></svg>\';\n var btns=[];\n document.querySelectorAll(\'.btn-green\').forEach(function(b){\n  if(b.closest(\'form\')||b.tagName===\'SPAN\'||b.classList.contains(\'go\'))return;\n  var t=b.textContent.trim();b.classList.add(\'go\');btns.push(b);\n  if(/^cta-(nav|hero|head|band|sticky)$/.test(b.dataset.track||\'\'))b.classList.add(\'pulse\');\n  b.innerHTML=\'<span class="sheen"></span>\'+BIKE+\'<span class="lbl"></span>\';b.querySelector(\'.lbl\').textContent=t;\n  b.addEventListener(\'pointermove\',function(e){var r=b.getBoundingClientRect();b.style.setProperty(\'--mx\',(e.clientX-r.left)+\'px\');b.style.setProperty(\'--my\',(e.clientY-r.top)+\'px\')});\n  b.addEventListener(\'pointerdown\',function(e){var r=b.getBoundingClientRect(),s=document.createElement(\'span\');s.className=\'rip\';s.style.left=(e.clientX-r.left)+\'px\';s.style.top=(e.clientY-r.top)+\'px\';b.appendChild(s);setTimeout(function(){s.remove()},650)});\n });\n if(!reduce&&fine&&btns.length){var raf=0,px=0,py=0;\n  document.addEventListener(\'pointermove\',function(e){px=e.clientX;py=e.clientY;if(raf)return;raf=requestAnimationFrame(function(){raf=0;\n   btns.forEach(function(b){var r=b.getBoundingClientRect();if(r.bottom<-100||r.top>innerHeight+100){return}\n    var cx=r.left+r.width/2,cy=r.top+r.height/2,dx=px-cx,dy=py-cy,d=Math.hypot(dx,dy),reach=r.width/2+70;\n    if(d<reach){var k=Math.min(1,(reach-d)/reach);b.style.setProperty(\'--tx\',(dx*.22*k).toFixed(1)+\'px\');b.style.setProperty(\'--ty\',(dy*.3*k).toFixed(1)+\'px\')}\n    else{b.style.setProperty(\'--tx\',\'0px\');b.style.setProperty(\'--ty\',\'0px\')}})})},{passive:true});\n }\n // dispatch reachable now? Klantenservice: Mon-Fri 8u-17u (Brussels time)\n function open(){try{var p=new Intl.DateTimeFormat(\'en-GB\',{timeZone:\'Europe/Brussels\',weekday:\'short\',hour:\'numeric\',hour12:false}).formatToParts(new Date()),w=p.find(function(x){return x.type===\'weekday\'}).value,h=+p.find(function(x){return x.type===\'hour\'}).value%24;return [\'Mon\',\'Tue\',\'Wed\',\'Thu\',\'Fri\'].indexOf(w)>-1&&h>=8&&h<17}catch(e){return false}}\n var on=open(),tel=document.querySelector(\'.nav .tel\');\n if(tel){var d=document.createElement(\'i\');d.className=\'dot\'+(on?\' on\':\'\');tel.insertBefore(d,tel.firstChild);tel.title=on?\'Ons dispatchteam is nu bereikbaar\':\'Dispatch bereikbaar ma tot vr, 8u tot 17u\'}\n var ds=document.getElementById(\'dispatch-status\');\n if(ds)ds.textContent=on?\'Ons dispatchteam is nu bereikbaar: 0479 33 68 99\':\'Dispatch bereikbaar ma tot vr, 8u tot 17u. Stuur je aanvraag gerust nu.\';\n})();\n'

# ---------------------------------------------------------------- extra CSS
EXTRA_CSS = """
@media (max-width:1000px){.haast .dispatch{order:2}}

/* ---- snazzy CTA ---- */
.btn-green.go{position:relative;overflow:hidden;isolation:isolate;transform:translate(var(--tx,0px),var(--ty,0px));transition:transform .18s ease-out,background .2s,color .2s,box-shadow .2s;will-change:transform;--mx:50%;--my:50%}
.btn-green.go:hover{transform:translate(var(--tx,0px),calc(var(--ty,0px) - 2px));background:var(--green);box-shadow:0 14px 34px -8px rgba(0,255,110,.65)}
.btn-green.go::after{content:"";position:absolute;left:16px;right:16px;bottom:5px;border-bottom:1.5px dashed rgba(0,0,0,0);z-index:1;transition:border-color .25s}
.btn-green.go:hover::after{border-color:rgba(0,0,0,.32)}
.btn-green.go .lbl{position:relative;z-index:2;transition:letter-spacing .25s}
.btn-green.go:hover .lbl{letter-spacing:.01em}
.btn-green.go .sheen{position:absolute;inset:0;z-index:1;opacity:0;transition:opacity .25s;background:radial-gradient(110px circle at var(--mx) var(--my),rgba(255,255,255,.95),rgba(255,255,255,0) 62%)}
.btn-green.go:hover .sheen{opacity:.9}
.btn-green.go .rd{position:absolute;left:-34px;bottom:4px;width:21px;height:14px;z-index:3;fill:none;stroke:#000;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;opacity:0;pointer-events:none}
.btn-green.go:hover .rd{animation:ride .95s cubic-bezier(.45,.05,.3,1) 1}
@keyframes ride{0%{left:-34px;opacity:1}100%{left:calc(100% + 12px);opacity:1}}
.btn-green.go.pulse{animation:ring 2.8s ease-out infinite}
.btn-green.go.pulse:hover{animation:none}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(0,255,110,.6)}65%{box-shadow:0 0 0 18px rgba(0,255,110,0)}100%{box-shadow:0 0 0 0 rgba(0,255,110,0)}}
.btn-green.go:active{transform:translate(var(--tx,0px),var(--ty,0px)) scale(.96)}
.btn-green.go .rip{position:absolute;z-index:2;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;background:rgba(0,0,0,.28);animation:rip .6s ease-out forwards;pointer-events:none}
@keyframes rip{to{transform:scale(22);opacity:0}}
.tel{display:inline-flex;align-items:center;gap:8px}
.tel .dot{width:8px;height:8px;border-radius:50%;background:#666;display:inline-block}
.tel .dot.on{background:var(--green);box-shadow:0 0 0 0 rgba(0,255,110,.7);animation:ring 2.2s infinite}
.stickycta{display:none}
@media (max-width:700px){
  .stickycta{display:flex;gap:10px;position:fixed;left:0;right:0;bottom:0;z-index:90;padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:rgba(0,0,0,.9);backdrop-filter:blur(14px);border-top:1px solid #222}
  .stickycta .btn{flex:1;padding:14px 12px;font-size:14px}
  .stickycta .btn-black{flex:0 0 auto;background:#1b1b1b;border:1px solid #333}
  body{padding-bottom:72px}
  #proto{bottom:84px}
}
@media (prefers-reduced-motion:reduce){.btn-green.go .rd{display:none}.btn-green.go.pulse,.tel .dot.on{animation:none}.btn-green.go{transform:none!important}}
.mosaic{grid-template-columns:repeat(12,1fr)}
.mosaic .a{grid-column:span 6;grid-row:span 2}.mosaic .b{grid-column:span 6}.mosaic .c,.mosaic .d{grid-column:span 3}
.co2 .zero{white-space:nowrap;font-size:clamp(48px,6.4vw,92px)}
.co2 .zero sub,.co2 .zero small{font-size:.5em}
@media (max-width:1000px){.mosaic{grid-template-columns:1fr 1fr}.mosaic .a,.mosaic .b,.mosaic .c,.mosaic .d{grid-column:span 1;grid-row:auto}}
.metrics b span{display:inline;margin:0;font:inherit;color:inherit;letter-spacing:inherit}
.nav .links{align-items:center}
.nav .links a,.nav .mt{display:inline-flex;align-items:center;height:40px;padding:0;line-height:1;font:500 15px/1 Inter}
.nav .links a::after{bottom:4px}
.nav>.wrap{display:flex;align-items:center;justify-content:space-between;height:76px;gap:20px}
.pagehead{padding:56px 0 72px}
.pagehead .crumbs{font-size:13px;color:#9a9a9a;margin-bottom:26px}
.pagehead .crumbs a{color:#cfcfcf}.pagehead .crumbs a:hover{color:var(--green)}
.pagehead .crumbs span{color:#fff}
.ph-grid{display:grid;gap:56px;align-items:center}
.pagehead.has-img .ph-grid{grid-template-columns:1.1fr .9fr}
.pagehead h1{font-size:clamp(36px,5.4vw,76px);font-weight:800;letter-spacing:-.05em;line-height:.98}
.pagehead .lead{margin:22px 0 30px;font-size:19px;color:#cfcfcf;max-width:32em}
.ph-img{border-radius:var(--r);overflow:hidden;aspect-ratio:4/3;background:#111}
.ph-img img{width:100%;height:100%;object-fit:cover;display:block}
.ctaband{padding:84px 0}
.ctaband .wrap{display:flex;justify-content:space-between;align-items:center;gap:28px;flex-wrap:wrap}
.ctaband h2{font-size:clamp(28px,3.8vw,48px);font-weight:800;letter-spacing:-.045em;max-width:16em}
.sgrid3{grid-template-columns:repeat(3,1fr)}
.sgrid-links .sc{background:#000;min-height:200px;transition:background .2s,color .2s}
.sgrid-links .sc:hover{background:var(--green);color:#000}
.sgrid-links .sc:hover p{color:#0a0a0a}
.sgrid3 .sc{background:#000;min-height:220px}
.sgrid3 .sc.g{background:var(--green)}
.sgrid3 a.sc{color:#fff}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start}
.two-col h2{font-size:clamp(30px,4vw,52px);font-weight:800;letter-spacing:-.045em;margin-bottom:16px}
.big{font-size:19px;color:var(--muted);max-width:32em;margin-bottom:22px}
.facts-col{display:grid;gap:0;border-top:2px solid #000}
.facts-i{padding:18px 0;border-bottom:1px solid var(--line)}
.facts-i b{display:block;font:700 19px Poppins;letter-spacing:-.03em}
.facts-i span{color:var(--muted);font-size:15px}
.book h1{font-size:clamp(36px,5vw,68px);font-weight:800;letter-spacing:-.05em;line-height:.98}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.light h1,.dark h1{font-weight:800}
.med h1,.dna h1,.haast h1,.cities h1,.eco h1,.sens-h1{letter-spacing:-.045em}
.med h1{font-size:clamp(34px,4.6vw,60px)}
.dna h1{font-size:clamp(34px,4.8vw,64px)}
.haast h1{font-size:clamp(34px,4.8vw,64px)}
.cities h1{font-size:clamp(34px,4.8vw,64px)}
.eco h1{font-size:clamp(34px,4.6vw,60px)}
#vaste-h1 h1,.more-h1 h1{font-size:clamp(34px,5vw,64px);font-weight:800;letter-spacing:-.045em}
@media (max-width:1000px){.pagehead.has-img .ph-grid,.two-col{grid-template-columns:1fr}.sgrid3{grid-template-columns:1fr}.ph-img{aspect-ratio:16/10}}
"""

# ---------------------------------------------------------------- write pages
def write(slug, body_faq):
    body, faq_keys = body_faq
    title, desc, _ = PAGE_META[slug]
    depth = 0 if not slug else slug.count("/") + 1
    has_form = 'id="form"' in body
    has_city = 'id="cpanel"' in body
    has_hero = 'id="hv"' in body
    cta_href = "#boeken" if slug == "" else url(slug, "contact")
    sticky = "" if slug == "contact" else f'<div class="stickycta"><a class="btn btn-black" href="tel:+32479336899" data-track="bel-sticky">Bel dispatch</a><a class="btn btn-green" href="{cta_href}" data-track="cta-sticky">Plan je levering</a></div>'
    faq_block = "" if slug in ("",) else faq_html(faq_keys)
    if slug == "": faq_block = faq_html(["steden", "intercity", "buiten", "haast", "klant", "bewijs"]); faq_keys = ["steden", "intercity", "buiten", "haast", "klant", "bewijs"]
    page = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700;800&display=swap" rel="stylesheet">
{jsonld(slug, faq_keys)}
{STYLE.replace("</style>", EXTRA_CSS + "</style>")}
</head>
<body>
<div id="proto" role="navigation" aria-label="Prototype versie"><a href="{'../' * (depth + 1)}v1/nl/" title="Bekijk de huidige site (kloon)">v1</a><span aria-current="true">v2</span></div>
{nav(slug)}
{body}
{faq_block}
{footer(slug)}
{sticky}
{script(slug, has_form, has_city, has_hero)}
</body>
</html>
"""
    page = fix_links(page, slug)
    d = os.path.join(V2, slug) if slug else V2
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)

if __name__ == "__main__":
    for slug, _ in PAGES:
        write(slug, build_body(slug))
        print("built", slug or "/")
