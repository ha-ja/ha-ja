#!/usr/bin/env python3
"""Generate an animated boot-sequence + matrix-rain SVG banner (CSS only, GitHub-safe).

usage: gen_matrix.py <dark|light> <out.svg>
"""
import random
import sys
from xml.sax.saxutils import escape

THEMES = {
    "dark": dict(
        bg="#020805", head="#e5ffe9", mid="#3ddc84", tail="#1f8f4e",
        vig="#000", vig_a=(.85, .55), title="#c8ffd8", sub="#3ddc84",
        boot="#9aa5a0", ok="#3ddc84", glow=4,
    ),
    "light": dict(
        bg="#f3faf5", head="#0b3d1f", mid="#1a7f37", tail="#6cc48a",
        vig="#f3faf5", vig_a=(.92, .7), title="#0b5d2a", sub="#1a7f37",
        boot="#57606a", ok="#1a7f37", glow=1.5,
    ),
}

W, H = 840, 220
FS = 16
COL_W = 15
TRAVEL_FROM = -380
TRAVEL_TO = H + 40
GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789<>/=+*{}$#"

BOOT = [
    ("", "ha-ja BIOS v1.0  ·  memory test 65536K OK"),
    ("", "booting kernel ..."),
    ("OK", "Mounted /home/ha-ja"),
    ("OK", "Started kotlin.service"),
    ("OK", "Started swift.service"),
    ("OK", "Started python.service"),
    ("OK", "Started bash.service"),
    ("OK", "Reached target matrix.target"),
    ("", "login: ha-ja"),
]
LINE_STEP = 0.32                      # seconds between boot lines
BOOT_END = len(BOOT) * LINE_STEP + 0.5  # when the boot screen fades out


def build(theme: str) -> str:
    t = THEMES[theme]
    random.seed(42)

    cols = []
    for i in range(W // COL_W + 1):
        x = i * COL_W + 4
        length = random.randint(6, 20)
        dur = round(random.uniform(3.5, 9.0), 2)
        delay = round(-random.uniform(0, dur), 2)
        chars = []
        for j in range(length):
            frac = (j + 1) / length
            if j == length - 1:
                fill, op = t["head"], 1.0
            else:
                fill = t["mid"] if frac > 0.6 else t["tail"]
                op = round(0.15 + 0.75 * frac, 2)
            cls = ' class="f"' if random.random() < 0.12 else ""
            chars.append(
                f'<text x="{x}" y="{j * FS}" fill="{fill}" opacity="{op}"{cls}>'
                f'{escape(random.choice(GLYPHS))}</text>'
            )
        cols.append(
            f'<g class="c" style="animation-duration:{dur}s;animation-delay:{delay}s">'
            + "".join(chars) + "</g>"
        )

    boot = []
    for i, (status, msg) in enumerate(BOOT):
        y = 26 + i * 21
        d = round(i * LINE_STEP, 2)
        if status:
            line = (f'<tspan fill="{t["boot"]}">[  </tspan><tspan fill="{t["ok"]}">OK</tspan>'
                    f'<tspan fill="{t["boot"]}">  ] {escape(msg)}</tspan>')
        else:
            line = f'<tspan fill="{t["boot"]}">{escape(msg)}</tspan>'
        boot.append(f'<text class="bl" x="20" y="{y}" style="animation-delay:{d}s">{line}</text>')

    va, vb = t["vig_a"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ha-ja">
<style>
  text {{ font-family: "JetBrains Mono", "SFMono-Regular", Menlo, Consolas, monospace; font-size: {FS}px; }}
  .c {{ animation-name: fall; animation-timing-function: linear; animation-iteration-count: infinite; }}
  @keyframes fall {{ from {{ transform: translateY({TRAVEL_FROM}px); }} to {{ transform: translateY({TRAVEL_TO}px); }} }}
  .f {{ animation: flick 1.3s steps(2) infinite; }}
  @keyframes flick {{ 50% {{ opacity: .1; }} }}
  .t {{ font-size: 64px; font-weight: 700; letter-spacing: 6px; }}
  .s {{ font-size: 16px; letter-spacing: 2px; }}
  .g1 {{ animation: g1 4s steps(1) {BOOT_END + 1.5}s infinite; opacity: 0; }}
  .g2 {{ animation: g2 4s steps(1) {BOOT_END + 1.5}s infinite; opacity: 0; }}
  @keyframes g1 {{ 0%,88%,100% {{ transform: translate(0,0); opacity: 0; }} 90% {{ transform: translate(-4px,1px); opacity: .8; }} 94% {{ transform: translate(3px,-2px); opacity: .8; }} }}
  @keyframes g2 {{ 0%,88%,100% {{ transform: translate(0,0); opacity: 0; }} 91% {{ transform: translate(4px,-1px); opacity: .8; }} 95% {{ transform: translate(-3px,2px); opacity: .8; }} }}
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  /* boot sequence: lines pop in one by one, then the screen clears */
  .bl {{ font-size: 14px; animation: on .01s linear both; }}
  @keyframes on {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  .boot {{ animation: off .35s ease-in {BOOT_END}s both; }}
  @keyframes off {{ from {{ opacity: 1; }} to {{ opacity: 0; }} }}
  .main {{ animation: in .9s ease-out {BOOT_END + 0.2}s both; }}
  @keyframes in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
</style>
<defs>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="{t["glow"]}" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="vig" cx="50%" cy="50%" r="60%">
    <stop offset="0%" stop-color="{t["vig"]}" stop-opacity="{va}"/>
    <stop offset="45%" stop-color="{t["vig"]}" stop-opacity="{vb}"/>
    <stop offset="100%" stop-color="{t["vig"]}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="100%" height="100%" fill="{t["bg"]}" rx="8"/>
<g class="boot">{"".join(boot)}</g>
<g class="main">
<g>{"".join(cols)}</g>
<ellipse cx="{W/2}" cy="{H/2}" rx="300" ry="85" fill="url(#vig)"/>
<g text-anchor="middle">
  <text class="t g1" x="{W/2}" y="{H/2 + 14}" fill="#ff2a6d">ha-ja</text>
  <text class="t g2" x="{W/2}" y="{H/2 + 14}" fill="#00b8d4">ha-ja</text>
  <text class="t" x="{W/2}" y="{H/2 + 14}" fill="{t["title"]}" filter="url(#glow)">ha-ja</text>
  <text class="s" x="{W/2}" y="{H/2 + 48}" fill="{t["sub"]}">&gt; system online<tspan class="cur">_</tspan></text>
</g>
</g>
</svg>
'''


if __name__ == "__main__":
    theme, out = sys.argv[1], sys.argv[2]
    svg = build(theme)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {out} ({theme}): {len(svg.encode())/1024:.1f} KB")
