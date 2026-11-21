# Cargo Velo prototype

A prototype for the Cargo Velo team. **Not the official website.** It is hidden from search engines (`noindex`).

| | What | Path |
|---|---|---|
| **Start page** | Choose v1 or v2 | `/` |
| **v1** | The current cargovelo.be, cloned as closely as possible: all 61 pages in Dutch and French from the sitemap | `/v1/nl/`, `/v1/fr/` |
| **v2** | The prototype: 16 pages positioned on *ontzorgen* (home, Haast, medical samples, DNA/biotech, sensitive deliveries, vaste rondes, logistics partners, webshops, the three-city network with a page per city, customers, sustainability, about, request form) | `/v2/` |
| **Strategy** | Positioning, 18-month growth plan, query coverage (internal) | `/v2/strategie/` |

A small switch in the bottom-left corner of every page moves between v1 and v2.

## How v1 is built

- The HTML of every page in the site's sitemap was copied. Page links point to the clone.
- Images, scripts and the homepage video are loaded from `cargovelo.be`, so v1 always shows the latest assets and needs no copied media. The theme stylesheet and its fonts (Inter, Poppins) are copied, because browsers block cross-origin fonts.
- Analytics and canonical tags were removed, and forms are disabled (they show a notice) so the prototype never creates real enquiries.
- If cargovelo.be is down or changes, v1 may look different from the live site.

## How v2 is built

v2 is generated: `python3 tools/build_v2.py` assembles the pages from the one-page prototype in `tools/v2_onepage.html` (kept as a component library). Edit the script or that file, rebuild, then commit. Each page has its own title, description, breadcrumb and FAQ, plus Service, FAQPage and LocalBusiness JSON-LD. Every page is `noindex` for now.

Click tracking for the team: call-to-actions carry their source (`data-track`), and the request email includes `Via_pagina` (the call-to-action and page clicked) and `Bekeken_paginas` (pages viewed in that session). Nothing is sent anywhere until a visitor submits a request.

## v2 form (sends an email)

The form on `/v2/contact/` (and the bottom of the home page) sends each submission by email to **nysjo85@gmail.com** with **pieter@legal.io** in copy, using [FormSubmit](https://formsubmit.co) (a free service, because GitHub Pages is static).

- **First time:** the first real submission makes FormSubmit email nysjo85@gmail.com asking to confirm. Confirm once and every later submission is delivered. Nothing has been sent from the prototype yet.
- **Spam:** includes a hidden honeypot field. The addresses are visible in the page source. After activation FormSubmit can give a random alias to use instead; change `TO` in `tools/v2_onepage.html` and rebuild.
- **If sending fails** the form offers a pre-filled `mailto:` link and the phone number.
- To change recipients, edit `TO` and `CC` near the bottom of `tools/v2_onepage.html`, run `python3 tools/build_v2.py`, and commit.

## Things to confirm (also listed on the strategy page)

- Eurofins, and the German partner "Printship", were given by Jo. They are named in v2's DNA section but could not be verified publicly. Plasmidsaurus is on the current site.
- Medical compliance wording (FAMHP, FAVV, GDP, ADR, UN3373) and the hub and shuttle details before promising same-day city-to-city service.
- Reviews use the text of the site's own Google review cards, with the reviewers' names.
- Revenue by business line, to calibrate the 18-month plan.

## Research sources

- New Mobility, Cargo Velo and Fietskoerier merger (May 2026): https://newmobility.news/en/2026/05/12/cargo-velo-pedals-ahead-with-antwerp-rival-fietskoerier-acquisition/
- Merger coverage: https://www.made-in.be/oost-vlaanderen/de-fietskoerier-en-cargo-velo-fuseren-tot-grootste-fietskoeriersbedrijf-van-belgie/
- City of Ghent last-mile providers: https://stad.gent/nl/mobiliteit-openbare-werken/duurzame-stedelijke-logistiek-gent
- ZAS Antwerp cargo bike deliveries: https://urban-mobility-observatory.transport.ec.europa.eu/news-events/news/antwerp-hospitals-go-green-cargo-bike-deliveries-2025-06-27_en
- AML lab logistics: https://www.aml-lab.be/en/doctor/Logistics
- Eurofins Genomics drop boxes: https://eurofinsgenomics.com/en/products/dna-sequencing/dropboxes/
- Plasmidsaurus instructions: https://plasmidsaurus.com/instructions
- Ghent low-emission zone: https://stad.gent/nl/mobiliteit-openbare-werken/lage-emissiezone
- Brussels low-emission zone: https://www.brussels.be/low-emission-zone-new-ban-2026
- Flanders zero-emission zones for city logistics: https://www.vlaanderen.be/mobiliteitsprofessionals/goederenvervoer/stedelijke-logistiek/zero-emissiezones-voor-stadslogistiek-zes
- Same-day delivery in Belgium: https://www.easyship.com/blog/same-day-delivery-in-belgium

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.
