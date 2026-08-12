#!/usr/bin/env python3
"""
生成 assets/hero.svg + assets/card-*.svg —— 像素风（日式 RPG UI）自动排版。

用法：
    python3 scripts/generate.py

流程：
    1. 编辑根目录的 tech-stack.json（改/加标签只动这里）
    2. 跑一次本脚本，自动重新生成 4 张卡片 SVG
    3. git add 提交即可

tech-stack.json 结构（每张卡片一个对象，可多张）：
    {
      "fullstack": {                     // key 决定输出文件名 card-<key>.svg
        "rail":  "FS",                   // 左侧导轨大字（取代 L1/L2...）
        "title": "全栈 · Fullstack",      // 卡片主标题（手写体）
        "en":    "Fullstack",            // 右上角英文小字（空字符串则不显示）
        "accent":"#4FA39A",              // 导轨圆点 / 小字颜色
        "icon":  "star",                 // 导轨像素图标: chip | star | db | heart
        "blocks":[
          { "label":"后端 · Backend", "color":"#4FA39A", "fill":"#F1F9EF", "tags":["Java", ...] },
          { "label":"", "highlight":true, "color":"#E85D4A", "fill":"#FFF1F1", "tags":["..."] },   // highlight 用红色描边
          { "note":"📖 研读 ...", "color":"#F5A623" }                                              // note 块渲染成整条横幅
        ]
      }
    }

像素风配色（深色日式 RPG UI）：
    边框 #0A0E18 · 面板 #1F2A44 · 面板高光/导轨 #2A3A5E · 标签底 #26345A
    主文字 #F5EFE0 · 次要文字 #A8B4D0 · 强调色沿用蜡笔色（红/橙/黄/绿/青/蓝/紫/粉）
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "tech-stack.json")
OUT = os.path.join(ROOT, "assets")

# ── 像素风（日式 RPG UI）配色与字体 ──
PX_FONT = "'Monaco','Menlo','Consolas','Courier New','Andale Mono',monospace"
FRAME = "#0A0E18"    # 面板黑色像素边框
PANEL = "#1F2A44"    # 深蓝面板
RAIL  = "#2A3A5E"    # 面板内浅一档的蓝色（导轨 / 顶部高光条）
CHIP  = "#26345A"    # 标签底色
TXT   = "#F5EFE0"    # 主文字（米白）
TXT2  = "#A8B4D0"    # 次要文字（浅蓝灰）

ROW = 36                                     # 行距
Y0 = 100                                     # 第一行中心 y
MAX_RIGHT = 798                              # 标签最右边界（卡片 860 宽）


def PX(s):
    """像素风文字：拉丁字母大写（中文不受影响）。"""
    return s.upper()

# 像素图标：{(r, c) 填充格}，6 列宽，每格 4px
PIXEL = {
    "chip":  { "#4FA39A": {(0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 5),
                           (2, 0), (2, 2), (2, 3), (2, 5), (3, 0), (3, 2), (3, 3), (3, 5),
                           (4, 0), (4, 5), (5, 1), (5, 2), (5, 3), (5, 4)} },
    "star":  { "#FFD166": {(0, 2), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                           (3, 1), (3, 2), (3, 3), (4, 2)} },
    "db":    { "#6BA368": {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
                           (1, 0), (1, 5), (2, 0), (2, 5),
                           (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
                           (4, 1), (4, 2), (4, 3), (4, 4), (5, 1), (5, 2), (5, 3), (5, 4)} },
    "heart": { "#E85D4A": {(0, 1), (0, 2), (0, 4), (0, 5),
                           (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
                           (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
                           (3, 1), (3, 2), (3, 3), (3, 4), (4, 2), (4, 3)} },
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def is_cjk(ch):
    o = ord(ch)
    return (0x2E80 <= o <= 0x9FFF) or (0xF900 <= o <= 0xFAFF) or (0x20000 <= o <= 0x2FA1F)


def is_emoji(ch):
    o = ord(ch)
    return (0x1F000 <= o <= 0x1FAFF) or (0x2600 <= o <= 0x27BF) or (0x2300 <= o <= 0x23FF) or (0x2B00 <= o <= 0x2BFF)


def text_w(s, size):
    """估算等宽字体文本宽度：CJK ≈ 1em，emoji ≈ 1.2em，其余字符（含空格）≈ 0.62em。"""
    w = 0.0
    for ch in s:
        if is_cjk(ch):
            w += size
        elif is_emoji(ch):
            w += size * 1.2
        else:
            w += size * 0.62
    return w


def chip_size(tag):
    """按长度选字号，返回 (font_size, chip_width)。"""
    size, w = 13, text_w(tag, 13) + 30
    if w > 210:
        size, w = 11.5, text_w(tag, size) + 28
    elif w > 168:
        size, w = 12, text_w(tag, size) + 28
    return size, w


def chip(x, y, tag):
    """像素风标签：深底 + 黑色像素边框 + 米白等宽文字，无圆角无旋转。"""
    size, w = chip_size(tag)
    cx = x + w / 2
    by = y + size * 0.35
    return (f'<g>'
            f'<rect x="{x:.0f}" y="{y - 14}" width="{w:.0f}" height="28" '
            f'fill="{CHIP}" stroke="{FRAME}" stroke-width="2"/>'
            f'<text x="{cx:.0f}" y="{by:.1f}" text-anchor="middle" font-size="{size}" '
            f'fill="{TXT}" font-family="{PX_FONT}">{esc(PX(tag))}</text></g>')


def note_bar(y, text, color):
    return (f'<g>'
            f'<rect x="80" y="{y - 15}" width="680" height="34" '
            f'fill="{RAIL}" stroke="{FRAME}" stroke-width="2"/>'
            f'<text x="420" y="{y + 4}" text-anchor="middle" font-size="13" '
            f'fill="{TXT}" font-family="{PX_FONT}">{esc(PX(text))}</text></g>')


def pixel(icon, ox=28, oy=96):
    parts = []
    for color, cells in icon.items():
        for (r, c) in cells:
            parts.append(f'<rect x="{ox + c * 4}" y="{oy + r * 4}" width="4" height="4" fill="{color}"/>')
    return "".join(parts)


def gen_card(rail_label, cfg):
    title = cfg["title"]
    en = cfg.get("en", "")
    accent = cfg.get("accent", "#4FA39A")
    icon = PIXEL[cfg.get("icon", "chip")]
    blocks = cfg["blocks"]

    frags = []
    y = Y0
    for blk in blocks:
        if "note" in blk:
            frags.append(note_bar(y, blk["note"], blk.get("color", "#F5A623")))
            y += ROW
            continue
        label = blk.get("label", "")
        tags = blk.get("tags", [])
        color = blk.get("color", "#4FA39A")
        if label:
            lbl = PX(label)
            frags.append(f'<text x="80" y="{y + 5}" font-size="13" font-weight="bold" '
                         f'fill="{color}" font-family="{PX_FONT}">{esc(lbl)}</text>')
            start_x = max(168, 82 + text_w(lbl, 13) + 16)
        else:
            start_x = 80
        x = start_x
        for tag in tags:
            size, w = chip_size(tag)
            if x + w > MAX_RIGHT:
                y += ROW
                x = start_x
            frags.append(chip(x, y, tag))
            x += w + 12
        y += ROW

    h = (y - ROW) + 46
    rail_from = min(120, h - 30)
    rail_to = h - 24

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{h}" viewBox="0 0 860 {h}">')
    # 深色像素面板：黑色外框 + 深蓝面板 + 顶部高光条 + 内框线
    out.append(f'<rect x="0" y="0" width="860" height="{h}" fill="{FRAME}"/>')
    out.append(f'<rect x="3" y="3" width="854" height="{h - 6}" fill="{PANEL}"/>')
    out.append(f'<rect x="3" y="3" width="854" height="4" fill="{RAIL}"/>')
    out.append(f'<rect x="6" y="6" width="848" height="{h - 12}" fill="none" stroke="{FRAME}" stroke-width="1"/>')
    # 导轨
    out.append(f'<rect x="38" y="28" width="5" height="5" fill="{accent}"/>')
    out.append(f'<text x="44" y="72" font-size="26" font-family="{PX_FONT}" font-weight="bold" '
               f'fill="{accent}">{rail_label}</text>')
    out.append(f'<g shape-rendering="crispEdges">{pixel(icon)}</g>')
    out.append(f'<rect x="57" y="120" width="3" height="{rail_to - 120}" fill="{RAIL}"/>')
    # 标题
    out.append(f'<text x="80" y="50" font-size="22" font-family="{PX_FONT}" font-weight="bold" '
               f'fill="{TXT}">{esc(PX(title))}</text>')
    if en:
        out.append(f'<text x="730" y="46" font-size="14" font-family="{PX_FONT}" font-weight="bold" '
                   f'fill="{accent}">{esc(PX(en))}</text>')
    out.extend(frags)
    out.append("</svg>")
    return "\n".join(out)


# ─────────────────────────── HERO 生成 ───────────────────────────
# 装饰层（像素画 / 外框 / 云朵 / 星星 / 螺旋）是固定模板，文字从 hero 数据读取。

HERO_DEFS = """  <defs>
    <g id="bot">
      <g shape-rendering="crispEdges">
        <rect x="62" y="52" width="6" height="6" fill="#4FA39A"/><rect x="74" y="52" width="6" height="6" fill="#4FA39A"/>
        <rect x="62" y="58" width="6" height="6" fill="#4FA39A"/><rect x="74" y="58" width="6" height="6" fill="#4FA39A"/>
        <rect x="56" y="64" width="6" height="6" fill="#4FA39A"/><rect x="62" y="64" width="6" height="6" fill="#4FA39A"/><rect x="68" y="64" width="6" height="6" fill="#4FA39A"/><rect x="74" y="64" width="6" height="6" fill="#4FA39A"/><rect x="80" y="64" width="6" height="6" fill="#4FA39A"/>
        <rect x="50" y="70" width="6" height="6" fill="#4FA39A"/><rect x="56" y="70" width="6" height="6" fill="#4FA39A"/><rect x="62" y="70" width="6" height="6" fill="#4FA39A"/><rect x="68" y="70" width="6" height="6" fill="#4FA39A"/><rect x="74" y="70" width="6" height="6" fill="#4FA39A"/><rect x="80" y="70" width="6" height="6" fill="#4FA39A"/><rect x="86" y="70" width="6" height="6" fill="#4FA39A"/>
        <rect x="44" y="76" width="6" height="6" fill="#4FA39A"/><rect x="50" y="76" width="6" height="6" fill="#4FA39A"/><rect x="56" y="76" width="6" height="6" fill="#FFFFFF"/><rect x="62" y="76" width="6" height="6" fill="#4FA39A"/><rect x="68" y="76" width="6" height="6" fill="#4FA39A"/><rect x="74" y="76" width="6" height="6" fill="#4FA39A"/><rect x="80" y="76" width="6" height="6" fill="#FFFFFF"/><rect x="86" y="76" width="6" height="6" fill="#4FA39A"/><rect x="92" y="76" width="6" height="6" fill="#4FA39A"/>
        <rect x="44" y="82" width="6" height="6" fill="#4FA39A"/><rect x="50" y="82" width="6" height="6" fill="#4FA39A"/><rect x="56" y="82" width="6" height="6" fill="#4FA39A"/><rect x="62" y="82" width="6" height="6" fill="#4FA39A"/><rect x="68" y="82" width="6" height="6" fill="#4FA39A"/><rect x="74" y="82" width="6" height="6" fill="#4FA39A"/><rect x="80" y="82" width="6" height="6" fill="#4FA39A"/><rect x="86" y="82" width="6" height="6" fill="#4FA39A"/><rect x="92" y="82" width="6" height="6" fill="#4FA39A"/>
        <rect x="50" y="88" width="6" height="6" fill="#4FA39A"/><rect x="56" y="88" width="6" height="6" fill="#4FA39A"/><rect x="62" y="88" width="6" height="6" fill="#4FA39A"/><rect x="68" y="88" width="6" height="6" fill="#4FA39A"/><rect x="74" y="88" width="6" height="6" fill="#4FA39A"/><rect x="80" y="88" width="6" height="6" fill="#4FA39A"/><rect x="86" y="88" width="6" height="6" fill="#4FA39A"/>
        <rect x="44" y="94" width="6" height="6" fill="#4FA39A"/><rect x="62" y="94" width="6" height="6" fill="#4FA39A"/><rect x="68" y="94" width="6" height="6" fill="#4FA39A"/><rect x="74" y="94" width="6" height="6" fill="#4FA39A"/><rect x="92" y="94" width="6" height="6" fill="#4FA39A"/>
        <rect x="50" y="100" width="6" height="6" fill="#4FA39A"/><rect x="56" y="100" width="6" height="6" fill="#4FA39A"/><rect x="62" y="100" width="6" height="6" fill="#4FA39A"/><rect x="68" y="100" width="6" height="6" fill="#4FA39A"/><rect x="74" y="100" width="6" height="6" fill="#4FA39A"/><rect x="80" y="100" width="6" height="6" fill="#4FA39A"/><rect x="86" y="100" width="6" height="6" fill="#4FA39A"/>
      </g>
    </g>
    <g id="rocket">
      <g shape-rendering="crispEdges">
        <rect x="678" y="64" width="6" height="6" fill="#E85D4A"/><rect x="684" y="64" width="6" height="6" fill="#E85D4A"/>
        <rect x="672" y="70" width="6" height="6" fill="#E85D4A"/><rect x="678" y="70" width="6" height="6" fill="#E85D4A"/><rect x="684" y="70" width="6" height="6" fill="#E85D4A"/><rect x="690" y="70" width="6" height="6" fill="#E85D4A"/>
        <rect x="666" y="76" width="6" height="6" fill="#E85D4A"/><rect x="672" y="76" width="6" height="6" fill="#E85D4A"/><rect x="678" y="76" width="6" height="6" fill="#E85D4A"/><rect x="684" y="76" width="6" height="6" fill="#E85D4A"/><rect x="690" y="76" width="6" height="6" fill="#E85D4A"/><rect x="696" y="76" width="6" height="6" fill="#E85D4A"/>
        <rect x="666" y="82" width="6" height="6" fill="#E85D4A"/><rect x="672" y="82" width="6" height="6" fill="#FFFFFF"/><rect x="678" y="82" width="6" height="6" fill="#FFFFFF"/><rect x="684" y="82" width="6" height="6" fill="#FFFFFF"/><rect x="690" y="82" width="6" height="6" fill="#FFFFFF"/><rect x="696" y="82" width="6" height="6" fill="#E85D4A"/>
        <rect x="666" y="88" width="6" height="6" fill="#E85D4A"/><rect x="672" y="88" width="6" height="6" fill="#E85D4A"/><rect x="678" y="88" width="6" height="6" fill="#E85D4A"/><rect x="684" y="88" width="6" height="6" fill="#E85D4A"/><rect x="690" y="88" width="6" height="6" fill="#E85D4A"/><rect x="696" y="88" width="6" height="6" fill="#E85D4A"/>
        <rect x="666" y="94" width="6" height="6" fill="#E85D4A"/><rect x="678" y="94" width="6" height="6" fill="#E85D4A"/><rect x="684" y="94" width="6" height="6" fill="#E85D4A"/><rect x="696" y="94" width="6" height="6" fill="#E85D4A"/>
        <rect x="672" y="100" width="6" height="6" fill="#E85D4A"/><rect x="690" y="100" width="6" height="6" fill="#E85D4A"/>
        <rect x="678" y="106" width="6" height="6" fill="#F5A623"/><rect x="684" y="106" width="6" height="6" fill="#F5A623"/>
        <rect x="672" y="112" width="6" height="6" fill="#F5A623"/><rect x="690" y="112" width="6" height="6" fill="#F5A623"/>
      </g>
    </g>
    <g id="heart">
      <g shape-rendering="crispEdges">
        <rect x="678" y="320" width="6" height="6" fill="#E85D4A"/><rect x="684" y="320" width="6" height="6" fill="#E85D4A"/><rect x="696" y="320" width="6" height="6" fill="#E85D4A"/><rect x="702" y="320" width="6" height="6" fill="#E85D4A"/>
        <rect x="672" y="326" width="6" height="6" fill="#E85D4A"/><rect x="678" y="326" width="6" height="6" fill="#E85D4A"/><rect x="684" y="326" width="6" height="6" fill="#E85D4A"/><rect x="690" y="326" width="6" height="6" fill="#E85D4A"/><rect x="696" y="326" width="6" height="6" fill="#E85D4A"/><rect x="702" y="326" width="6" height="6" fill="#E85D4A"/><rect x="708" y="326" width="6" height="6" fill="#E85D4A"/>
        <rect x="672" y="332" width="6" height="6" fill="#E85D4A"/><rect x="678" y="332" width="6" height="6" fill="#E85D4A"/><rect x="684" y="332" width="6" height="6" fill="#E85D4A"/><rect x="690" y="332" width="6" height="6" fill="#E85D4A"/><rect x="696" y="332" width="6" height="6" fill="#E85D4A"/><rect x="702" y="332" width="6" height="6" fill="#E85D4A"/><rect x="708" y="332" width="6" height="6" fill="#E85D4A"/>
        <rect x="678" y="338" width="6" height="6" fill="#E85D4A"/><rect x="684" y="338" width="6" height="6" fill="#E85D4A"/><rect x="690" y="338" width="6" height="6" fill="#E85D4A"/><rect x="696" y="338" width="6" height="6" fill="#E85D4A"/><rect x="702" y="338" width="6" height="6" fill="#E85D4A"/>
        <rect x="684" y="344" width="6" height="6" fill="#E85D4A"/><rect x="690" y="344" width="6" height="6" fill="#E85D4A"/><rect x="696" y="344" width="6" height="6" fill="#E85D4A"/>
        <rect x="690" y="350" width="6" height="6" fill="#E85D4A"/>
      </g>
    </g>
    <g id="daisy">
      <g shape-rendering="crispEdges">
        <rect x="56" y="326" width="6" height="6" fill="#E58AB8"/><rect x="68" y="326" width="6" height="6" fill="#E58AB8"/>
        <rect x="50" y="332" width="6" height="6" fill="#E58AB8"/><rect x="56" y="332" width="6" height="6" fill="#E58AB8"/><rect x="62" y="332" width="6" height="6" fill="#E58AB8"/><rect x="68" y="332" width="6" height="6" fill="#E58AB8"/><rect x="74" y="332" width="6" height="6" fill="#E58AB8"/>
        <rect x="44" y="338" width="6" height="6" fill="#E58AB8"/><rect x="50" y="338" width="6" height="6" fill="#FFD166"/><rect x="56" y="338" width="6" height="6" fill="#FFD166"/><rect x="62" y="338" width="6" height="6" fill="#FFD166"/><rect x="68" y="338" width="6" height="6" fill="#FFD166"/><rect x="74" y="338" width="6" height="6" fill="#FFD166"/><rect x="80" y="338" width="6" height="6" fill="#E58AB8"/>
        <rect x="50" y="344" width="6" height="6" fill="#E58AB8"/><rect x="56" y="344" width="6" height="6" fill="#E58AB8"/><rect x="62" y="344" width="6" height="6" fill="#E58AB8"/><rect x="68" y="344" width="6" height="6" fill="#E58AB8"/><rect x="74" y="344" width="6" height="6" fill="#E58AB8"/>
        <rect x="56" y="350" width="6" height="6" fill="#E58AB8"/><rect x="68" y="350" width="6" height="6" fill="#E58AB8"/>
      </g>
    </g>
    <g id="sparkle">
      <g shape-rendering="crispEdges">
        <rect x="752" y="190" width="6" height="6" fill="#FFD166"/>
        <rect x="746" y="196" width="6" height="6" fill="#FFD166"/><rect x="752" y="196" width="6" height="6" fill="#FFD166"/><rect x="758" y="196" width="6" height="6" fill="#FFD166"/>
        <rect x="740" y="202" width="6" height="6" fill="#FFD166"/><rect x="746" y="202" width="6" height="6" fill="#FFD166"/><rect x="752" y="202" width="6" height="6" fill="#FFD166"/><rect x="758" y="202" width="6" height="6" fill="#FFD166"/><rect x="764" y="202" width="6" height="6" fill="#FFD166"/>
        <rect x="746" y="208" width="6" height="6" fill="#FFD166"/><rect x="752" y="208" width="6" height="6" fill="#FFD166"/><rect x="758" y="208" width="6" height="6" fill="#FFD166"/>
        <rect x="752" y="214" width="6" height="6" fill="#FFD166"/>
      </g>
    </g>
  </defs>"""

# 精灵直接内联（不依赖 <use>，兼容所有渲染器）
SPRITES_INLINE = re.search(r"<defs>(.*)</defs>", HERO_DEFS, re.S).group(1).strip()


def pixel_bar(x0, x1, y, bw=8, bh=5, gap=4, color="#FFD166"):
    """一串像素方块（用于名字下的像素下划线）。"""
    blocks = []
    x = x0
    while x + bw <= x1:
        blocks.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{color}"/>')
        x += bw + gap
    if x < x1:
        blocks.append(f'<rect x="{x}" y="{y}" width="{max(x1 - x, 3)}" height="{bh}" fill="{color}"/>')
    return "".join(blocks)


def gen_hero(cfg):
    greeting = PX(cfg.get("greeting", "hi there, I'm"))
    name = PX(cfg.get("name", "Erywim"))
    tagline = PX(cfg.get("tagline", ""))
    sub1 = PX(cfg.get("sub1", ""))
    sub2 = PX(cfg.get("sub2", ""))

    g_size = min(22, 660 / max(text_w(greeting, 1), 1))
    n_size = min(64, 470 / max(text_w(name, 1), 1))   # 名字要避开右上火箭
    t_size = min(20, 660 / max(text_w(tagline, 1), 1)) if tagline else 20
    name_w = text_w(name, n_size)
    underline = pixel_bar(162, 162 + name_w, 192)

    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" width="860" height="400" viewBox="0 0 860 400">')
    # 深色像素面板
    out.append(f'<rect x="0" y="0" width="860" height="400" fill="{FRAME}"/>')
    out.append(f'<rect x="3" y="3" width="854" height="394" fill="{PANEL}"/>')
    out.append(f'<rect x="3" y="3" width="854" height="4" fill="{RAIL}"/>')
    out.append(f'<rect x="6" y="6" width="848" height="388" fill="none" stroke="{FRAME}" stroke-width="1"/>')
    out.append('  <!-- 像素元素（内联，避免 <use> 兼容问题） -->')
    out.append(SPRITES_INLINE)
    out.append('  <!-- 文字 -->')
    out.append(f'  <text x="160" y="114" font-size="{g_size:.0f}" font-family="{PX_FONT}" font-weight="bold" fill="#FF8A7A">{esc(greeting)}</text>')
    out.append(f'  <text x="158" y="178" font-size="{n_size:.0f}" font-family="{PX_FONT}" font-weight="bold" fill="{TXT}">{esc(name)}</text>')
    out.append(f'  <g shape-rendering="crispEdges">{underline}</g>')
    if tagline:
        out.append(f'  <text x="160" y="240" font-size="{t_size:.0f}" font-family="{PX_FONT}" font-weight="bold" fill="#7ED6B8">{esc(tagline)}</text>')
    if sub1:
        out.append(f'  <text x="162" y="274" font-size="14" fill="{TXT2}" font-family="{PX_FONT}">{esc(sub1)}</text>')
    if sub2:
        out.append(f'  <text x="162" y="300" font-size="14" fill="{TXT2}" font-family="{PX_FONT}">{esc(sub2)}</text>')
    out.append('</svg>')
    return "\n".join(out)


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    for key, cfg in data.items():
        if key == "hero":
            path = os.path.join(OUT, "hero.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(gen_hero(cfg))
            print(f"generated {path}")
        else:
            rail_label = cfg.get("rail", "FS")
            path = os.path.join(OUT, f"card-{key}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(gen_card(rail_label, cfg))
            print(f"generated {path}")


if __name__ == "__main__":
    main()
