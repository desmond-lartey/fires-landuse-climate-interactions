#!/usr/bin/env python3
"""
Build the fires-landuse-climate-interactions documentation site.

This is a plain Python templating script, not a framework: it renders
static HTML into docs/, which GitHub Pages then serves as-is. There is no
Jekyll config, no mkdocs, and no GitHub Actions workflow involved — you
only need to re-run this script (`python tools/build_site.py`) after
editing PAGE_SECTIONS below, then commit the regenerated docs/ files.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

REPO_URL = "https://github.com/desmond-lartey/fires-landuse-climate-interactions"
DOI = "10.1177/19400829261486748"
DOI_URL = f"https://doi.org/{DOI}"
JOURNAL = "Tropical Conservation Science"

# ---------------------------------------------------------------- nav ----

NAV = [
    ("index.html", "Home"),
    ("study-design.html", "Study Design"),
    ("pipeline.html", "Pipeline"),
    ("script-reference.html", "Script Reference"),
    ("data-outputs.html", "Data &amp; Outputs"),
    ("findings.html", "Findings"),
]

PAGE_META = {
    "index.html": ("Home", "Overview, headline findings, and quick links."),
    "study-design.html": ("Study Design", "Objective, study region, ecological zones, protected areas, and data sources."),
    "pipeline.html": ("Pipeline", "Environment setup and the exact run order of every script."),
    "script-reference.html": ("Script Reference", "Function-by-function documentation for every Earth Engine script."),
    "data-outputs.html": ("Data & Outputs", "Intermediate assets, output CSV schema, and repository layout."),
    "findings.html": ("Findings", "Headline results and zone-by-zone operational guidance."),
}

# ------------------------------------------------------------- icons -----

ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    "sun": '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "moon": '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    "github": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.79-.25.79-.55 0-.27-.01-1.16-.02-2.11-3.2.7-3.88-1.36-3.88-1.36-.52-1.34-1.28-1.69-1.28-1.69-1.04-.72.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.76 2.69 1.25 3.35.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.19-3.09-.12-.29-.52-1.47.11-3.06 0 0 .97-.31 3.18 1.18a11 11 0 015.8 0c2.2-1.49 3.17-1.18 3.17-1.18.64 1.6.24 2.77.12 3.06.74.8 1.18 1.83 1.18 3.09 0 4.43-2.69 5.4-5.25 5.69.41.36.78 1.06.78 2.14 0 1.55-.01 2.79-.01 3.17 0 .3.21.66.8.55A10.52 10.52 0 0023.5 12C23.5 5.65 18.35.5 12 .5z"/></svg>',
    "note": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v5h1"/></svg>',
    "tip": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.6 10.8c.5.4.8 1 .8 1.7v.5h5.6v-.5c0-.6.3-1.2.8-1.7A6 6 0 0012 3z"/></svg>',
    "warning": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9L1.8 18a1 1 0 00.9 1.5h18.6a1 1 0 00.9-1.5L13.7 3.9a1 1 0 00-1.7 0z"/><path d="M12 9v5M12 17h.01"/></svg>',
    "success": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/></svg>',
    "danger": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.5 2H19a1 1 0 011 1v3.5L22 12l-2 3.5V19a1 1 0 01-1 1h-3.5L12 22l-3.5-2H5a1 1 0 01-1-1v-3.5L2 12l2-3.5V5a1 1 0 011-1h3.5z"/><path d="M12 8v5M12 16h.01"/></svg>',
}

ADMON_TITLES = {"note": "Note", "tip": "Tip", "warning": "Warning", "success": "Complete", "danger": "Caution"}


def admon(kind, title, body_html):
    label = title or ADMON_TITLES[kind]
    return (
        f'<div class="admon {kind}"><div class="admon-title">{ICONS[kind]}{label}</div>{body_html}</div>'
    )


def code(fname, lang, text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    bar = ""
    if fname:
        bar = (f'<div class="codebar"><span class="fname">{fname}</span>'
               f'<span class="lang">{lang}</span><button class="copy" type="button">Copy</button></div>')
    return f'<div class="codewrap tall">{bar}<pre><code>{text}</code></pre></div>'


def code_small(fname, lang, text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    bar = (f'<div class="codebar"><span class="fname">{fname}</span>'
           f'<span class="lang">{lang}</span><button class="copy" type="button">Copy</button></div>')
    return f'<div class="codewrap">{bar}<pre><code>{text}</code></pre></div>'


# =====================================================================
# PAGE CONTENT
# Each entry: (filename, sections) where sections = [(id, "H2 label"), ...]
# used to build both the sidebar sub-nav and the right-hand "on this page" TOC.
# The actual HTML body is built by the page_<slug>() functions below.
# =====================================================================

PAGE_SECTIONS = {
    "index.html": [
        ("about", "About this study"),
        ("headline", "Headline findings"),
        ("calendar", "Fire-season calendar"),
        ("map", "Quick links"),
        ("cite", "Citation"),
    ],
    "study-design.html": [
        ("objective", "Objective"),
        ("domain", "Study region and period"),
        ("questions", "Research questions"),
        ("zones", "Ecological zones"),
        ("parks", "Protected areas evaluated"),
        ("sources", "Data sources"),
    ],
    "pipeline.html": [
        ("environment", "Environment"),
        ("run-order", "Run order"),
        ("pull", "Pulling exports into the repository"),
        ("products", "Key data products"),
        ("troubleshoot", "Troubleshooting"),
    ],
    "script-reference.html": [
        ("burned-area", "01 · burned_area_composites.js"),
        ("buffer", "02 · buffer_disaggregation.js"),
        ("landcover", "03 · landcover_harmonisation.js"),
        ("climate", "04 · climate_integration.js"),
        ("combined", "05 · combined_pipeline.js"),
        ("seasonal", "05b · seasonal_fire_rainfall.js"),
        ("functions", "Full function reference"),
    ],
    "data-outputs.html": [
        ("assets", "Intermediate Earth Engine assets"),
        ("schema", "Output CSV schema"),
        ("repo", "Repository layout"),
    ],
    "findings.html": [
        ("headline", "Headline results"),
        ("frequency", "Frequency by protected area"),
        ("rainfall", "Rainfall coupling"),
        ("gradient", "Buffer and land-cover gradient"),
        ("guidance", "Zone-by-zone guidance"),
        ("timing", "Inside vs. outside timing"),
    ],
}


def load_calendar_table():
    with open(os.path.join(ROOT, "tools", "_calendar_fragment.html")) as fh:
        return fh.read()


# ------------------------------------------------------------- Home ------

def page_index():
    cal = load_calendar_table()
    return f"""
<p class="eyebrow">{ICONS['success']}Published research &middot; documentation site</p>
<h1>Fire, land use, and climate interactions in West African conservation landscapes</h1>
<p class="lede">A spatially explicit, buffer-based analysis of 20 years (2004&ndash;2024) of MODIS
burned-area detections across 15 protected areas in C&ocirc;te d'Ivoire, Ghana, Togo, Burkina Faso,
Benin, and Nigeria &mdash; integrating harmonized GLAD/ESRI land cover and ERA5-Land climate
reanalysis to explain why fire regimes differ across ecological zones, buffer distance, and
vegetation type.</p>

<div class="badges">
  <span class="badge pub">{ICONS['success']}Published</span>
  <span class="badge doi"><a href="{DOI_URL}">DOI {DOI}</a></span>
  <span class="badge">Journal <b>{JOURNAL}</b></span>
  <span class="badge">Period <b>2004&ndash;2024</b></span>
  <span class="badge">Protected areas <b>15</b></span>
  <span class="badge">Ecological zones <b>4</b></span>
  <span class="badge">License <b>MIT</b> (code)</span>
</div>

<section id="about">
<h2>About this study</h2>
<p>Fire shapes vegetation structure, biodiversity, and carbon dynamics across West African protected
areas (PAs), yet fine-scale interactions of climatic, ecological, and landscape controls on burning
have remained poorly understood. This study analyzed fire dynamics across 15 PAs in four ecological
zones, using 20 years (2004&ndash;2024) of MODIS burned area data, harmonized GLAD and ESRI land
cover, and ERA5 climate reanalysis within a buffer-based spatial framework (0&ndash;20&nbsp;km) that
captures the gradient from PA interiors to surrounding human-modified landscapes.</p>
<div class="grid">
  <div class="card"><span class="k">Data inputs</span><h3>Four remotely sensed layers</h3>
  <p>MODIS MCD64A1 burned area (500&nbsp;m), harmonized GLAD 2000&ndash;2020 / ESRI 2021&ndash;2024
  land cover (30&nbsp;m / 10&nbsp;m), and ERA5-Land monthly climate reanalysis (~25&nbsp;km), reduced
  to park- and buffer-level zonal statistics in Google Earth Engine.</p></div>
  <div class="card"><span class="k">Spatial framework</span><h3>Interior-to-edge gradients</h3>
  <p>Each park is analysed as five concentric units &mdash; the interior (0&nbsp;km) and buffer rings
  at 5, 10, 15, and 20&nbsp;km &mdash; so fire exposure, land cover, and climate can be compared from
  park core to surrounding landscape.</p></div>
</div>
</section>

<section id="headline">
<h2>Headline findings</h2>
<ul>
  <li><strong>Northern Savanna parks burn hardest and most predictably.</strong> Mole, Comoé, and
  W (Benin) reach 57&ndash;61% of park area burned in December alone; Southern Forest parks (Bia,
  Marahoué) stay near zero regardless of season.</li>
  <li><strong>Dry-season rainfall is the dominant climatic control.</strong> Burned area rises as
  precipitation falls (pooled slope &minus;371.08&nbsp;km&sup2;/mm, p&nbsp;&lt;&nbsp;0.001); the
  effect is individually significant at Gashaka-Gumti (p&nbsp;=&nbsp;0.014).</li>
  <li><strong>Fire exposure declines from park interior to edge</strong> &mdash; strongest in
  Northern Savanna, essentially flat in Southern Forest, where fire is ecologically constrained at
  any distance.</li>
  <li><strong>Ecological zone governs fire frequency more than land-cover class does.</strong> The
  same land-cover type burns at very different rates depending on which zone it sits in.</li>
  <li><strong>Fires outside park boundaries ignite earlier and burn more</strong> than fires inside,
  pointing to stronger anthropogenic ignition pressure in surrounding landscapes.</li>
</ul>
<p>Full statistical detail is on the <a href="findings.html">Findings</a> page.</p>
</section>

<section id="calendar">
<h2>Fire-season calendar</h2>
<p>Average % of park area burned per month, October&ndash;March, 2004&ndash;2024, across all 15
protected areas:</p>
<div class="tablewrap">
<table class="data">
{cal}
</table>
</div>
<p style="font-size:0.85rem;color:var(--fg-muted);">Colour scale runs from pale (0%) to dark red
(61%, the study maximum). Derived from Figure 3 of the manuscript.</p>
</section>

<section id="map">
<h2>Quick links</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Page</th><th>What's there</th></tr></thead>
<tbody>
<tr><td><a href="study-design.html">Study Design</a></td><td>Objective, study region, research questions, ecological-zone criteria, the 15 protected areas, and the four source datasets.</td></tr>
<tr><td><a href="pipeline.html">Pipeline</a></td><td>Environment setup and the exact order every script runs in, from raw MODIS composites to the final joined CSV.</td></tr>
<tr><td><a href="script-reference.html">Script Reference</a></td><td>Every Earth Engine script, read top to bottom, with a full parameter/return reference for each custom function.</td></tr>
<tr><td><a href="data-outputs.html">Data &amp; Outputs</a></td><td>Intermediate Earth Engine asset names, the output CSV schema, and how the repository is laid out on disk.</td></tr>
<tr><td><a href="findings.html">Findings</a></td><td>Headline results and zone-by-zone operational guidance.</td></tr>
</tbody>
</table>
</div>
</section>

<section id="cite">
<h2>Citation</h2>
<div class="cite">
Lartey, D., N&rsquo;Dri, A. B., Amoako, E. E., Lawer, E. A., Issifu, H., Tsendbazar, N.,
Ametsitsi, G., Janssen, T., Konan, A., &amp; Veenendaal, E. Fire, Land Use and Climate
Interactions: Understanding the drivers of fire regimes in conservation landscapes of West
Africa. <em>{JOURNAL}</em>. <a href="{DOI_URL}">https://doi.org/{DOI}</a>
</div>
</section>
"""


# --------------------------------------------------------- Study Design --

def page_study_design():
    return f"""
<p class="eyebrow">Study design</p>
<h1>Objective, region, and framework</h1>
<p class="lede">The study region spans Upper Guinea, 5&deg;N&ndash;10&deg;N and 10&deg;W&ndash;5&deg;E,
across C&ocirc;te d'Ivoire, Ghana, Togo, Burkina Faso, Benin, and Nigeria.</p>

<section id="objective">
<h2>Objective</h2>
<p>Assess fine-scale interactions of climatic, ecological, and landscape controls on burning across
West African protected areas &mdash; controls that remain poorly understood despite advances in
remote sensing and climate modelling at larger scales &mdash; using a unified spatial and ecological
framework that allows direct comparison across parks, rather than the single-site studies that have
dominated the literature to date.</p>
</section>

<section id="domain">
<h2>Study region and period</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Item</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Study period</td><td>2004&ndash;2024 (20-year MODIS burned-area climatology, 22-year normalisation window)</td></tr>
<tr><td>Spatial domain</td><td>Upper Guinea, approximately 5&deg;N&ndash;10&deg;N, 10&deg;W&ndash;5&deg;E</td></tr>
<tr><td>Countries</td><td>C&ocirc;te d'Ivoire, Ghana, Togo, Burkina Faso, Benin, Nigeria</td></tr>
<tr><td>Rainfall gradient</td><td>Peaks near 4,000&nbsp;mm/yr, declining to ~1,200&nbsp;mm/yr at the forest&ndash;savanna boundary and further in the driest segments</td></tr>
<tr><td>Spatial framework</td><td>Five concentric analysis units per park: interior (0&nbsp;km) and buffers at 5, 10, 15, 20&nbsp;km</td></tr>
</tbody>
</table>
</div>
</section>

<section id="questions">
<h2>Research questions</h2>
<ol>
  <li>Why do protected areas differ in frequency of burning?</li>
  <li>How is overall annual burning related to rainfall and temperature variability, particularly during dry years?</li>
  <li>What is the relationship between fire activity, location, climate, and land cover types?</li>
  <li>Do different land cover types burn at different frequencies, extents, and seasonal timings?</li>
  <li>How does the timing of fires vary between inside and outside of protected areas?</li>
</ol>
</section>

<section id="zones">
<h2>Ecological zones</h2>
<p>Zones are a region-specific classification, not a global biome scheme, combining three criteria:</p>
<ul>
  <li><strong>Mean annual rainfall</strong> &mdash; following Tano et al. (2023)</li>
  <li><strong>Dry-season length</strong> &mdash; following Eva &amp; Lambin (2000) and Ouattara et al. (2024)</li>
  <li><strong>Vegetation structure</strong> &mdash; following Ametsitsi et al. (2020), Janssen et al. (2018), Liu et al. (2016)</li>
</ul>
<div class="grid">
  <div class="card"><span class="k">Northern Savanna</span><h3>Sudanian savanna</h3><p>Open canopy, continuous grass cover, long dry season. Frequent, extensive, low-intensity fire is expected.</p></div>
  <div class="card"><span class="k">Northern Forest</span><h3>Woodland&ndash;forest mosaic</h3><p>More humid than Northern Savanna. Fire expected to be less frequent and more spatially patchy.</p></div>
  <div class="card"><span class="k">Southern Transition</span><h3>Forest&ndash;savanna mosaic</h3><p>Tree and grass dominance co-exist under moderate rainfall. Intermediate, interannually variable fire activity.</p></div>
  <div class="card"><span class="k">Southern Forest</span><h3>Humid tropical forest</h3><p>Closed canopy, high rainfall, limited fire spread. Rare fire, but locally severe under drought.</p></div>
</div>
{admon("note", "Zone assignment is a hypothesis, not an assumption", "<p>These zone&ndash;fire associations are treated as testable expectations against the 15 study parks, not foregone conclusions &mdash; see <a href='findings.html#guidance'>Findings &rarr; zone-by-zone guidance</a> for how each zone actually behaved.</p>")}
</section>

<section id="parks">
<h2>Protected areas evaluated (Table 1 &amp; 2)</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>#</th><th>Protected area</th><th>Country</th><th>Rainfall (mm/yr)</th><th>Dry season</th><th>Zone</th></tr></thead>
<tbody>
<tr><td class="num">7</td><td>W (Benin)</td><td>Benin</td><td class="num">~700</td><td class="num">6&ndash;7 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">6</td><td>For&ecirc;t Class&eacute;e de Tiogo</td><td>Burkina Faso</td><td class="num">~1,200</td><td class="num">5&ndash;6 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">1</td><td>Bontioli (Partial Reserve)</td><td>Burkina Faso</td><td class="num">~1,200</td><td class="num">5&ndash;6 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">9</td><td>Bontioli (Total Reserve)</td><td>Burkina Faso</td><td class="num">~1,200</td><td class="num">5&ndash;6 mo</td><td><span class="zone nf">Northern Forest</span></td></tr>
<tr><td class="num">3</td><td>Kabor&eacute; Tambi</td><td>Burkina Faso</td><td class="num">600&ndash;700</td><td class="num">6&ndash;7 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">8</td><td>W (Burkina Faso)</td><td>Burkina Faso</td><td class="num">~700</td><td class="num">6&ndash;7 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">2</td><td>Como&eacute;</td><td>C&ocirc;te d'Ivoire</td><td class="num">900&ndash;1,100</td><td class="num">5&ndash;6 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">13</td><td>Marahou&eacute;</td><td>C&ocirc;te d'Ivoire</td><td class="num">~1,100</td><td class="num">5&ndash;6 mo</td><td><span class="zone st">Southern Transition</span></td></tr>
<tr><td class="num">15</td><td>Bia</td><td>Ghana</td><td class="num">1,500&ndash;1,800</td><td class="num">4&ndash;5 mo</td><td><span class="zone sf">Southern Forest</span></td></tr>
<tr><td class="num">11</td><td>Kogyae</td><td>Ghana</td><td class="num">1,200&ndash;1,300</td><td class="num">5&ndash;6 mo</td><td><span class="zone st">Southern Transition</span></td></tr>
<tr><td class="num">12</td><td>Kyabobo</td><td>Ghana</td><td class="num">922&ndash;1,874</td><td class="num">5&ndash;6 mo</td><td><span class="zone st">Southern Transition</span></td></tr>
<tr><td class="num">5</td><td>Mole</td><td>Ghana</td><td class="num">~1,100</td><td class="num">5&ndash;6 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">10</td><td>Gashaka-Gumti</td><td>Nigeria</td><td class="num">1,350&ndash;1,720</td><td class="num">4&ndash;5 mo</td><td><span class="zone st">Southern Transition</span></td></tr>
<tr><td class="num">4</td><td>Kainji Lake</td><td>Nigeria</td><td class="num">1,100&ndash;1,200</td><td class="num">5&ndash;6 mo</td><td><span class="zone ns">Northern Savanna</span></td></tr>
<tr><td class="num">14</td><td>Old Oyo</td><td>Nigeria</td><td class="num">900&ndash;1,500</td><td class="num">5&ndash;6 mo</td><td><span class="zone st">Southern Transition</span></td></tr>
</tbody>
</table>
</div>
<p style="font-size:0.85rem;color:var(--fg-muted);">Numbers match Figure 1 of the manuscript. IUCN
category, designation year, area, and human-occupancy detail (Table 2) are in the manuscript;
boundary attributes are exported from the authors' merged WDPA-derived shapefile.</p>
</section>

<section id="sources">
<h2>Data sources (Table 3)</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Layer</th><th>Source</th><th>Resolution</th><th>Coverage</th></tr></thead>
<tbody>
<tr><td>Burned area</td><td>MODIS MCD64A1 Collection 6.1 (Giglio et al., 2018)</td><td class="num">500&nbsp;m</td><td class="num">2004&ndash;2024</td></tr>
<tr><td>Land cover</td><td>GLAD GLCLU2020 v2 (Potapov et al., 2022) + ESRI Global LULC 10&nbsp;m (Karra et al., 2021)</td><td class="num">30&nbsp;m / 10&nbsp;m</td><td class="num">2000&ndash;2020 / 2017&ndash;2024</td></tr>
<tr><td>Climate</td><td>ERA5-Land Monthly Aggregates (ECMWF/C3S, 2018)</td><td class="num">~11&ndash;25&nbsp;km</td><td class="num">2004&ndash;2024</td></tr>
<tr><td>Park boundaries</td><td>WDPA-derived, merged authors' shapefile</td><td class="num">vector</td><td class="num">static</td></tr>
</tbody>
</table>
</div>
{admon("note", "Reconciling resolutions", "<p>Burned area (500&nbsp;m), land cover (30&nbsp;m), and climate (~11&ndash;25&nbsp;km) are never resampled onto a common pixel grid. Each layer is reduced independently to zonal statistics <em>within</em> the same park/buffer geometry, and the resulting scalars are joined by <code>(park, buffer, year)</code>. See <a href='data-outputs.html#schema'>Data &amp; Outputs</a> for the joined schema.</p>")}
</section>
"""


# -------------------------------------------------------------- Pipeline -

def page_pipeline():
    return f"""
<p class="eyebrow">Pipeline</p>
<h1>Environment, run order, and outputs</h1>
<p class="lede">The analysis runs in a fixed order. The Earth Engine steps submit extraction/export
tasks and pull results from Google Drive; a lightweight Python pass then cleans and joins the raw
exports. Full script listings and function-level documentation are on the
<a href="script-reference.html">Script Reference</a> page.</p>

{admon("tip", "Adapting this to a different region", "<p>Every asset path in the scripts is namespaced under <code>projects/ee-desmond/assets/...</code>. To run this on a different park set or region, replace that prefix with your own Earth Engine cloud project, upload your own boundary shapefile as an EE <code>FeatureCollection</code>, and update the <code>NewParkMerged</code> reference used throughout.</p>")}

<section id="environment">
<h2>Environment</h2>
{code_small("terminal", "bash", """python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

earthengine authenticate""")}
<p>Python 3.10+ recommended for the local pipeline steps. A Google Earth Engine account with a cloud
project is required for every step run in the Code Editor.</p>
</section>

<section id="run-order">
<h2>Run order</h2>
<h3>Earth Engine steps (submit tasks, download from Drive)</h3>
{code_small("run order — Earth Engine", "text", """Step 1   gee-full-script/01_burned_area_composites.js
         Sum MCD64A1 monthly burn detections into a 20-year (2004-2024)
         climatology, one composite per calendar month.
         -> SummedBurnedArea_Month{1..12}, SummedBurnedArea_AllMonths

Step 2   gee-full-script/02_buffer_disaggregation.js
         Build five buffers per park (0, 5, 10, 15, 20 km) and compute
         monthly burn frequency + burned area for each.
         -> BurnedAreaAndFrequencyResults.csv

Step 3   gee-full-script/03_landcover_harmonisation_full.js
         Harmonise GLAD (2000-2020) and ESRI (2021-2024) land cover
         into one 9-class scheme; resolve the correct source per year.

Step 4/5 gee-full-script/05_combined_pipeline_full.js
         For every park x buffer x benchmark year: burn stats, land-cover
         histogram, and 8 ERA5-Land climate variables in one export.
         -> BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2.csv

Step 6   gee-full-script/05b_seasonal_fire_rainfall_full.js
         Dry- vs wet-season burned area and rainfall totals per park/year,
         used for the Step 5 regressions.
         -> BurnedArea_ERA5Seasonal_2004_2024.csv"""
)}
{admon("warning", "Export quotas", "<p>Earth Engine limits concurrent per-user tasks. Queue the 12 monthly exports in Step 1 in smaller batches if you hit a limit, and expect the combined pipeline (Steps 4/5) to be the slowest single export &mdash; it re-runs the climate zonal mean for every park &times; buffer &times; year.</p>")}

<h3>Local steps (no Earth Engine required)</h3>
{code_small("run order — local", "bash", """# 1. Clean + join the raw exports (parses the LandUseDistribution
#    JSON column, joins benchmark-year land cover onto the per-buffer
#    burn table, derives dry/wet season totals)
python pipeline/01_clean_join.py --in DATA_DIR --out outputs/

# 2. Fit the fire-rainfall OLS regressions (within-year, multi-year, pooled)
python pipeline/02_fit_regressions.py --in outputs/BurnedArea_LC_Climate_joined.csv

# 3. Render the figures referenced on the Findings page
python pipeline/03_make_figures.py --in outputs/ --out figures/""")}
</section>

<section id="pull">
<h2>Pulling exports into the repository</h2>
<p>All <code>Export.table.toDrive</code> calls write to a <code>GEE</code> folder in Google Drive.
Download the resulting CSVs into <code>DATA_DIR/</code>, keeping the export
<code>description</code> as the filename so the local scripts can find them without edits:</p>
{code_small("expected files in DATA_DIR/", "text", """DATA_DIR/
├── BurnedAreaAndFrequencyResults.csv
├── BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2.csv
└── BurnedArea_ERA5Seasonal_2004_2024.csv""")}
</section>

<section id="products">
<h2>Key data products</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>File</th><th>Contents</th></tr></thead>
<tbody>
<tr><td><code>BurnedAreaAndFrequencyResults.csv</code></td><td>Park &times; buffer burn frequency/area, no land cover or climate</td></tr>
<tr><td><code>BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2.csv</code></td><td>Park &times; buffer &times; benchmark-year, burn + land-cover histogram + 8 climate variables</td></tr>
<tr><td><code>BurnedArea_ERA5Seasonal_2004_2024.csv</code></td><td>Park &times; year &times; season (dry/wet), burned area and rainfall totals</td></tr>
</tbody>
</table>
</div>
<p>Full column-by-column schema is on the <a href="data-outputs.html#schema">Data &amp; Outputs</a> page.</p>
</section>

<section id="troubleshoot">
<h2>Troubleshooting</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Symptom</th><th>Likely cause</th><th>Fix</th></tr></thead>
<tbody>
<tr><td><code>User memory limit exceeded</code> in <code>reduceRegion</code></td><td>Buffer geometry too large at 500&nbsp;m/30&nbsp;m scale for the default reducer memory</td><td>Raise <code>maxPixels</code> (already <code>1e13</code> in the provided scripts) and/or reduce at a coarser scale temporarily to debug</td></tr>
<tr><td>Land-cover histogram keys don't match expected 1&ndash;9</td><td>A GLAD or ESRI code wasn't included in the remap dictionary</td><td>Check the unabridged <code>gladToEsri</code> dictionary in <code>gee-full-script/03_landcover_harmonisation_full.js</code>; add any missing native codes</td></tr>
<tr><td>Seasonal script times out client-side</td><td>The nested loop calls <code>.getInfo()</code> for list lengths on every iteration</td><td>Cache list sizes once before the loop, or refactor to server-side <code>.map()</code></td></tr>
<tr><td>Precipitation values look 1000&times; too small</td><td>ERA5-Land precipitation is natively in metres, not millimetres</td><td>Confirm the <code>.multiply(1000)</code> conversion is present before export</td></tr>
</tbody>
</table>
</div>
</section>
"""


# ------------------------------------------------------- Script Reference

def fn(name_html, ret, body):
    return f'<div class="fn"><h4 class="fn-name">{name_html} <span class="ret">{ret}</span></h4>{body}</div>'


def page_script_reference():
    burned_area_js = """// Function to process and mosaic burned area data for a given date
function processBurnedArea(date, region) {
  var filtered = modisCollection.filterDate(date, ee.Date(date).advance(1, 'month'));
  var mosaicked = filtered.mosaic().clip(region);
  var burned = mosaicked.select('BurnDate').gt(0).selfMask();
  return burned.set('date', date);
}

// Function to sum burned area for a specific month across multiple years
function sumBurnedAreaForSpecificMonth(month, startYear, endYear, region) {
  var dateList = ee.List.sequence(startYear, endYear).map(function(year) {
    return ee.Date.fromYMD(year, month, 1);
  });
  var monthlyBurned = ee.ImageCollection.fromImages(
    dateList.map(function(date) { return processBurnedArea(date, region); })
  );
  return monthlyBurned.sum().set('month', month).toDouble();
}

// Function to sum burned area for all months across multiple years
function sumBurnedAreaForAllMonths(startYear, endYear, region) {
  var monthList = ee.List.sequence(1, 12);
  var allBurned = ee.ImageCollection.fromImages(
    monthList.map(function(month) {
      return sumBurnedAreaForSpecificMonth(month, startYear, endYear, region);
    })
  );
  return allBurned.sum().toDouble();
}

// Export every month, then the all-months composite
for (var month = 1; month <= 12; month++) {
  (function(month) {
    var summedBurned = sumBurnedAreaForSpecificMonth(month, 2004, 2024, area);
    Export.image.toDrive({
      image: summedBurned, description: 'SummedBurnedArea_Month' + month,
      scale: 500, region: area, fileFormat: 'GeoTIFF'
    });
  })(month);
}

var summedBurnedForAllMonths = sumBurnedAreaForAllMonths(2004, 2024, area);
Export.image.toDrive({
  image: summedBurnedForAllMonths, description: 'SummedBurnedArea_AllMonths',
  scale: 500, region: area, fileFormat: 'GeoTIFF'
});"""

    buffer_js = """var bufferDistances = ee.List.sequence(0, 20, 5).map(function(distance) {
  return ee.Number(distance).multiply(1000);
});

function calculateBurnedAreaAndFrequency(feature) {
  var results = bufferDistances.map(function(bufferDistance) {
    var bufferedGeometry = ee.Algorithms.If(
      ee.Number(bufferDistance).eq(0),
      feature.geometry(),
      feature.geometry().buffer(bufferDistance)
    );
    bufferedGeometry = ee.Geometry(bufferedGeometry);

    var burnFrequencyDict = ee.Dictionary({});
    var burnedAreaDict = ee.Dictionary({});

    months.forEach(function(month, index) {
      var burnedImage = ee.Image(burnedAreaImages[index]);
      var burnFrequency = burnedImage.reduceRegion({
        reducer: ee.Reducer.sum(), geometry: bufferedGeometry,
        scale: 500, maxPixels: 1e13
      }).get('BurnDate');
      var burnedAreaSqKm = ee.Number(burnFrequency).multiply(500 * 500).divide(1e6);
      burnFrequencyDict = burnFrequencyDict.set(month, burnFrequency);
      burnedAreaDict = burnedAreaDict.set(month, burnedAreaSqKm);
    });

    var bufferAreaSqKm = ee.Number(bufferedGeometry.area()).divide(1e6);
    var totalPixels = bufferAreaSqKm.divide(0.25); // 500 m pixel = 0.25 sqkm
    var avgBurnPerPixel = ee.Number(
      burnFrequencyDict.values().reduce(ee.Reducer.sum())
    ).divide(totalPixels);
    var avgBurnPerYear = avgBurnPerPixel.divide(22);

    return ee.Feature(bufferedGeometry, {
      'ORIG_NAME': feature.get('ORIG_NAME'),
      'Bufferdist': ee.Number(bufferDistance).divide(1000),
      'TotalPixels': totalPixels,
      'AvgBurnPerPixel': avgBurnPerPixel,
      'AvgBurnPerYear': avgBurnPerYear,
      'BufferArea_sqkm': bufferAreaSqKm
      // ...plus one {Month}_BurnFrequency / {Month}_BurnedArea_sqkm pair per month
    });
  });
  return ee.FeatureCollection(results);
}

var allResults = ee.FeatureCollection(parks.map(calculateBurnedAreaAndFrequency).flatten());
Export.table.toDrive({ collection: allResults, description: 'BurnedAreaAndFrequencyResults', fileFormat: 'CSV', folder: 'GEE' });"""

    lc_js = """var gladToEsri = ee.Dictionary({
  // Water
  200:1, 201:1, 202:1, 203:1, 204:1, 207:1, 208:1, 209:1, 210:1, 211:1,
  // Trees: stable, disturbed, gains, and height-gain sub-codes all map to class 2
  25:2, 26:2, /* ... 27 through 195 follow the same pattern ... */ 196:2,
  // Flooded vegetation
  100:3, 101:3, /* ... */ 124:3,
  // Rangeland / short vegetation
  0:9, 1:9, /* ... */ 24:9,
  // Crops
  244:4, 245:4, 246:4, 247:4, 248:4, 249:4,
  // Built-up
  250:5, 251:5, 252:5, 253:5,
  // Snow/Ice
  241:7, 242:7, 243:7
  // Clouds (8) has no GLAD equivalent -- absent by design
});

function harmoniseGlad(img) {
  return img.remap(
    gladToEsri.keys().map(ee.Number.parse),
    gladToEsri.values().map(ee.Number.parse)
  ).rename('landcover');
}

function remapEsri(image) {
  return image.remap([1,2,4,5,7,8,9,10,11], [1,2,3,4,5,6,7,8,9]).rename('landcover');
}

function getLandCoverYear(year) {
  if (year >= 2021) {
    var esriImage = esri_lulc10.filterDate(year+'-01-01', year+'-12-31').mosaic().select(0);
    return remapEsri(esriImage);
  }
  if (year >= 2000 && year <= 2020) {
    return harmoniseGlad(ee.Image('projects/glad/GLCLU2020/v2/LCLUC_' + year).select(0));
  }
  return ee.Image(0).rename('landcover');
}"""

    climate_js = """function getClimateForYear(year) {
  var start = ee.Date.fromYMD(year, 1, 1);
  var end   = ee.Date.fromYMD(year, 12, 31);

  var era5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
      .filterDate(start, end)
      .select(['temperature_2m','temperature_2m_min','temperature_2m_max',
                'dewpoint_temperature_2m','total_precipitation_sum',
                'surface_pressure','u_component_of_wind_10m','v_component_of_wind_10m'])
      .mean();

  var Tmean_C = era5.select('temperature_2m').subtract(273.15).rename('Tmean_C');
  var Tmin_C  = era5.select('temperature_2m_min').subtract(273.15).rename('Tmin_C');
  var Tmax_C  = era5.select('temperature_2m_max').subtract(273.15).rename('Tmax_C');
  var Tdew_C  = era5.select('dewpoint_temperature_2m').subtract(273.15).rename('Tdew_C');
  var Precip_mm = era5.select('total_precipitation_sum').multiply(1000).rename('Precip_mm');
  var SurfaceP_hPa = era5.select('surface_pressure').divide(100).rename('SurfaceP_hPa');
  var WindU = era5.select('u_component_of_wind_10m').rename('WindU');
  var WindV = era5.select('v_component_of_wind_10m').rename('WindV');

  return ee.Image.cat([Tmean_C, Tmin_C, Tmax_C, Tdew_C, Precip_mm, SurfaceP_hPa, WindU, WindV]);
}"""

    combined_js = """function calculateBurnedAreaAndLandUse(feature, landCover, year) {
  var results = bufferDistances.map(function(bufferDistance) {
    var geom = ee.Algorithms.If(
      ee.Number(bufferDistance).eq(0), feature.geometry(), feature.geometry().buffer(bufferDistance)
    );
    geom = ee.Geometry(geom);

    var climate = getClimateForYear(year).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: geom, scale: 11132, maxPixels: 1e13
    });

    var burnFrequencyDict = ee.Dictionary({});
    var burnedAreaDict = ee.Dictionary({});
    months.forEach(function(month, index) {
      var burnFreq = burnedAreaImages[index].reduceRegion({
        reducer: ee.Reducer.sum(), geometry: geom, scale: 500, maxPixels: 1e13
      }).get('BurnDate');
      var areaSqKm = ee.Number(burnFreq).multiply(500 * 500).divide(1e6);
      burnFrequencyDict = burnFrequencyDict.set(month + '_BurnFrequency', burnFreq);
      burnedAreaDict = burnedAreaDict.set(month + '_BurnedArea_sqkm', areaSqKm);
    });

    var landCoverStats = landCover.reduceRegion({
      reducer: ee.Reducer.frequencyHistogram(), geometry: geom, scale: 30, maxPixels: 1e13
    }).get('landcover');

    var bufferAreaSqKm = ee.Number(geom.area()).divide(1e6);
    var totalBurns = ee.Number(burnFrequencyDict.values().reduce(ee.Reducer.sum()));
    var totalPixels = bufferAreaSqKm.divide(0.0009); // 30 m LC pixels
    var avgBurnPerPixel = totalBurns.divide(totalPixels);
    var avgBurnPerYear = avgBurnPerPixel.divide(22);

    var props = ee.Dictionary({
      'ORIG_NAME': feature.get('ORIG_NAME'), 'Year': year,
      'Buffer_km': ee.Number(bufferDistance).divide(1000),
      'BufferArea_sqkm': bufferAreaSqKm, 'TotalPixels': totalPixels,
      'AvgBurnPerPixel': avgBurnPerPixel, 'AvgBurnPerYear': avgBurnPerYear,
      'LandUseDistribution': landCoverStats,
      'ERA5_Tmean_C': climate.get('Tmean_C'), 'ERA5_Tmin_C': climate.get('Tmin_C'),
      'ERA5_Tmax_C': climate.get('Tmax_C'), 'ERA5_Tdew_C': climate.get('Tdew_C'),
      'ERA5_Precip_mm': climate.get('Precip_mm'),
      'ERA5_SurfacePressure_hPa': climate.get('SurfaceP_hPa'),
      'ERA5_WindU': climate.get('WindU'), 'ERA5_WindV': climate.get('WindV')
    }).combine(burnFrequencyDict).combine(burnedAreaDict);

    return ee.Feature(geom, props);
  });
  return ee.FeatureCollection(results);
}

var allResults = ee.FeatureCollection([]);
[2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023, 2024].forEach(function(y) {
  var lcImg = getLandCoverYear(y);
  var yearFC = ee.FeatureCollection(
    parks.map(function(f) { return calculateBurnedAreaAndLandUse(f, lcImg, y); }).flatten()
  );
  allResults = allResults.merge(yearFC);
});

Export.table.toDrive({
  collection: allResults,
  description: 'BurnedArea_LC_Climate_ESRI_GLAD_2000_2024_corrected2',
  fileFormat: 'CSV', folder: 'GEE'
});"""

    seasonal_js = """var seasons = [
  {label: 'Dry', startMonth: 10, endMonth: 3},  // Oct -> Mar (crosses year boundary)
  {label: 'Wet', startMonth: 4,  endMonth: 9}   // Apr -> Sep
];

var processParkYearSeason = function(park, year, season) {
  var geom = park.geometry();
  var start = ee.Date.fromYMD(year, season.startMonth, 1);
  var end = ee.Algorithms.If(
    ee.Number(season.startMonth).gt(season.endMonth),
    ee.Date.fromYMD(ee.Number(year).add(1), season.endMonth, 28),
    ee.Date.fromYMD(year, season.endMonth, 28)
  );
  end = ee.Date(end);

  var BA_season = MODIS_BA.filterDate(start, end).map(function(img) {
    return ee.Image.pixelArea().updateMask(img.select('BurnDate').gt(0)).divide(1e6);
  }).sum();
  var baDict = BA_season.reduceRegion({
    reducer: ee.Reducer.sum(), geometry: geom, scale: 500, maxPixels: 1e13
  });
  var burnedArea_km2 = ee.Number(ee.Algorithms.If(baDict.contains('area'), baDict.get('area'), 0));

  var rainImg = ERA5.filterDate(start, end).sum().multiply(1000).rename('rainfall_mm');
  var rainDict = rainImg.reduceRegion({
    reducer: ee.Reducer.mean(), geometry: geom, scale: 27830, maxPixels: 1e13
  });
  var rainfall_mm = ee.Number(ee.Algorithms.If(rainDict.contains('rainfall_mm'), rainDict.get('rainfall_mm'), 0));

  return ee.Feature(null, {
    'Park': park.get('ORIG_NAME'), 'Year': year, 'Season': season.label,
    'BurnedArea_km2': burnedArea_km2, 'Rainfall_mm': rainfall_mm
  });
};

Export.table.toDrive({
  collection: outputFC, description: 'BurnedArea_ERA5Seasonal_2004_2024',
  folder: 'GEE', fileFormat: 'CSV',
  selectors: ['Park', 'Year', 'Season', 'BurnedArea_km2', 'Rainfall_mm']
});"""

    return f"""
<p class="eyebrow">Script reference</p>
<h1>Every Earth Engine script, read top to bottom</h1>
<p class="lede">These scripts live in <code>gee-full-script/</code> and run in the order documented on
the <a href="pipeline.html">Pipeline</a> page. They are a run-in-order study pipeline pasted directly
into the <a href="https://code.earthengine.google.com/">GEE Code Editor</a>, not an installable
package &mdash; this page documents the functions for reading and adapting the code.</p>

{admon("note", "Full unabridged source", "<p>The excerpts below are trimmed for readability. Complete, unabridged scripts &mdash; including the full ~200-entry <code>gladToEsri</code> dictionary &mdash; are in <code>gee-full-script/</code> in the repository.</p>")}

<section id="burned-area">
<h2>01 &middot; burned_area_composites.js</h2>
<p>Builds the 20-year (2004&ndash;2024) monthly burn-frequency climatology from MODIS MCD64A1, one
image per calendar month.</p>
<ul>
<li><strong><code>processBurnedArea(date, region)</code></strong> &mdash; filters MCD64A1 to a one-month window, mosaics over <code>region</code>, returns a binary "burned this month" mask.</li>
<li><strong><code>sumBurnedAreaForSpecificMonth(month, startYear, endYear, region)</code></strong> &mdash; sums that mask across a year range into a per-pixel year-count climatology.</li>
<li><strong><code>sumBurnedAreaForAllMonths(startYear, endYear, region)</code></strong> &mdash; sums all 12 months into one all-months composite.</li>
</ul>
{code(None, "GEE JS", burned_area_js)}
</section>

<section id="buffer">
<h2>02 &middot; buffer_disaggregation.js</h2>
<p>Generates five concentric buffers per park (0, 5, 10, 15, 20&nbsp;km) and computes burn frequency,
burned area, and normalised exposure rates for each.</p>
<ul>
<li><strong><code>calculateBurnedAreaAndFrequency(feature)</code></strong> &mdash; builds the five buffer geometries around one park and reduces each of the six dry-season monthly composites within them.</li>
</ul>
{code(None, "GEE JS", buffer_js)}
</section>

<section id="landcover">
<h2>03 &middot; landcover_harmonisation.js</h2>
<p>Remaps GLAD's native codes and ESRI's 11-class scheme onto one shared 9-class scheme, and resolves
the correct dataset for any requested year.</p>
<ul>
<li><strong><code>harmoniseGlad(img)</code></strong> &mdash; remaps GLAD codes via the <code>gladToEsri</code> dictionary.</li>
<li><strong><code>remapEsri(image)</code></strong> &mdash; remaps ESRI's 11 native codes onto the same 9-class target.</li>
<li><strong><code>getLandCoverYear(year)</code></strong> &mdash; dispatches to GLAD (2000&ndash;2020) or ESRI (2021&ndash;2024) automatically.</li>
</ul>
{code(None, "GEE JS", lc_js)}
</section>

<section id="climate">
<h2>04 &middot; climate_integration.js</h2>
<p>Builds an 8-band annual-mean ERA5-Land climate image with unit conversions already applied.</p>
<ul>
<li><strong><code>getClimateForYear(year)</code></strong> &mdash; K&rarr;&deg;C, m&rarr;mm, Pa&rarr;hPa conversions, one image per year.</li>
</ul>
{code(None, "GEE JS", climate_js)}
</section>

<section id="combined">
<h2>05 &middot; combined_pipeline.js</h2>
<p>The production script: for every park &times; buffer &times; benchmark year, emits burn frequency,
burned area, the land-cover histogram, and all eight climate variables in a single feature.</p>
<ul>
<li><strong><code>calculateBurnedAreaAndLandUse(feature, landCover, year)</code></strong> &mdash; the main per-park-per-year driver, merging burn stats, land cover, and climate into one output row per buffer.</li>
</ul>
{code(None, "GEE JS", combined_js)}
</section>

<section id="seasonal">
<h2>05b &middot; seasonal_fire_rainfall.js</h2>
<p>Computes dry- vs wet-season burned-area and rainfall totals per park/year &mdash; the input to the
fire&ndash;rainfall regressions.</p>
<ul>
<li><strong><code>processParkYearSeason(park, year, season)</code></strong> &mdash; one seasonal burned-area/rainfall total for one park in one year.</li>
</ul>
{code(None, "GEE JS", seasonal_js)}
{admon("warning", "Performance note", "<p>The triple loop over parks &times; years &times; seasons calls <code>.getInfo()</code> to get client-side list lengths. Fine for 15 parks &times; 21 years &times; 2 seasons (630 features), but restructure as server-side <code>.map()</code> nesting for much larger park lists.</p>")}
</section>

<section id="functions">
<h2>Full function reference</h2>
<p>Parameter and return-type documentation for every custom function above.</p>

{fn("processBurnedArea(date, region)", "&rarr; ee.Image", '''
<div class="tablewrap"><table class="data"><thead><tr><th>Parameter</th><th>Type</th><th>Description</th></tr></thead><tbody>
<tr><td>date</td><td>ee.Date</td><td>First day of the target month</td></tr>
<tr><td>region</td><td>ee.Geometry</td><td>Clipping extent (study area)</td></tr>
</tbody></table></div>
<p>Returns a single-band binary mask (<code>BurnDate &gt; 0</code>, self-masked), tagged with a <code>date</code> property.</p>''')}

{fn("sumBurnedAreaForSpecificMonth(month, startYear, endYear, region)", "&rarr; ee.Image", '''
<div class="tablewrap"><table class="data"><thead><tr><th>Parameter</th><th>Type</th><th>Description</th></tr></thead><tbody>
<tr><td>month</td><td>int (1&ndash;12)</td><td>Calendar month</td></tr>
<tr><td>startYear, endYear</td><td>int</td><td>Climatology bounds (2004, 2024)</td></tr>
<tr><td>region</td><td>ee.Geometry</td><td>Study area extent</td></tr>
</tbody></table></div>
<p>Returns the pixel-wise count of years (0&ndash;21) that recorded a burn in that month, cast to <code>double</code>.</p>''')}

{fn("sumBurnedAreaForAllMonths(startYear, endYear, region)", "&rarr; ee.Image", "<p>Calls <code>sumBurnedAreaForSpecificMonth</code> for all 12 months and sums the results into one all-months composite.</p>")}

{fn("calculateBurnedAreaAndFrequency(feature)", "&rarr; ee.FeatureCollection", '''
<div class="tablewrap"><table class="data"><thead><tr><th>Parameter</th><th>Type</th><th>Description</th></tr></thead><tbody>
<tr><td>feature</td><td>ee.Feature</td><td>One park polygon with an <code>ORIG_NAME</code> property</td></tr>
</tbody></table></div>
<p>Returns 5 features (one per buffer distance), each with the fields listed in the <a href="data-outputs.html#schema">output schema</a>. Closes over module-level <code>months</code>, <code>burnedAreaImages</code>, <code>bufferDistances</code>.</p>''')}

{fn("harmoniseGlad(img)", "&rarr; ee.Image", "<p><code>img</code>: single-band GLAD image, native codes. Returns a single band named <code>landcover</code>, values 1&ndash;9 (class 8/Clouds never appears from this source).</p>")}

{fn("remapEsri(image)", "&rarr; ee.Image", "<p><code>image</code>: single-band ESRI image, native codes <code>1,2,4,5,7,8,9,10,11</code>. Returns a single band named <code>landcover</code>, values 1&ndash;9.</p>")}

{fn("getLandCoverYear(year)", "&rarr; ee.Image", '''
<div class="tablewrap"><table class="data"><thead><tr><th>Year range</th><th>Source</th><th>Function called</th></tr></thead><tbody>
<tr><td class="num">2000&ndash;2020</td><td>GLAD GLCLU2020 v2</td><td><code>harmoniseGlad()</code></td></tr>
<tr><td class="num">2021&ndash;2024</td><td>ESRI Global LULC 10&nbsp;m</td><td><code>remapEsri()</code> after annual mosaic</td></tr>
<tr><td>other</td><td>&mdash;</td><td><code>ee.Image(0)</code> fallback</td></tr>
</tbody></table></div>''')}

{fn("getClimateForYear(year)", "&rarr; ee.Image", "<p><code>year</code>: calendar year, filtered Jan 1&ndash;Dec 31. Returns 8 bands: <code>Tmean_C</code>, <code>Tmin_C</code>, <code>Tmax_C</code>, <code>Tdew_C</code>, <code>Precip_mm</code>, <code>SurfaceP_hPa</code>, <code>WindU</code>, <code>WindV</code>.</p>")}

{fn("calculateBurnedAreaAndLandUse(feature, landCover, year)", "&rarr; ee.FeatureCollection", '''
<div class="tablewrap"><table class="data"><thead><tr><th>Parameter</th><th>Type</th><th>Description</th></tr></thead><tbody>
<tr><td>feature</td><td>ee.Feature</td><td>One park polygon</td></tr>
<tr><td>landCover</td><td>ee.Image</td><td>Output of <code>getLandCoverYear(year)</code> for the matching year</td></tr>
<tr><td>year</td><td>int</td><td>Benchmark year, forwarded to <code>getClimateForYear</code></td></tr>
</tbody></table></div>
<p>Returns 5 features (one per buffer), each with the full schema documented on <a href="data-outputs.html#schema">Data &amp; Outputs</a>.</p>''')}

{fn("processParkYearSeason(park, year, season)", "&rarr; ee.Feature", '''
<div class="tablewrap"><table class="data"><thead><tr><th>Parameter</th><th>Type</th><th>Description</th></tr></thead><tbody>
<tr><td>park</td><td>ee.Feature</td><td>One park polygon with <code>ORIG_NAME</code></td></tr>
<tr><td>year</td><td>ee.Number</td><td>Calendar year of the season's start</td></tr>
<tr><td>season</td><td>{{label, startMonth, endMonth}}</td><td>Dry (10&rarr;3) or Wet (4&rarr;9); startMonth &gt; endMonth means the season crosses the year boundary</td></tr>
</tbody></table></div>
<p>Returns a geometry-less feature with <code>Park</code>, <code>Year</code>, <code>Season</code>, <code>BurnedArea_km2</code>, <code>Rainfall_mm</code>.</p>''')}

<h3>Constants referenced throughout</h3>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Name</th><th>Value</th><th>Used by</th></tr></thead>
<tbody>
<tr><td><code>months</code></td><td><code>['Oct','Nov','Dec','Jan','Feb','Mar']</code></td><td>Scripts 02, 05</td></tr>
<tr><td><code>bufferDistances</code></td><td><code>[0, 5000, 10000, 15000, 20000]</code> m</td><td>Scripts 02, 05</td></tr>
<tr><td>Burned-area reduce scale</td><td class="num">500&nbsp;m</td><td>All burn-frequency <code>reduceRegion</code> calls</td></tr>
<tr><td>Land-cover reduce scale</td><td class="num">30&nbsp;m</td><td>All <code>frequencyHistogram</code> calls</td></tr>
<tr><td>Climate reduce scale</td><td class="num">11,132&nbsp;m</td><td>All ERA5-Land <code>reduceRegion</code> calls (native grid)</td></tr>
<tr><td>Climatology length</td><td class="num">22 years</td><td><code>AvgBurnPerYear</code> normalisation</td></tr>
</tbody>
</table>
</div>
</section>
"""


# --------------------------------------------------------- Data & Outputs

def page_data_outputs():
    return f"""
<p class="eyebrow">Data &amp; outputs</p>
<h1>Assets, schema, and repository layout</h1>
<p class="lede">Everything downstream of Earth Engine is built from a single wide CSV keyed by park,
buffer distance, and year. This page documents the intermediate assets and the resulting schema.</p>

<section id="assets">
<h2>Intermediate Earth Engine assets</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Asset ID pattern</th><th>Produced by</th><th>Contents</th></tr></thead>
<tbody>
<tr><td><code>assets/SummedBurnedArea_Month{{1..12}}</code></td><td>Script 01</td><td>21-year summed monthly burn-frequency image, 500&nbsp;m</td></tr>
<tr><td><code>assets/SummedBurnedArea_AllMonths</code></td><td>Script 01</td><td>All-months summed burn-frequency image</td></tr>
<tr><td><code>assets/NewParkMerged</code></td><td>manual GIS step</td><td>Merged 15-park boundary FeatureCollection (<code>ORIG_NAME</code>)</td></tr>
<tr><td><code>assets/GLAD_harmonised_30m_2000</code></td><td>Script 03</td><td>GLAD 2000 remapped to the 9-class scheme, 30&nbsp;m</td></tr>
<tr><td><code>assets/BurnedAreaAndFrequencyResultsAsset</code></td><td>Script 02</td><td>Park &times; buffer burn-frequency/area table, no land cover/climate</td></tr>
<tr><td><code>assets/BurnedArea_LC_Climate_ESRI_GLAD_2000_2024</code></td><td>Script 05</td><td>Park &times; buffer &times; year, burn + land cover + 8 climate variables</td></tr>
</tbody>
</table>
</div>
</section>

<section id="schema">
<h2>Output CSV schema</h2>
<p>One row per <code>(park, buffer distance, year)</code> in the land-cover-linked table &mdash;
15 parks &times; 5 buffers &times; 9 benchmark years = 675 rows. The seasonal table has one row per
<code>(park, year, season)</code> &mdash; 15 &times; 21 &times; 2 = 630 rows.</p>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Column</th><th>Type</th><th>Description</th></tr></thead>
<tbody>
<tr><td><code>ORIG_NAME</code></td><td>string</td><td>Park name</td></tr>
<tr><td><code>Year</code></td><td>int</td><td>Benchmark year or calendar year</td></tr>
<tr><td><code>Buffer_km</code></td><td>float</td><td>0, 5, 10, 15, or 20</td></tr>
<tr><td><code>BufferArea_sqkm</code></td><td>float</td><td>Geodesic area of the buffer polygon</td></tr>
<tr><td><code>{{Mon}}_BurnFrequency</code></td><td>int</td><td>Summed pixel-years burned for that month, Oct&ndash;Mar</td></tr>
<tr><td><code>{{Mon}}_BurnedArea_sqkm</code></td><td>float</td><td>Burn frequency converted to km&sup2; at 500&nbsp;m/pixel</td></tr>
<tr><td><code>TotalPixels</code></td><td>float</td><td>Buffer area &divide; pixel area at the relevant resolution</td></tr>
<tr><td><code>AvgBurnPerPixel</code></td><td>float</td><td>Summed monthly frequencies &divide; TotalPixels</td></tr>
<tr><td><code>AvgBurnPerYear</code></td><td>float</td><td>AvgBurnPerPixel &divide; 22</td></tr>
<tr><td><code>LandUseDistribution</code></td><td>dict/JSON</td><td>Class &rarr; pixel-count histogram, 30&nbsp;m</td></tr>
<tr><td><code>ERA5_Tmean_C</code>, <code>_Tmin_C</code>, <code>_Tmax_C</code>, <code>_Tdew_C</code></td><td>float</td><td>Zonal mean temperature variables, &deg;C</td></tr>
<tr><td><code>ERA5_Precip_mm</code></td><td>float</td><td>Zonal mean total precipitation, mm</td></tr>
<tr><td><code>ERA5_SurfacePressure_hPa</code></td><td>float</td><td>Zonal mean surface pressure, hPa</td></tr>
<tr><td><code>ERA5_WindU</code>, <code>ERA5_WindV</code></td><td>float</td><td>Zonal mean 10&nbsp;m wind components, m/s</td></tr>
<tr><td><code>Season</code></td><td>string</td><td>Dry (Oct&ndash;Mar) or Wet (Apr&ndash;Sep) &mdash; seasonal table only</td></tr>
<tr><td><code>BurnedArea_km2</code>, <code>Rainfall_mm</code></td><td>float</td><td>Seasonal totals &mdash; seasonal table only</td></tr>
</tbody>
</table>
</div>
{admon("note", "frequencyHistogram output", "<p><code>LandUseDistribution</code> is a nested dictionary keyed by class code (<code>\"1\"</code>&hellip;<code>\"9\"</code>) with pixel counts as values. Divide each value by the row's <code>TotalPixels</code> for a class fraction, or multiply by 0.0009&nbsp;km&sup2; (30&nbsp;m pixel area) for class area.</p>")}
</section>

<section id="repo">
<h2>Repository layout</h2>
{code_small("repository layout", "text", """fires-landuse-climate-interactions/
├── DATA_DIR/          # raw CSV/SHP exports pulled from Google Drive <- GEE
├── gee-full-script/    # canonical, unabridged Earth Engine scripts
├── pipeline/            # Python: cleaning, joins, regressions, figures
├── notebooks/            # exploratory notebooks, not part of the reproducible path
├── outputs/               # cleaned/joined CSVs consumed by pipeline scripts
├── figures/                # rendered figures referenced in the manuscript
├── docs/                    # this documentation site (GitHub Pages source)
├── archive/                  # superseded scripts, kept for provenance
└── tools/                      # the plain-Python script that builds docs/""")}
</section>
"""


# --------------------------------------------------------------- Findings

def page_findings():
    return f"""
<p class="eyebrow">Findings</p>
<h1>What the twenty-year record shows</h1>
<p class="lede">The full quantitative results &mdash; per-park regression tables, figures, and
statistics &mdash; are in the published manuscript. This page summarises the headline results and the
operational guidance that follows from them.</p>

<section id="headline">
<h2>Headline results</h2>
<ul>
<li><strong>Northern Savanna parks burn hardest and most predictably.</strong> Mole, Como&eacute;, and W (Benin) show the highest burned-area proportions, with December averages reaching 57&ndash;61% of park area.</li>
<li><strong>Dry-season rainfall is the dominant climatic control.</strong> Burned area rises as precipitation falls across fire-prone parks (pooled slope &minus;371.08&nbsp;km&sup2;/mm, p&nbsp;&lt;&nbsp;0.001, R&sup2;&nbsp;=&nbsp;0.04); Gashaka-Gumti is individually significant (p&nbsp;=&nbsp;0.014).</li>
<li><strong>Fire exposure declines from interior to edge</strong>, most strongly in Northern Savanna; Southern Forest shows almost no buffer-distance effect because fire is ecologically constrained regardless of distance.</li>
<li><strong>Ecological zone governs fire frequency more than land-cover class alone.</strong> The same land-cover type burns at very different rates depending on zone.</li>
<li><strong>Fires outside park boundaries ignite earlier and burn more extensively</strong> than fires inside, especially in savanna-dominated parks &mdash; consistent with stronger anthropogenic ignition pressure at the boundary.</li>
</ul>
</section>

<section id="frequency">
<h2>Frequency of burning by protected area</h2>
<p>Burning concentrates in the early-to-mid dry season, October through January, but the extent
differs sharply by park. Mole, Como&eacute;, and W (Benin) show the highest burned-area proportions,
with December averages reaching roughly 57&ndash;61% of park area. W (Burkina Faso), Gashaka-Gumti,
and Kabor&eacute; Tambi show strong November&ndash;January peaks &mdash; all Northern Savanna. Bia,
Marahou&eacute;, and Togo show near-zero burned area throughout the fire season. Grouped by zone,
Northern Savanna forms a clear high-burning cluster, Northern Forest and Southern Transition are
intermediate and variable, and Southern Forest is consistently near zero.</p>
<p>See the <a href="index.html#calendar">fire-season calendar</a> on the homepage for the full
15-park, 6-month heatmap this section is drawn from.</p>
</section>

<section id="rainfall">
<h2>Rainfall coupling</h2>
<p>The rainfall&ndash;fire relationship is strongest in the dry season, when fuel moisture is lowest.
Fire-prone parks &mdash; Gashaka-Gumti, Mole, Como&eacute;, Kainji Lake, and Kogyae &mdash; show
negative slopes between precipitation and burned area. Gashaka-Gumti is the only park with an
individually significant negative slope (&minus;182.69&nbsp;km&sup2;/mm, p&nbsp;=&nbsp;0.014); others
show the same direction without reaching significance, likely reflecting high interannual variability
relative to record length. Parks with limited fire activity &mdash; Bia, Tiogo, Kyabobo, Marahou&eacute;,
Bontioli &mdash; show flat or inconsistent slopes, indicating ecological rather than climatic
constraints on burning.</p>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Fit</th><th>Scale</th><th>Slope</th><th>p</th><th>R&sup2;</th></tr></thead>
<tbody>
<tr><td>Pooled, all parks &amp; years</td><td>2004&ndash;2024</td><td class="num">&minus;371.08 km&sup2;/mm</td><td class="num">&lt;0.001</td><td class="num">0.04</td></tr>
<tr><td>Gashaka-Gumti</td><td>2004&ndash;2024</td><td class="num">&minus;182.69 km&sup2;/mm</td><td class="num">0.014</td><td class="num">&mdash;</td></tr>
</tbody>
</table>
</div>
<p>Interannual peaks in dry-season burned area at fire-prone Northern Savanna parks align with drier
years (notably around 2009, 2012, 2015&ndash;2016, and 2019). Wet-season burning is negligible almost
everywhere, with occasional early-ignition exceptions at a handful of savanna parks.</p>
</section>

<section id="gradient">
<h2>Buffer and land-cover gradient</h2>
<p>Annual burned area declines with increasing distance from park boundaries, an effect strongest in
Northern Savanna, where fire frequency peaks within 5&ndash;10&nbsp;km of the interior and then
declines toward 20&nbsp;km. Parks and years with higher cumulative burned area show larger tree-cover
losses, mixed rangeland responses, and moderate cropland gains at moderate fire exposure but declines
at extreme exposure. Rangelands show the highest proportional burned area &mdash; 60&ndash;80% of
grass-dominated pixels within the 0&nbsp;km buffer at Como&eacute;, Mole, and W (Benin).</p>
</section>

<section id="guidance">
<h2>Zone-by-zone guidance</h2>
<div class="tablewrap">
<table class="data">
<thead><tr><th>Zone</th><th>Guidance</th></tr></thead>
<tbody>
<tr><td><span class="zone ns">Northern Savanna</span></td><td>Fire is frequent and largely unavoidable. Prioritise seasonal rainfall forecasts for early-burn planning and buffer-zone coordination with farming/pastoral communities rather than suppression.</td></tr>
<tr><td><span class="zone nf">Northern Forest</span></td><td>Intermediate, patchier fire activity. Monitor for encroachment of savanna-type burning at drier margins.</td></tr>
<tr><td><span class="zone st">Southern Transition</span></td><td>Fire activity is intermediate and interannually variable &mdash; the zone most sensitive to a shifting climate; context-specific management is needed for the mosaic of open and closed vegetation patches.</td></tr>
<tr><td><span class="zone sf">Southern Forest</span></td><td>Near-zero burning at any distance from the boundary. Canopy integrity, not active fire suppression, is the operative protection mechanism.</td></tr>
</tbody>
</table>
</div>
</section>

<section id="timing">
<h2>Inside vs. outside timing</h2>
<p>Fires outside park boundaries ignite earlier and burn more extensively than fires inside,
particularly in savanna-dominated parks. At Mole, Kainji Lake, Old Oyo, Gashaka-Gumti, Kyabobo, and
Togo, burned area outside the park rises sharply in November&ndash;December, peaking in
December&ndash;January, while interior burning peaks one to two months later &mdash; consistent with
earlier ignition pressure from agricultural burning and land clearing in surrounding landscapes.
Como&eacute; and W (Benin) show synchronized inside/outside timing but higher magnitude outside.
Forest-dominated or moist-transition parks (Bia, Bontioli) show little distinction between inside and
outside, since fire spread is ecologically constrained regardless of boundary position.</p>
{admon("tip", "What this means for management", "<p>Buffer zones in savanna parks are active ignition interfaces that need targeted, coordinated intervention &mdash; working with surrounding communities on early-season burn timing, rather than attempting exclusion, is the more realistic path to reducing uncontrolled fire spread into park interiors.</p>")}
</section>
"""


PAGE_BUILDERS = {
    "index.html": page_index,
    "study-design.html": page_study_design,
    "pipeline.html": page_pipeline,
    "script-reference.html": page_script_reference,
    "data-outputs.html": page_data_outputs,
    "findings.html": page_findings,
}

# =====================================================================
# SHELL RENDERING
# =====================================================================

PAGE_ORDER = [n for n, _ in NAV]


def sidebar_html(current):
    parts = ['<p class="side-group-label">Documentation</p><ul class="side-nav">']
    for fname, label in NAV:
        current_attr = ' aria-current="page"' if fname == current else ""
        parts.append(f'<li><a href="{fname}"{current_attr}>{label}</a></li>')
        if fname == current and PAGE_SECTIONS.get(fname):
            parts.append('<ul class="side-sub">')
            for sid, slabel in PAGE_SECTIONS[fname]:
                parts.append(f'<li><a href="#{sid}">{slabel}</a></li>')
            parts.append("</ul>")
    parts.append("</ul>")
    parts.append(f"""
<div class="repo-card">
  <a href="{REPO_URL}">{ICONS['github']} View on GitHub</a>
  <p>Static docs — no Jekyll, no build step. GitHub Pages serves <code>docs/</code> directly.</p>
</div>""")
    return "".join(parts)


def toc_html(current):
    secs = PAGE_SECTIONS.get(current, [])
    if not secs:
        return ""
    items = "".join(f'<li><a href="#{sid}">{slabel}</a></li>' for sid, slabel in secs)
    return f'<p class="toc-label">On this page</p><ol>{items}</ol>'


def prev_next(current):
    idx = PAGE_ORDER.index(current)
    parts = ['<div class="pagenav">']
    if idx > 0:
        pf = PAGE_ORDER[idx - 1]
        parts.append(f'<a class="prev" href="{pf}"><span class="dir">&larr; Previous</span><span class="lbl">{PAGE_META[pf][0]}</span></a>')
    else:
        parts.append("<span></span>")
    if idx < len(PAGE_ORDER) - 1:
        nf = PAGE_ORDER[idx + 1]
        parts.append(f'<a class="next" href="{nf}"><span class="dir">Next &rarr;</span><span class="lbl">{PAGE_META[nf][0]}</span></a>')
    parts.append("</div>")
    return "".join(parts)


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — fires-landuse-climate-interactions</title>
<meta name="description" content="{description}">
<link rel="icon" href="data:,">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<a class="skip" href="#content">Skip to content</a>

<header class="topbar">
  <div class="topbar-in">
    <button class="burger" aria-expanded="false" aria-label="Toggle navigation">{menu_icon}</button>
    <a class="site-title" href="index.html">
      <span class="mark">FLC</span>
      <span class="name">fires-landuse-climate-interactions<small>Documentation</small></span>
    </a>
    <div class="topbar-search">
      {search_icon}
      <input type="search" placeholder="Search the docs&hellip;" aria-label="Search the documentation">
      <div class="search-results"></div>
    </div>
    <div class="topbar-actions">
      <button class="icon-btn theme-toggle" aria-label="Toggle dark mode">{sun_icon}{moon_icon}</button>
      <a class="icon-btn" href="{repo_url}" aria-label="View source on GitHub">{github_icon}</a>
    </div>
  </div>
</header>
<div class="sidebar-scrim"></div>

<div class="shell">
  <aside class="sidebar" aria-label="Documentation">
    {sidebar}
  </aside>

  <main class="content" id="content">
    {body}
    {pagenav}
  </main>

  <aside class="toc" aria-label="On this page">
    {toc}
  </aside>
</div>

<footer class="foot">
  <div class="foot-in">
    <div>
      <h4>fires-landuse-climate-interactions</h4>
      <p>Documentation for a 20-year, 15-park fire regime analysis in West Africa, published in
      {journal}.</p>
    </div>
    <div>
      <h4>Site</h4>
      <ul>{footer_nav}</ul>
    </div>
    <div>
      <h4>Data sources</h4>
      <ul><li>MODIS MCD64A1 C6.1</li><li>GLAD GLCLU2020 v2</li><li>ESRI Global LULC 10m</li><li>ERA5-Land Monthly Aggregates</li></ul>
    </div>
    <div>
      <h4>Publication</h4>
      <ul><li><a href="{doi_url}">DOI: {doi}</a></li><li>{journal}</li></ul>
    </div>
  </div>
</footer>

<script src="assets/site.js"></script>
</body>
</html>
"""


def render_page(fname):
    title, description = PAGE_META[fname]
    body = PAGE_BUILDERS[fname]()
    footer_nav = "".join(f'<li><a href="{f}">{l}</a></li>' for f, l in NAV if f != fname)
    html = PAGE_TEMPLATE.format(
        title=title,
        description=description,
        menu_icon=ICONS["menu"],
        search_icon=ICONS["search"],
        sun_icon=ICONS["sun"],
        moon_icon=ICONS["moon"],
        github_icon=ICONS["github"],
        repo_url=REPO_URL,
        sidebar=sidebar_html(fname),
        body=body,
        pagenav=prev_next(fname),
        toc=toc_html(fname),
        footer_nav=footer_nav,
        journal=JOURNAL,
        doi_url=DOI_URL,
        doi=DOI,
    )
    return html


def build_search_index():
    index = []
    for fname, _ in NAV:
        title = PAGE_META[fname][0]
        for sid, slabel in PAGE_SECTIONS.get(fname, []):
            clean = re.sub("<[^>]+>", "", slabel)
            index.append({"page": fname, "pageTitle": title, "id": sid, "text": clean})
        index.append({"page": fname, "pageTitle": title, "id": "", "text": title})
    return index


def main():
    os.makedirs(DOCS, exist_ok=True)
    for fname, _ in NAV:
        html = render_page(fname)
        with open(os.path.join(DOCS, fname), "w", encoding="utf-8") as fh:
            fh.write(html)
        print("wrote", fname)

    with open(os.path.join(DOCS, "search-index.json"), "w", encoding="utf-8") as fh:
        json.dump(build_search_index(), fh, ensure_ascii=False, indent=0)
    print("wrote search-index.json")


if __name__ == "__main__":
    main()
