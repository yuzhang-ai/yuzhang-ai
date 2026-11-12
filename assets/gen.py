#!/usr/bin/env python3
"""Generate the animated header SVGs for the GitHub profile README (light + dark).

Pure SVG + SMIL, no scripts, no external fonts (GitHub serves README images through
camo as <img>, so only SMIL/CSS animation inside the file runs). Typing is done with a
clip-path whose width animates per phrase; the typed line is monospace so the clip
width tracks the glyphs.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent
W, H = 900, 230

PHRASES = [
    "AI-augmented product manager",
    "writes skills that teach coding agents taste",
    "ships an AI daily brief, every morning",
    "stay hungry, stay foolish",
]
FS = 21            # typed line font size
CW = FS * 0.602    # monospace advance ≈ 0.6em (Menlo / SF Mono / Consolas)
X0 = 72            # left margin
TYPE_PER_CHAR, HOLD, ERASE, GAP = 0.055, 1.9, 0.45, 0.55

THEMES = {
    "light": dict(bg="#fffaf0", ink="#2e2a27", muted="#62594e", gold="#b49367", rule="#e7dcc6", noise=0.035),
    "dark": dict(bg="#1b1915", ink="#f3ecdf", muted="#a89e8e", gold="#c9a86d", rule="#3a342b", noise=0.05),
}


def f(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def timeline():
    """Per phrase: (start, typed, held, erased, end) in seconds, plus total cycle length."""
    t, segs = 0.0, []
    for p in PHRASES:
        a = t
        b = a + len(p) * TYPE_PER_CHAR
        c = b + HOLD
        d = c + ERASE
        e = d + GAP
        segs.append((a, b, c, d, e))
        t = e
    return segs, t


def build(theme):
    c = THEMES[theme]
    segs, total = timeline()
    y_typed = 158
    parts = []
    defs = []
    for i, (p, (a, b, cc, d, e)) in enumerate(zip(PHRASES, segs)):
        w = len(p) * CW
        kt = [0, a / total, b / total, cc / total, d / total, 1]
        kt = ";".join(f(k) for k in kt)
        vals_w = f"0;0;{f(w)};{f(w)};0;0"
        defs.append(
            f'<clipPath id="c{i}"><rect x="{X0}" y="{y_typed - FS}" height="{FS * 1.5:.0f}" width="0">'
            f'<animate attributeName="width" values="{vals_w}" keyTimes="{kt}" dur="{f(total)}s" '
            f'calcMode="linear" repeatCount="indefinite"/></rect></clipPath>'
        )
        parts.append(
            f'<text class="typed" x="{X0}" y="{y_typed}" clip-path="url(#c{i})">{p}</text>'
        )
        # caret follows the typed edge, visible only inside this phrase's window
        vals_x = f"{f(X0)};{f(X0)};{f(X0 + w + 3)};{f(X0 + w + 3)};{f(X0)};{f(X0)}"
        vis = ";".join(["0", "1", "1", "1", "0", "0"])
        kt_vis = ";".join(f(k) for k in [0, a / total, b / total, cc / total, (d - 0.001) / total, 1])
        parts.append(
            f'<rect class="caret" x="{X0}" y="{y_typed - FS + 2}" width="2" height="{FS + 4}" opacity="0">'
            f'<animate attributeName="x" values="{vals_x}" keyTimes="{kt}" dur="{f(total)}s" calcMode="linear" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{vis}" keyTimes="{kt_vis}" dur="{f(total)}s" calcMode="discrete" repeatCount="indefinite"/>'
            f'</rect>'
        )
    # idle caret blinks at the left edge during the gaps between phrases
    gap_vals, gap_kt = ["0"], ["0"]
    for (a, b, cc, d, e) in segs:
        gap_vals += ["1", "0"]
        gap_kt += [f(d / total), f(e / total)]
    gap_kt[-1] = "1"
    idle = (
        f'<rect class="caret" x="{X0}" y="{y_typed - FS + 2}" width="2" height="{FS + 4}" opacity="0">'
        f'<animate attributeName="opacity" values="{";".join(gap_vals)}" keyTimes="{";".join(gap_kt)}" '
        f'dur="{f(total)}s" calcMode="discrete" repeatCount="indefinite"/>'
        f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="张禹 Yu Zhang — AI-augmented product manager">
<style>
  .name {{ font: 600 44px/1 Georgia, "Iowan Old Style", "Songti SC", "Noto Serif CJK SC", "Source Han Serif SC", serif; fill: {c["ink"]}; letter-spacing: .5px; }}
  .latin {{ font: 400 22px/1 Georgia, "Iowan Old Style", serif; fill: {c["muted"]}; letter-spacing: 1.5px; }}
  .typed {{ font: 400 {FS}px/1 ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; fill: {c["ink"]}; }}
  .meta {{ font: 400 13px/1 ui-monospace, "SF Mono", Menlo, Consolas, monospace; fill: {c["muted"]}; letter-spacing: .6px; }}
  .caret {{ fill: {c["gold"]}; }}
  .prompt {{ font: 400 {FS}px/1 ui-monospace, "SF Mono", Menlo, Consolas, monospace; fill: {c["gold"]}; }}
</style>
<defs>
  <filter id="paper" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 {c["noise"]} 0"/>
  </filter>
  <linearGradient id="rule" gradientUnits="userSpaceOnUse" x1="{X0}" x2="{X0 + 420}" y1="0" y2="0">
    <stop offset="0" stop-color="{c["gold"]}"/>
    <stop offset=".7" stop-color="{c["gold"]}"/>
    <stop offset="1" stop-color="{c["gold"]}" stop-opacity="0"/>
  </linearGradient>
  {"".join(defs)}
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{c["bg"]}"/>
<rect width="{W}" height="{H}" rx="14" filter="url(#paper)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="13.5" fill="none" stroke="{c["rule"]}"/>

<g opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur=".9s" begin=".1s" fill="freeze"/>
  <text class="name" x="{X0}" y="86">张禹</text>
  <text class="latin" x="{X0 + 118}" y="86">Yu Zhang</text>
</g>
<rect x="{X0}" y="105" width="0" height="1.5" fill="url(#rule)">
  <animate attributeName="width" from="0" to="420" dur="1.1s" begin=".5s" fill="freeze" calcMode="spline" keySplines=".2 .7 .2 1"/>
</rect>

<g opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur=".6s" begin="1.3s" fill="freeze"/>
  <text class="prompt" x="{X0 - 22}" y="{y_typed}">›</text>
  {"".join(parts)}
  {idle}
</g>

<g opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur=".8s" begin="1.8s" fill="freeze"/>
  <text class="meta" x="{X0}" y="{H - 30}">Beijing · oaioil.cn · yuzhang-ai.github.io/ai-daily</text>
</g>
</svg>
'''
    return svg


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for t in THEMES:
        p = OUT / f"header-{t}.svg"
        p.write_text(build(t), encoding="utf-8")
        print(p, p.stat().st_size, "bytes; cycle", f(timeline()[1]), "s")
