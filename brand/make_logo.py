"""Build the Lumaube logo SVGs (wordmark converted to paths, no font needed)."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT = "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf"
INK, DAWN, HONEY, CREAM = "#1E2238", "#F08A5D", "#F7C873", "#FBF6EE"

def text_path(text, size, tracking=0.04):
    f = TTFont(FONT)
    cmap, gs = f.getBestCmap(), f.getGlyphSet()
    upm = f["head"].unitsPerEm
    scale = size / upm
    hmtx = f["hmtx"]
    x, d = 0.0, []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        d.append(pen.getCommands())
        x += hmtx[g][0] * scale + size * tracking
    return " ".join(d), x - size * tracking

def icon(cx, cy, r, ink=INK):
    """Rising sun over a horizon: half disc + 5 rays + horizon line."""
    rays = []
    import math
    for a in (-150, -120, -90, -60, -30):
        t = math.radians(a)
        x1, y1 = cx + math.cos(t) * r * 1.32, cy + math.sin(t) * r * 1.32
        x2, y2 = cx + math.cos(t) * r * 1.62, cy + math.sin(t) * r * 1.62
        rays.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="url(#lmb-g)" stroke-width="{r*0.16:.1f}" stroke-linecap="round"/>')
    return (f'<path d="M{cx-r:.1f} {cy:.1f} A{r:.1f} {r:.1f} 0 0 1 {cx+r:.1f} {cy:.1f} Z" fill="url(#lmb-g)"/>'
            + "".join(rays)
            + f'<line x1="{cx-r*1.75:.1f}" y1="{cy+r*0.02:.1f}" x2="{cx+r*1.75:.1f}" y2="{cy+r*0.02:.1f}" stroke="{ink}" stroke-width="{r*0.12:.1f}" stroke-linecap="round"/>')

GRAD = (f'<defs><linearGradient id="lmb-g" x1="0" y1="1" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{DAWN}"/><stop offset="1" stop-color="{HONEY}"/></linearGradient></defs>')

def horizontal(ink=INK, name="logo.svg"):
    d, w = text_path("lumaube", 64)
    r = 26
    W, H = int(110 + w + 10), 96
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Lumaube">'
           f'<title>Lumaube</title>{GRAD}{icon(50, 62, r, ink)}'
           f'<path transform="translate(104 62)" fill="{ink}" d="{d}"/></svg>')
    open(name, "w").write(svg)
    return name

def square(bg=CREAM, name="logo-icon.svg"):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Lumaube">'
           f'<title>Lumaube</title>{GRAD}<rect width="512" height="512" rx="112" fill="{bg}"/>{icon(256, 344, 120)}</svg>')
    open(name, "w").write(svg)

horizontal()
horizontal(ink=CREAM, name="logo-white.svg")
square()
square(bg=INK, name="logo-icon-dark.svg")
print("ok")
