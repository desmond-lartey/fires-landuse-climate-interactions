"""Emit static HTML fragments (fire-season calendar + study-area table)."""
import json

# Figure 3: average monthly burned area as % of protected-area extent, 2004-2024
DATA = [
    # display name, ORIG_NAME note, zone code, Oct, Nov, Dec, Jan, Feb, Mar
    ("Mole",                 "GH", "ns", [0.01,  7.15, 57.35, 10.33, 1.35, 0.14]),
    ("Parc national de la Comoé", "CI", "ns", [0.02,  7.15, 51.23,  7.57, 0.71, 0.10]),
    ("Kogyae",               "GH", "st", [0.00,  0.21, 12.05, 41.96, 7.28, 0.25]),
    ("Parc National du W",   "BF", "ns", [4.73, 39.94, 17.24,  2.99, 1.43, 0.74]),
    ("W (Benin)",            "BJ", "ns", [1.82, 19.65, 22.46,  7.54, 4.40, 1.67]),
    ("Parc National de Pô dit Kaboré Tambi", "BF", "ns", [2.20, 23.43, 11.04, 3.61, 2.15, 0.45]),
    ("Kainji Lake",          "NG", "ns", [0.00, 10.29, 18.57, 16.06, 3.19, 0.06]),
    ("Old Oyo",              "NG", "st", [0.00,  0.12,  6.87, 14.02, 4.79, 0.00]),
    ("Kyabobo",              "GH", "st", [0.02,  0.19,  7.87, 10.40, 3.95, 0.65]),
    ("Forêt Classée et Réserve Totale de faune de Bontioli", "BF", "nf", [3.82, 6.60, 5.59, 0.84, 0.23, 0.00]),
    ("Gashaka-Gumti",        "NG", "st", [0.02,  3.93,  4.98,  2.15, 1.82, 0.28]),
    ("Forêt Classée et Réserve Partielle de Faune de Bontioli", "BF", "ns", [0.75, 7.17, 1.58, 0.12, 0.01, 0.00]),
    ("Forêt Classée de Tiogo", "BF", "ns", [7.82, 2.62, 1.32, 0.09, 0.08, 0.00]),
    ("Parc national de la Marahoué", "CI", "st", [0.00, 0.51, 0.96, 0.52, 0.14, 0.03]),
    ("Bia National Park",    "GH", "sf", [0.00,  0.00,  0.00,  0.00, 0.00, 0.00]),
]

MONTHS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
VMAX = 61.0

# ramp stops derived from the study's own dictionaries:
# paper -> ESRI Crops -> MODIS burn ramp
STOPS = [
    (0.00, (0xF8, 0xF6, 0xF2)),
    (0.22, (0xFF, 0xDB, 0x5C)),
    (0.55, (0xFF, 0x19, 0x01)),
    (0.76, (0xC6, 0x15, 0x03)),
    (1.00, (0x4E, 0x04, 0x00)),
]


def ramp(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(STOPS) - 1):
        a, ca = STOPS[i]
        b, cb = STOPS[i + 1]
        if a <= t <= b:
            f = 0 if b == a else (t - a) / (b - a)
            return tuple(round(ca[j] + (cb[j] - ca[j]) * f) for j in range(3))
    return STOPS[-1][1]


def hexof(rgb):
    return "#%02X%02X%02X" % rgb


def luminance(rgb):
    r, g, b = [c / 255 for c in rgb]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


rows = []
for name, cc, zone, vals in DATA:
    cells = []
    for v in vals:
        t = (v / VMAX) ** 0.5 if v > 0 else 0.0
        rgb = ramp(t)
        fg = "#F1ECE6" if luminance(rgb) < 0.42 else "#2A211C"
        label = "0" if v == 0 else ("%.2f" % v)
        cells.append(
            '        <td class="v" style="background:%s;color:%s">%s</td>'
            % (hexof(rgb), fg, label)
        )
    rows.append(
        '      <tr>\n        <td class="park">%s<em>%s</em></td>\n%s\n      </tr>'
        % (name, cc, "\n".join(cells))
    )

cal = """    <thead>
      <tr>
        <th class="park" scope="col">Protected area</th>
%s
      </tr>
    </thead>
    <tbody>
%s
    </tbody>""" % (
    "\n".join('        <th scope="col">%s</th>' % m for m in MONTHS),
    "\n".join(rows),
)

with open("/home/claude/site/_calendar.html", "w") as fh:
    fh.write(cal)

print(cal[:900])
print("...\nrows:", len(rows))
