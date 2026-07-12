#!/usr/bin/env python3
"""Static build: content/*.json -> site/index.html

The admin panel writes these JSON files; this script regenerates the HTML.
Markup is rendered at build time (not fetched by JS) so crawlers and the
first paint both get the real content.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CONTENT = os.path.join(SITE, "content")


def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)


def e(s):
    return html.escape(str(s), quote=True)


site = load("site.json")
projects = load("projects.json")
quotes = load("testimonials.json")

with open(os.path.join(SITE, "assets/css/style.css"), encoding="utf-8") as f:
    css = f.read()
# crude minify: strip comments + collapse whitespace (safe for this stylesheet)
css_min = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
css_min = re.sub(r"\s+", " ", css_min)
css_min = re.sub(r"\s*([{};:,>])\s*", r"\1", css_min).replace(";}", "}").strip()

cards = []
for i, p in enumerate(projects):
    span = "card--wide" if p.get("featured") else ""
    slug = p["slug"]
    w, h = p["width"], p["height"]
    # first two images are above the fold on desktop -> eager, high priority
    eager = i < 2
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    cards.append(f'''      <button class="card {span} reveal" type="button"
        data-full="assets/img/{slug}@2x.webp"
        data-alt="{e(p['alt'])}"
        data-title="{e(p['title'])}"
        data-category="{e(p['category'])}"
        data-year="{e(p['year'])}"
        data-description="{e(p['description'])}"
        aria-label="Open {e(p['title'])} — {e(p['category'])}">
        <div class="card-media">
          <img src="assets/img/{slug}.webp"
               srcset="assets/img/{slug}.webp {w // 2}w, assets/img/{slug}@2x.webp {w}w"
               sizes="(max-width: 560px) 92vw, (max-width: 860px) 46vw, {'88vw' if p.get('featured') else '44vw'}"
               width="{w // 2}" height="{h // 2}"
               alt="{e(p['alt'])}" {loading}>
        </div>
        <div class="card-meta">
          <h3>{e(p['title'])}</h3>
          <span class="cat">{e(p['category'])} — {e(p['year'])}</span>
        </div>
      </button>''')

quote_html = []
dot_html = []
for i, q in enumerate(quotes):
    active = " is-active" if i == 0 else ""
    quote_html.append(f'''        <figure class="quote{active}">
          <blockquote>“{e(q['quote'])}”</blockquote>
          <figcaption><strong>{e(q['name'])}</strong> <span>— {e(q['role'])}, {e(q['company'])}</span></figcaption>
        </figure>''')
    dot_html.append(
        f'<button class="dot" role="tab" aria-selected="{"true" if i == 0 else "false"}" '
        f'aria-label="Testimonial {i + 1}: {e(q["name"])}"></button>'
    )

socials = "\n".join(
    f'            <li><a href="{e(s["url"])}" rel="noopener">{e(s["label"])}</a></li>' for s in site["socials"]
)

ld = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": site["name"],
    "jobTitle": site["role"],
    "url": site["domain"],
    "email": "mailto:" + site["email"],
    "address": {"@type": "PostalAddress", "addressLocality": site["location"]},
    "description": site["seo_description"],
    "sameAs": [s["url"] for s in site["socials"] if s["url"] != "#"],
}

doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(site['seo_title'])}</title>
<meta name="description" content="{e(site['seo_description'])}">
<link rel="canonical" href="{e(site['domain'])}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(site['seo_title'])}">
<meta property="og:description" content="{e(site['seo_description'])}">
<meta property="og:url" content="{e(site['domain'])}/">
<meta property="og:image" content="{e(site['domain'])}/assets/img/{projects[0]['slug']}@2x.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fbfaf8">
<link rel="preload" as="image" href="assets/img/{projects[0]['slug']}.webp"
      imagesrcset="assets/img/{projects[0]['slug']}.webp {projects[0]['width'] // 2}w, assets/img/{projects[0]['slug']}@2x.webp {projects[0]['width']}w">
<style>{css_min}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#work" style="position:absolute;left:-9999px">Skip to work</a>

<header class="site-head">
  <div class="wrap">
    <a class="brand" href="#top">{e(site['name'])} <em>— {e(site['role'])}</em></a>
    <nav class="nav" aria-label="Primary">
      <a href="#work">Work</a>
      <a href="#about">About</a>
      <a href="#testimonials">Clients</a>
      <a href="#contact">Contact</a>
    </nav>
  </div>
</header>

<main id="top">
  <section class="hero" id="about">
    <div class="wrap hero-grid">
      <div>
        <h1>{e(site['tagline'].split(' for ')[0])} <em>for people who care how it is made.</em></h1>
        <p class="lead">{e(site['bio_lead'])}</p>
        <p class="body">{e(site['bio_body'])}</p>
        <ul class="meta-list">
          <li><span class="k">Based in</span><span>{e(site['location'])}</span></li>
          <li><span class="k">Practice</span><span>Identity · Editorial · Type</span></li>
          <li><span class="k">Availability</span><span>Taking commissions</span></li>
        </ul>
      </div>
      <figure class="portrait">
        <img src="assets/img/portrait.webp"
             srcset="assets/img/portrait.webp 600w, assets/img/portrait@2x.webp 1200w"
             sizes="(max-width: 900px) 0px, 30vw"
             width="600" height="750" alt="Portrait of {e(site['name'])} in the studio" loading="lazy" decoding="async">
        <figcaption>Studio — {e(site['location'])}</figcaption>
      </figure>
    </div>
  </section>

  <section class="work" id="work">
    <div class="wrap">
      <p class="eyebrow">Selected Work — {len(projects):02d} Projects</p>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>

  <section class="quotes" id="testimonials">
    <div class="wrap">
      <p class="eyebrow">Clients</p>
      <div class="quote-stage">
{chr(10).join(quote_html)}
      </div>
      <div class="quote-nav" role="tablist" aria-label="Testimonials">
        {chr(10).join("        " + d for d in dot_html).strip()}
      </div>
    </div>
  </section>

  <footer class="site-foot" id="contact">
    <div class="wrap">
      <div class="foot-grid">
        <div>
          <p class="eyebrow">Contact</p>
          <h2>Have something worth making?</h2>
          <a class="mailto" href="mailto:{e(site['email'])}">{e(site['email'])}</a>
        </div>
        <div>
          <ul class="socials">
{socials}
          </ul>
        </div>
      </div>
      <div class="colophon">
        <span>© <span id="yr">2026</span> {e(site['name'])}</span>
        <span>All work shown is the property of its respective clients</span>
      </div>
    </div>
  </footer>
</main>

<div class="lb" id="lightbox" role="dialog" aria-modal="true" aria-label="Project image viewer" aria-hidden="true">
  <div class="lb-bar">
    <span class="lb-count">01 / {len(projects):02d}</span>
    <button class="lb-close" type="button" aria-label="Close viewer">Close ✕</button>
  </div>
  <div class="lb-stage"><img src="" alt=""></div>
  <div class="lb-foot">
    <div class="lb-info">
      <h3></h3>
      <p></p>
    </div>
    <div class="lb-arrows">
      <button class="lb-arrow lb-prev" type="button" aria-label="Previous project">← Prev</button>
      <button class="lb-arrow lb-next" type="button" aria-label="Next project">Next →</button>
    </div>
  </div>
</div>

<script src="assets/js/main.js" defer></script>
</body>
</html>
'''

with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
    f.write(doc)

# sitemap + robots
with open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{site["domain"]}/</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>\n'
        "</urlset>\n"
    )
with open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: {site['domain']}/sitemap.xml\n")

print(f"built index.html — {len(projects)} projects, {len(quotes)} testimonials, css {len(css_min) // 1024}KB inlined")
