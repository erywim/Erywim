#!/usr/bin/env python3
"""从 tech-stack.json 生成 Profile README 的浅色/深色 Hero。"""

import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "tech-stack.json")
OUT = os.path.join(ROOT, "assets")

WIDTH = 840
HEIGHT = 220

DISPLAY_FONT = "'Avenir Next', 'Futura', 'Helvetica Neue', Arial, sans-serif"
CJK_FONT = (
    "'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC', "
    "'Microsoft YaHei', sans-serif"
)

THEMES = {
    "light": {
        "bg": "#F3E9CE",
        "grid": "#D6C8A7",
        "ink": "#1C2340",
        "muted": "#63523F",
        "border": "#1C2340",
        "accent": "#B64235",
        "route": "#2F7F78",
        "slime": "#3C9C91",
        "gold": "#A77A2A",
        "highlight": "#FFF9EA",
    },
    "dark": {
        "bg": "#12172A",
        "grid": "#27324B",
        "ink": "#F4EAD2",
        "muted": "#B9B5A9",
        "border": "#42536F",
        "accent": "#FF7A5C",
        "route": "#7AD9D0",
        "slime": "#67C9BC",
        "gold": "#E9B45E",
        "highlight": "#12172A",
    },
}

# 8-bit 史莱姆：X 为身体，E 为眼睛，W 为高光。
SLIME = [
    "..XXXX....",
    ".XXXXXX...",
    "XXXXXXXX..",
    "XXEXXEXX..",
    "XXXWXXXX..",
    "XXXEEXXX..",
    ".XXXXXX...",
    "..XXXX....",
]


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def pixel_slime(x, y, scale, colors):
    parts = []
    for row, cells in enumerate(SLIME):
        for col, cell in enumerate(cells):
            if cell == ".":
                continue
            fill = {
                "X": colors["slime"],
                "E": colors["ink"],
                "W": colors["highlight"],
            }[cell]
            parts.append(
                f'<rect x="{x + col * scale}" y="{y + row * scale}" '
                f'width="{scale}" height="{scale}" fill="{fill}"/>'
            )
    return "".join(parts)


def svg_header(profile, theme_name, colors):
    name = esc(profile["name"])
    role = esc(profile["role"])
    title = f"{name} — {role}"
    desc = (
        f"{name}，{role}。个人档案横幅，右侧是一条从像素史莱姆出发、"
        "经过四个节点抵达终点旗帜的冒险路线。"
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(desc)}</desc>
  <defs>
    <pattern id="dot-grid-{theme_name}" width="14" height="14" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1" fill="{colors['grid']}" opacity="0.62"/>
    </pattern>
  </defs>
  <rect x="1.5" y="1.5" width="837" height="217" rx="8" fill="{colors['bg']}"/>
  <rect x="1.5" y="1.5" width="837" height="217" rx="8" fill="url(#dot-grid-{theme_name})"/>
  <rect x="1.5" y="1.5" width="837" height="217" rx="8" fill="none" stroke="{colors['border']}" stroke-width="3"/>
  <path d="M22 1.5H818M22 218.5H818" stroke="{colors['border']}" stroke-width="1" opacity="0.16"/>
  <rect x="31" y="34" width="8" height="8" fill="{colors['accent']}"/>
  <rect x="44" y="34" width="8" height="8" fill="{colors['route']}" opacity="0.72"/>
  <rect x="57" y="34" width="8" height="8" fill="{colors['gold']}" opacity="0.72"/>
  <path d="M782 38h25M794.5 25.5v25" stroke="{colors['border']}" stroke-width="1" opacity="0.55"/>
  <circle cx="794.5" cy="38" r="2.5" fill="{colors['accent']}"/>
  <text x="31" y="127" fill="{colors['ink']}" font-family="{DISPLAY_FONT}" font-size="82" font-weight="800" letter-spacing="1.6">{name}</text>
  <rect x="33" y="145" width="52" height="4" fill="{colors['accent']}"/>
  <text x="33" y="181" fill="{colors['ink']}" font-family="{CJK_FONT}" font-size="40" font-weight="600" letter-spacing="0.7">{role}</text>
  <g fill="none" stroke="{colors['border']}" stroke-width="1" opacity="0.5">
    <path d="M31 192h64M43 186v12M763 46h44M785 34v24"/>
  </g>
  <g opacity="0.88">
    <path d="M553 163 C583 155 584 133 613 126 S655 101 686 109 S724 114 742 84" fill="none" stroke="{colors['route']}" stroke-width="4" stroke-linecap="round" stroke-dasharray="2 9"/>
    <circle cx="613" cy="126" r="6" fill="{colors['bg']}" stroke="{colors['route']}" stroke-width="3"/>
    <circle cx="654" cy="103" r="6" fill="{colors['bg']}" stroke="{colors['route']}" stroke-width="3"/>
    <circle cx="696" cy="112" r="6" fill="{colors['bg']}" stroke="{colors['route']}" stroke-width="3"/>
    <circle cx="742" cy="84" r="8" fill="{colors['bg']}" stroke="{colors['accent']}" stroke-width="3"/>
    <path d="M742 84V59" stroke="{colors['accent']}" stroke-width="3" stroke-linecap="square"/>
    <path d="M746 60h19l-6 7 6 7h-19z" fill="{colors['accent']}"/>
    <path d="M535 90l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill="{colors['gold']}" opacity="0.9"/>
    <path d="M773 151l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" fill="{colors['route']}" opacity="0.7"/>
    <path d="M520 61h17M528.5 52.5v17" stroke="{colors['border']}" stroke-width="1" opacity="0.42"/>
    <path d="M775 174h24M787 162v24" stroke="{colors['border']}" stroke-width="1" opacity="0.42"/>
  </g>
  <g shape-rendering="crispEdges">{pixel_slime(522, 158, 3, colors)}</g>
</svg>
"""


def main():
    with open(DATA, encoding="utf-8") as source:
        data = json.load(source)

    profile = data["profile"]
    os.makedirs(OUT, exist_ok=True)
    for theme_name, colors in THEMES.items():
        path = os.path.join(OUT, f"hero-{theme_name}.svg")
        with open(path, "w", encoding="utf-8") as output:
            output.write(svg_header(profile, theme_name, colors))
        print(f"generated {path}")


if __name__ == "__main__":
    main()
