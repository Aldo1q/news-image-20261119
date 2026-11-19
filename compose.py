#!/usr/bin/env python3
"""Compose the news-image-20261119 front page (broadsheet).

Design (DeepSeek V4.1 Flash analysis lane, applying the sibling entry's
winning redesign): square broadsheet, not a dashboard. Off-white newsprint,
black rules, ONE red accent reserved for the lead kicker and the Brent chart
callout. Dominant lead: the first-ever Trump-Xi-Putin trilateral in Shenzhen
(names first in the headline, city in the kicker), a three-flags hero (no
faces), a "Why it matters" box, data modules (Brent intraday chart,
Anthropic's record-IPO stats), three compact briefs (ICJ Rohingya ruling,
Crimea Bridge, IMF debt warning) and a World Briefs rail. All text
PIL-rendered; only the hero is an AI photo (flags + venue, no faces).
Layout v2: copy tightened so every block fits the 1024px page (v1 ran
the briefs and the rail off the bottom edge).
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
HERO = os.path.join(BASE, "assets", "media-generation-hero-shenzhen-trilateral-20261-0-1c0f0643-33c0-4118-b353-ff3ce58dd4f5.webp")
OUT = os.path.join(BASE, "entry.png")

W, H = 1024, 1024
M = 48                      # margin
CW = W - 2 * M              # content width = 928
PAPER = (247, 243, 234)
INK = (18, 18, 18)
GREY = (84, 84, 84)
FAINT = (188, 182, 170)
RED = (178, 34, 34)
BAR = (40, 40, 40)

def font(name, size):
    for p in (f"/usr/share/fonts/truetype/dejavu/{name}.ttf", f"/usr/share/fonts/{name}.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_MAST = font("DejaVuSerif-Bold", 54)
F_FURN = font("DejaVuSans-Bold", 14)
F_HOOK = font("DejaVuSans-Bold", 14)
F_KICK = font("DejaVuSans-Bold", 16)
F_LEAD = font("DejaVuSerif-Bold", 43)
F_DECK = font("DejaVuSerif", 20)
F_BODY = font("DejaVuSans", 15)
F_BYLINE = font("DejaVuSans-Bold", 12)
F_CAP = font("DejaVuSans", 12)
F_BOXHEAD = font("DejaVuSans-Bold", 14)
F_BULLET = font("DejaVuSans", 14)
F_MODHEAD = font("DejaVuSerif-Bold", 25)
F_MODHEAD_SM = font("DejaVuSerif-Bold", 18)
F_MODTEXT = font("DejaVuSans", 14)
F_MODTEXT_SM = font("DejaVuSans", 13)
F_CHART = font("DejaVuSans-Bold", 17)
F_CHART_SM = font("DejaVuSans", 11)
F_STAT = font("DejaVuSans-Bold", 21)
F_BRIEF = font("DejaVuSans", 13)

def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_block(d, x, y, text, fnt, fill, max_w, leading):
    for line in wrap(d, text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y

def crop_to_fill(img, tw, th, fx=0.5, fy=0.5):
    scale = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * scale + 0.5), int(img.height * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x0 = min(max(int(fx * nw - tw / 2), 0), nw - tw)
    y0 = min(max(int(fy * nh - th / 2), 0), nh - th)
    return img.crop((x0, y0, x0 + tw, y0 + th))

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- furniture + masthead ----------
    d.line([M, 22, W - M, 22], fill=INK, width=2)
    d.text((M, 30), "WORLD EDITION", font=F_FURN, fill=INK)
    date = "Thursday, 19 November 2026"
    d.text(((W - d.textlength(date, font=F_FURN)) / 2, 30), date, font=F_FURN, fill=INK)
    vol = "VOL. 1 · NO. 25 · PAGE 1"
    d.text((W - M - d.textlength(vol, font=F_FURN), 30), vol, font=F_FURN, fill=INK)
    d.line([M, 54, W - M, 54], fill=INK, width=1)
    title = "THE WORLD IN ONE IMAGE"
    d.text(((W - d.textlength(title, font=F_MAST)) / 2, 64), title, font=F_MAST, fill=INK)
    hook = "FIRST-EVER TRILATERAL: UKRAINE, NUCLEAR ARMS AND HORMUZ ON ONE TABLE"
    d.text(((W - d.textlength(hook, font=F_HOOK)) / 2, 132), hook, font=F_HOOK, fill=GREY)
    d.line([M, 156, W - M, 156], fill=INK, width=4)
    d.line([M, 164, W - M, 164], fill=INK, width=1)

    # ---------- lead story ----------
    LX, LW = M, 520
    RX, RW = 592, W - M - 592   # 384
    y = 182
    d.text((LX, y), "FIRST-EVER TRILATERAL · SHENZHEN · APEC", font=F_KICK, fill=RED)
    y += 26
    y = text_block(d, LX, y, "TRUMP, XI AND PUTIN MEET AT ONE TABLE", F_LEAD, INK, LW, 54)
    y += 6
    y = text_block(d, LX, y, "The US, Chinese and Russian leaders sit down together for the first time.", F_DECK, INK, LW, 27)
    y += 8
    y = text_block(d, LX, y, "Trump met Putin for forty minutes — Ukraine dominated, the Kremlin says — and Xi separately, before the three-way talks.", F_BODY, GREY, LW, 21)
    y += 8
    d.text((LX, y), "By the World Desk · Shenzhen", font=F_BYLINE, fill=INK)
    lead_left_end = y + 16

    ry = 182
    hero = crop_to_fill(Image.open(HERO).convert("RGB"), RW, 168, fx=0.40, fy=0.30)
    img.paste(hero, (RX, ry))
    ry += 176
    ry = text_block(d, RX, ry, "The flags of the United States, China and Russia over Shenzhen's convention district.", F_CAP, GREY, RW, 16)
    d.text((RX, ry), "PHOTO: WIRE IMAGE", font=F_CAP, fill=INK)
    ry += 24
    box_top = ry
    bullets = [
        "A first: all three leaders together",
        "Ukraine, nuclear arms lead agenda",
        "New START gone; Hormuz oil at stake",
    ]
    by = box_top + 10
    d.text((RX + 14, by), "WHY IT MATTERS", font=F_BOXHEAD, fill=INK)
    by += 22
    for b in bullets:
        d.rectangle([RX + 14, by + 5, RX + 20, by + 11], fill=INK)
        by = text_block(d, RX + 28, by, b, F_BULLET, GREY, RW - 42, 19)
        by += 2
    box_bot = by + 4
    d.rectangle([RX, box_top, RX + RW, box_bot], outline=INK, width=1)
    lead_end = max(lead_left_end, box_bot)
    print("lead ends:", lead_left_end, box_bot)

    # ---------- markets + anthropic band ----------
    y = lead_end + 14
    d.line([M, y, W - M, y], fill=INK, width=2)
    y += 16
    band_top = y
    # markets (left, wide)
    MX, MW = M, 568
    my = text_block(d, MX, y, "MARKETS", F_KICK, INK, MW, 20)
    my += 2
    my = text_block(d, MX, my, "BRENT SLIDES AS STOCKS FALL IN EUROPE AND ASIA", F_MODHEAD, INK, MW, 31)
    my += 6
    # intraday line chart: a slide through the day
    cx, cy, cw, ch = MX, my, 520, 64
    d.line([cx, cy + 8, cx + cw, cy + 8], fill=FAINT, width=1)          # open level
    pts = [(0, 8), (80, 16), (170, 30), (260, 26), (350, 42), (440, 38), (520, 50)]
    line = [(cx + px, cy + py) for px, py in pts]
    d.line(line, fill=INK, width=3)
    ex, ey = line[-1]
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=RED)
    d.text((ex - 118, ey - 26), "-2.6%", font=F_CHART, fill=RED)
    d.text((cx, cy + ch + 2), "BRENT CRUDE · CLOSE $89.59 A BARREL · VIX 24.56", font=F_CHART_SM, fill=GREY)
    my = cy + ch + 20
    my = text_block(d, MX, my, "European markets and Hong Kong fell as the Hormuz crisis kept energy on edge. South Korea's exports passed $1 trillion for the first time, on chip demand.", F_MODTEXT, GREY, MW, 19)
    markets_end = my
    # anthropic (right, narrow): record IPO as stat rows
    NX, NW = 664, W - M - 664   # 312
    d.line([640, band_top, 640, band_top + 196], fill=FAINT, width=1)
    ny = text_block(d, NX, y, "TECHNOLOGY", F_KICK, INK, NW, 20)
    ny += 2
    ny = text_block(d, NX, ny, "ANTHROPIC'S RECORD IPO", F_MODHEAD, INK, NW, 31)
    ny += 8
    for value, label in (("$83", "PRICE PER SHARE"), ("$81.3B", "RAISED — A RECORD"), ("$1.5T", "VALUATION")):
        d.text((NX, ny), value, font=F_STAT, fill=INK)
        vw = d.textlength(value, font=F_STAT)
        d.text((NX + vw + 10, ny + 9), label, font=F_CHART_SM, fill=GREY)
        ny += 28
    ny += 2
    ny = text_block(d, NX, ny, "The largest stock-market debut ever recorded.", F_MODTEXT, GREY, NW, 19)
    band_end = max(markets_end, ny)
    print("band ends:", markets_end, ny)

    # ---------- three briefs ----------
    y = band_end + 12
    d.line([M, y, W - M, y], fill=INK, width=2)
    y += 12
    briefs = [
        ("JUSTICE", "WORLD COURT RULES ON ROHINGYA GENOCIDE CASE",
         "Gambia's case against Myanmar, over the crackdown that drove 730,000 Rohingya into Bangladesh. No state has ever been found guilty of genocide."),
        ("WAR IN UKRAINE", "CRIMEA BRIDGE HIT FOR THE THIRD TIME THIS WEEK",
         "Traffic is suspended after two nights of strikes on the bridge linking Russia to annexed Crimea — a key supply route for the peninsula."),
        ("THE WORLD ECONOMY", "IMF: GLOBAL DEBT NEARS 100% OF GDP",
         "Global public debt nears the world's entire output — a post-war record — shrinking room to answer the next crisis."),
    ]
    bw = 296
    brief_end = y
    for i, (kick, head, body) in enumerate(briefs):
        bx = M + i * (bw + 20)
        if i:
            d.line([bx - 10, y, bx - 10, y + 118], fill=FAINT, width=1)
        byy = text_block(d, bx, y, kick, F_BOXHEAD, INK, bw, 18)
        byy += 2
        byy = text_block(d, bx, byy, head, F_MODHEAD_SM, INK, bw, 22)
        byy += 3
        byy = text_block(d, bx, byy, body, F_MODTEXT_SM, GREY, bw, 16)
        brief_end = max(brief_end, byy)
        print("brief", i, "ends", byy)
    y = brief_end + 10

    # ---------- world briefs rail + folio ----------
    rail_top = y
    brief_text = "WORLD BRIEFS — IEA: the Hormuz crisis is the gravest threat to energy security ever seen · EU proposes €45 billion more for Ukraine · COP31 ministers race to unblock a climate text in Antalya · Van Gogh sells for a record $190.4 million · Bangladesh: Yunus home torched amid violence in 28 districts · Fiji declares a national disaster over drought"
    rail_end = text_block(d, M + 12, rail_top + 7, brief_text, F_BRIEF, INK, CW - 24, 16)
    d.rectangle([M, rail_top, W - M, rail_end + 5], outline=INK, width=1)
    folio = "The World in One Image · Shenzhen — The Hague — Antalya · 19 November 2026"
    d.text(((W - d.textlength(folio, font=F_CAP)) / 2, rail_end + 11), folio, font=F_CAP, fill=GREY)
    print("rail ends:", rail_end + 5, "folio at:", rail_end + 11)

    # ---------- paper grain ----------
    noise = Image.effect_noise((W, H), 14).convert("RGB")
    img = Image.blend(img, noise, 0.01)

    img.save(OUT, optimize=True)
    print("saved:", OUT, os.path.getsize(OUT), "bytes", img.size)

if __name__ == "__main__":
    main()
