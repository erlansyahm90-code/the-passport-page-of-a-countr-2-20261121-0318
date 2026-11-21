#!/usr/bin/env python3
"""Build the passport-spread entry image for make.fun competition
the-passport-page-of-a-countr-2-20261121-0318.

Renders an open passport spread for the invented North Atlantic island
nation of Aldruna: data page (portrait + MRZ) on the left, visa/stamp page
on the right. Output: entry.png, 1024x1024, <= 1 MiB.

Everything is drawn from scratch with PIL (no downloaded assets).
Run: python3 build_passport.py
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIFB = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANSB = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
MONO = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")
MONOB = os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")

W, H = 1024, 1024
NAVY = (30, 58, 92)
DARK = (22, 34, 56)
LABEL_GREY = (105, 105, 112)
CREAM = (246, 242, 231)
CREAM2 = (248, 244, 234)
GOLD = (176, 141, 60)


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- ICAO MRZ
def check_digit(s):
    """ICAO 9303 check digit: values A=10..Z=35, '<'=0, weights 7,3,1."""
    vals = {}
    for i, ch in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[ch] = i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<ALDELDVIK<<MARIT<SOLVEIG"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "AL4839201"
    dob = "880907"
    exp = "330313"
    personal = "0709884217<<<<<"
    cd_doc = check_digit(doc)
    cd_dob = check_digit(dob)
    cd_exp = check_digit(exp)
    composite = doc + cd_doc + dob + cd_dob + exp + cd_exp + personal
    cd_final = check_digit(composite)
    line2 = doc + cd_doc + "ALD" + dob + cd_dob + "F" + exp + cd_exp + personal + cd_final
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# ---------------------------------------------------------------- emblem
def draw_emblem(size, fg=NAVY, accent=GOLD, bg=None):
    """Coat of arms of Aldruna: shield, eight-point star, three waves."""
    s = size * 3
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # shield
    shield = [
        (0.18 * s, 0.10 * s), (0.82 * s, 0.10 * s),
        (0.82 * s, 0.52 * s), (0.50 * s, 0.92 * s), (0.18 * s, 0.52 * s),
    ]
    d.polygon(shield, fill=fg + (255,), outline=accent + (255,))
    d.line(shield + [shield[0]], fill=accent + (255,), width=max(2, s // 90))
    # eight-point star
    cx, cy, r1, r2 = 0.50 * s, 0.30 * s, 0.13 * s, 0.055 * s
    star = []
    for i in range(16):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / 8 - math.pi / 2
        star.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(star, fill=accent + (255,))
    # three waves
    for k in range(3):
        y0 = (0.52 + 0.10 * k) * s
        pts = []
        for x in range(int(0.26 * s), int(0.74 * s), 4):
            pts.append((x, y0 + 0.018 * s * math.sin((x - 0.26 * s) / (0.48 * s) * math.pi * 3)))
        d.line(pts, fill=(235, 235, 225, 255), width=max(2, s // 110))
    img = img.resize((size, size), Image.LANCZOS)
    if bg is not None:
        base = Image.new("RGBA", (size, size), bg + (255,))
        base.alpha_composite(img)
        return base.convert("RGB")
    return img


# ---------------------------------------------------------------- portrait
def draw_portrait(w, h):
    """Flat-illustration passport portrait, drawn at 3x then downscaled."""
    # Design space is 450x570 (3x the final photo); the numbers below
    # are literal pixels in that space, line widths tripled for downscale.
    SS = 1
    W3, H3 = w * 3, h * 3
    img = Image.new("RGB", (W3, H3), (0, 0, 0))
    d = ImageDraw.Draw(img)
    # backdrop gradient (cool blue-grey, top darker)
    for y in range(H3):
        t = y / H3
        r = int(168 + (216 - 168) * t)
        g = int(190 + (224 - 190) * t)
        b = int(212 + (238 - 212) * t)
        d.line([(0, y), (W3, y)], fill=(r, g, b))
    skin = (243, 214, 182)
    skin_sh = (226, 188, 152)
    hair = (176, 141, 79)
    hair_d = (138, 106, 53)
    hair_l = (198, 166, 106)
    cx = W3 // 2
    # shoulders / top (navy sweater)
    d.ellipse([cx - 200 * SS, 400 * SS, cx + 200 * SS, 760 * SS], fill=(43, 58, 85))
    d.ellipse([cx - 150 * SS, 430 * SS, cx + 150 * SS, 700 * SS], fill=(52, 68, 98))
    # shirt V at neck
    d.polygon([(cx - 42 * SS, 392 * SS), (cx + 42 * SS, 392 * SS),
               (cx, 470 * SS)], fill=(226, 232, 238))
    # neck
    d.rounded_rectangle([cx - 42 * SS, 300 * SS, cx + 42 * SS, 420 * SS],
                        radius=20 * SS, fill=skin_sh)
    d.rounded_rectangle([cx - 42 * SS, 300 * SS, cx + 42 * SS, 405 * SS],
                        radius=20 * SS, fill=skin)
    # back hair (falls to shoulders, frames the face)
    d.ellipse([cx - 128 * SS, 78 * SS, cx + 128 * SS, 470 * SS], fill=hair)
    # ears
    d.ellipse([cx - 118 * SS, 235 * SS, cx - 92 * SS, 285 * SS], fill=skin_sh)
    d.ellipse([cx + 92 * SS, 235 * SS, cx + 118 * SS, 285 * SS], fill=skin_sh)
    # face
    d.ellipse([cx - 100 * SS, 118 * SS, cx + 100 * SS, 378 * SS], fill=skin)
    # jaw shading (soft, both sides)
    shade = Image.new("RGBA", (W3, H3), (0, 0, 0, 0))
    ds = ImageDraw.Draw(shade)
    ds.ellipse([cx - 100 * SS, 118 * SS, cx + 100 * SS, 378 * SS],
               fill=(0, 0, 0, 0), outline=(196, 152, 110, 60), width=30)
    img.paste(Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    # front hair: top sweep with centre parting
    d.ellipse([cx - 104 * SS, 96 * SS, cx + 104 * SS, 250 * SS], fill=hair)
    # face opening (re-cut the forehead oval)
    d.ellipse([cx - 88 * SS, 150 * SS, cx + 88 * SS, 378 * SS], fill=skin)
    # side sweeps
    d.ellipse([cx - 108 * SS, 150 * SS, cx - 70 * SS, 330 * SS], fill=hair)
    d.ellipse([cx + 70 * SS, 150 * SS, cx + 108 * SS, 330 * SS], fill=hair)
    # hair strands
    for (x0, y0, x1, y1) in [(150, 120, 190, 210), (260, 120, 300, 210),
                             (140, 180, 165, 300), (285, 180, 310, 300)]:
        d.arc([min(x0, x1) * SS, y0 * SS, max(x0, x1) * SS, y1 * SS], 200, 340,
              fill=hair_d, width=6)
    d.arc([cx - 60 * SS, 108 * SS, cx + 60 * SS, 200 * SS], 180, 360,
          fill=hair_l, width=9)
    # eyebrows
    d.arc([cx - 72 * SS, 205 * SS, cx - 22 * SS, 235 * SS], 200, 340,
          fill=(122, 90, 52), width=12)
    d.arc([cx + 22 * SS, 205 * SS, cx + 72 * SS, 235 * SS], 200, 340,
          fill=(122, 90, 52), width=12)
    # eyes
    for ex in (cx - 47 * SS, cx + 47 * SS):
        ey = 248 * SS
        d.ellipse([ex - 17 * SS, ey - 10 * SS, ex + 17 * SS, ey + 10 * SS],
                  fill=(250, 250, 248))
        d.ellipse([ex - 9 * SS, ey - 9 * SS, ex + 9 * SS, ey + 9 * SS],
                  fill=(90, 122, 153))
        d.ellipse([ex - 4 * SS, ey - 4 * SS, ex + 4 * SS, ey + 4 * SS],
                  fill=(20, 20, 24))
        d.ellipse([ex + 2 * SS, ey - 6 * SS, ex + 6 * SS, ey - 2 * SS],
                  fill=(255, 255, 255))
        d.arc([ex - 18 * SS, ey - 13 * SS, ex + 18 * SS, ey + 8 * SS], 180, 360,
              fill=(60, 50, 45), width=6)
    # nose: soft shadow + nostrils
    d.line([(cx - 2 * SS, 258 * SS), (cx - 5 * SS, 298 * SS)],
           fill=(214, 172, 138), width=9)
    d.arc([cx - 12 * SS, 292 * SS, cx + 12 * SS, 308 * SS], 0, 180,
          fill=(198, 152, 116), width=6)
    d.ellipse([cx - 10 * SS, 300 * SS, cx - 5 * SS, 305 * SS], fill=(150, 105, 80))
    d.ellipse([cx + 5 * SS, 300 * SS, cx + 10 * SS, 305 * SS], fill=(150, 105, 80))
    # lips (neutral, closed)
    d.arc([cx - 26 * SS, 322 * SS, cx + 26 * SS, 348 * SS], 0, 180,
          fill=(192, 131, 116), width=12)
    d.arc([cx - 24 * SS, 330 * SS, cx + 24 * SS, 352 * SS], 0, 180,
          fill=(178, 110, 98), width=9)
    d.line([(cx - 24 * SS, 336 * SS), (cx + 24 * SS, 336 * SS)],
           fill=(150, 95, 85), width=6)
    # blush
    blush = Image.new("RGBA", (W3, H3), (0, 0, 0, 0))
    db = ImageDraw.Draw(blush)
    db.ellipse([cx - 92 * SS, 285 * SS, cx - 58 * SS, 308 * SS], fill=(230, 150, 130, 45))
    db.ellipse([cx + 58 * SS, 285 * SS, cx + 92 * SS, 308 * SS], fill=(230, 150, 130, 45))
    img = Image.alpha_composite(img.convert("RGBA"), blush).convert("RGB")
    img = img.crop((45, 30, 405, 486))
    return img.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- stamps
def make_stamp(lines, size, ink, shape="rect"):
    """Border-control stamp on a transparent layer (drawn 2x, downscaled)."""
    SS = 2
    w, h = size[0] * SS, size[1] * SS
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = ink + (185,)
    pad = 8 * SS
    if shape == "oval":
        d.ellipse([pad, pad, w - pad, h - pad], outline=col, width=4 * SS)
        d.ellipse([pad + 6 * SS, pad + 6 * SS, w - pad - 6 * SS, h - pad - 6 * SS],
                  outline=col, width=2 * SS)
    else:
        d.rounded_rectangle([pad, pad, w - pad, h - pad], radius=8 * SS,
                            outline=col, width=4 * SS)
        d.rounded_rectangle([pad + 6 * SS, pad + 6 * SS, w - pad - 6 * SS,
                             h - pad - 6 * SS], radius=5 * SS,
                            outline=col, width=2 * SS)
    f_big = font(SANSB, 15 * SS)
    f_mid = font(SANSB, 12 * SS)
    f_small = font(SANSB, 10 * SS)
    f_date = font(MONOB, 13 * SS)
    fonts = [f_small, f_mid, f_big, f_date]
    total = sum(f.getbbox(t)[3] + 4 * SS for f, t in zip(fonts, lines))
    y = (h - total) // 2
    for f, t in zip(fonts, lines):
        bb = d.textbbox((0, 0), t, font=f)
        d.text(((w - (bb[2] - bb[0])) // 2, y), t, font=f, fill=col)
        y += (bb[3] - bb[1]) + 4 * SS
    img = img.filter(ImageFilter.GaussianBlur(0.6 * SS))
    return img.resize(size, Image.LANCZOS)


def paste_stamp(page, stamp_img, pos, angle):
    rotated = stamp_img.rotate(angle, expand=True, resample=Image.BICUBIC)
    page.alpha_composite(rotated, dest=pos)


# ---------------------------------------------------------------- guilloche
def guilloche(d, x0, y0, x1, y1, color=(221, 214, 189), step=14):
    y = y0 + 6
    phase = 0.0
    while y < y1:
        pts = []
        for x in range(x0, x1, 6):
            pts.append((x, y + 3.5 * math.sin((x - x0) / 46.0 + phase)))
        d.line(pts, fill=color, width=1)
        y += step
        phase += 0.55


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), (15, 22, 34))
    d = ImageDraw.Draw(img)
    # soft radial light behind the booklet
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.ellipse([-220, -160, W + 220, H + 160], fill=(52, 70, 102, 90))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(
        ImageFilter.GaussianBlur(120))).convert("RGB")
    d = ImageDraw.Draw(img)

    # page geometry
    lp = (30, 44, 498, 980)    # left page
    rp = (526, 44, 994, 980)   # right page
    # drop shadows
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rectangle([lp[0] + 6, lp[1] + 10, lp[2] + 6, lp[3] + 10], fill=(0, 0, 0, 120))
    ds.rectangle([rp[0] + 6, rp[1] + 10, rp[2] + 6, rp[3] + 10], fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img.convert("RGBA"),
                                sh.filter(ImageFilter.GaussianBlur(10))).convert("RGB")
    d = ImageDraw.Draw(img)
    # pages
    d.rectangle(lp, fill=CREAM2)
    d.rectangle(rp, fill=CREAM)
    # spine shadow on pages
    spine = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dsp = ImageDraw.Draw(spine)
    for i in range(26):
        a = int(70 * (1 - i / 26))
        dsp.line([(lp[2] - i, lp[1]), (lp[2] - i, lp[3])], fill=(60, 50, 30, a))
        dsp.line([(rp[0] + i, rp[1]), (rp[0] + i, rp[3])], fill=(60, 50, 30, a))
    img = Image.alpha_composite(img.convert("RGBA"), spine).convert("RGB")
    d = ImageDraw.Draw(img)
    # page frames (double rule)
    for (x0, y0, x1, y1) in (lp, rp):
        d.rectangle([x0 + 9, y0 + 9, x1 - 9, y1 - 9], outline=NAVY, width=2)
        d.rectangle([x0 + 14, y0 + 14, x1 - 14, y1 - 14], outline=NAVY, width=1)
    # guilloche inside frames
    guilloche(d, lp[0] + 16, lp[1] + 16, lp[2] - 16, lp[3] - 16)
    guilloche(d, rp[0] + 16, rp[1] + 16, rp[2] - 16, rp[3] - 16)

    # ================= LEFT PAGE: data page =================
    cx = (lp[0] + lp[2]) // 2
    # emblem + country name
    emb = draw_emblem(62)
    img.paste(emb, (cx - 31, 62), emb)
    d = ImageDraw.Draw(img)
    f_country = font(SERIFB, 25)
    t = "REPUBLIC OF ALDRUNA"
    bb = d.textbbox((0, 0), t, font=f_country)
    d.text((cx - (bb[2] - bb[0]) // 2, 128), t, font=f_country, fill=NAVY)
    f_sub = font(SANS, 11)
    t2 = "F E R Ð A B R É F   ·   P A S S P O R T"
    bb = d.textbbox((0, 0), t2, font=f_sub)
    d.text((cx - (bb[2] - bb[0]) // 2, 158), t2, font=f_sub, fill=LABEL_GREY)
    d.line([(lp[0] + 24, 182), (lp[2] - 24, 182)], fill=NAVY, width=2)

    # portrait
    photo = draw_portrait(150, 190)
    d.rectangle([54, 198, 208, 392], fill=(255, 255, 255), outline=NAVY, width=2)
    img.paste(photo, (58, 202))
    d = ImageDraw.Draw(img)

    # data fields right of the photo
    fx = 222
    f_lab = font(SANSB, 9)
    f_val = font(SANSB, 14)
    f_val_s = font(SANSB, 12)
    rows = [
        ("TYPE", "P", "CODE", "ALD"),
        ("PASSPORT No.", "AL4839201", None, None),
        ("SURNAME", "ELDVIK", None, None),
        ("GIVEN NAMES", "MARIT SOLVEIG", None, None),
        ("NATIONALITY", "ALDRUNESE", "SEX", "F"),
        ("DATE OF BIRTH", "07 SEP 1988", None, None),
        ("PLACE OF BIRTH", "SKARDVIK", None, None),
    ]
    y = 200
    for lab, val, lab2, val2 in rows:
        d.text((fx, y), lab, font=f_lab, fill=LABEL_GREY)
        d.text((fx, y + 11), val, font=f_val, fill=DARK)
        if lab2:
            d.text((fx + 170, y), lab2, font=f_lab, fill=LABEL_GREY)
            d.text((fx + 170, y + 11), val2, font=f_val, fill=DARK)
        y += 30 if val2 is None and lab2 is None else 30
        if lab in ("PASSPORT No.", "SURNAME", "GIVEN NAMES"):
            y += 0
    # second block: issue / expiry / authority / personal no.
    y = 412
    d.line([(lp[0] + 24, y), (lp[2] - 24, y)], fill=(180, 175, 155), width=1)
    y += 10
    block = [
        ("DATE OF ISSUE", "14 MAR 2023", "DATE OF EXPIRY", "13 MAR 2033"),
        ("AUTHORITY", "MINISTRY OF THE INTERIOR", None, None),
        ("PERSONAL No.", "070988-4217", "HEIGHT", "171 cm"),
    ]
    for lab, val, lab2, val2 in block:
        d.text((54, y), lab, font=f_lab, fill=LABEL_GREY)
        d.text((54, y + 11), val, font=f_val_s, fill=DARK)
        if lab2:
            d.text((280, y), lab2, font=f_lab, fill=LABEL_GREY)
            d.text((280, y + 11), val2, font=f_val_s, fill=DARK)
        y += 30
    # signature
    y += 6
    d.line([(54, y + 18), (300, y + 18)], fill=DARK, width=1)
    f_sig = font(SERIF, 17)
    d.text((60, y - 6), "Marit Eldvik", font=f_sig, fill=(40, 60, 110))
    d.text((54, y + 22), "SIGNATURE OF HOLDER", font=f_lab, fill=LABEL_GREY)
    # endorsement (the telling detail)
    ey0 = 640
    d.rectangle([54, ey0, lp[2] - 24, ey0 + 96], outline=NAVY, width=1)
    d.text((64, ey0 + 8), "ENDORSEMENT", font=f_lab, fill=NAVY)
    f_end = font(SANS, 11)
    endorsement = [
        "Holder is licensed to crew fishing vessels in",
        "Aldruna waters and is exempt from harbour dues",
        "at Skardvik, Vagsey and North Quay.",
        "— Maritime Authority, Skardvik",
    ]
    yy = ey0 + 24
    for line in endorsement:
        d.text((64, yy), line, font=f_end, fill=DARK)
        yy += 16
    # ghost image (security feature) + property notice
    ghost = photo.resize((70, 88), Image.LANCZOS).convert("RGBA")
    ghost.putalpha(ghost.split()[3].point(lambda a: int(a * 0.55)))
    img.paste(ghost, (lp[2] - 24 - 70, 752), ghost)
    d = ImageDraw.Draw(img)
    d.rectangle([lp[2] - 24 - 70, 752, lp[2] - 24, 752 + 88],
                outline=(150, 145, 125), width=1)
    d.text((54, 766), 'THIS PASSPORT REMAINS THE PROPERTY OF',
           font=font(SANS, 9), fill=LABEL_GREY)
    d.text((54, 780), 'THE REPUBLIC OF ALDRUNA.',
           font=font(SANS, 9), fill=LABEL_GREY)
    # MRZ
    mz0 = 868
    d.rectangle([lp[0] + 16, mz0 - 8, lp[2] - 16, mz0 + 52], fill=(235, 230, 214))
    d.line([(lp[0] + 16, mz0 - 8), (lp[2] - 16, mz0 - 8)], fill=NAVY, width=1)
    f_mrz = font(MONO, 13)
    l1, l2 = mrz_lines()
    d.text((lp[0] + 30, mz0), l1, font=f_mrz, fill=DARK)
    d.text((lp[0] + 30, mz0 + 20), l2, font=f_mrz, fill=DARK)

    # ================= RIGHT PAGE: visas / stamps =================
    d.text((550, 62), "VISAS", font=font(SERIFB, 21), fill=NAVY)
    d.text((550, 88), "V Í S A", font=font(SANS, 10), fill=LABEL_GREY)
    d.text((930, 66), "8", font=font(SERIFB, 20), fill=NAVY)
    d.line([(rp[0] + 24, 116), (rp[2] - 24, 116)], fill=NAVY, width=2)
    # faint watermark emblem
    wm = draw_emblem(300)
    wm.putalpha(wm.split()[3].point(lambda a: int(a * 0.10)))
    img.paste(wm, (750 - 150, 500 - 150), wm)
    d = ImageDraw.Draw(img)

    page = img.convert("RGBA")
    BLUE = (28, 78, 158)
    RED = (158, 40, 58)
    DKBLUE = (24, 48, 96)
    GREEN = (28, 118, 62)
    stamps = [
        (["ÍSLAND · ICELAND", "KEFLAVÍK", "ARRIVAL", "02 JUN 2023"],
         (182, 112), BLUE, "oval", (566, 150), -8),
        (["ÍSLAND · ICELAND", "KEFLAVÍK", "DEPARTURE", "09 JUN 2023"],
         (182, 112), BLUE, "oval", (786, 168), 6),
        (["NORGE · NORWAY", "BERGEN", "ARRIVAL", "18 OCT 2024"],
         (182, 112), RED, "rect", (572, 386), 5),
        (["NORGE · NORWAY", "BERGEN", "DEPARTURE", "25 OCT 2024"],
         (182, 112), RED, "rect", (792, 404), -7),
        (["UNITED KINGDOM", "ABERDEEN", "ARRIVAL", "11 APR 2025"],
         (182, 112), DKBLUE, "rect", (570, 622), -5),
        (["UNITED KINGDOM", "ABERDEEN", "DEPARTURE", "18 APR 2025"],
         (182, 112), DKBLUE, "rect", (790, 640), 8),
        (["SKARDVIK", "PORT TAX PAID", "40 KR", "02 JUN 2023"],
         (168, 104), GREEN, "rect", (664, 812), -3),
    ]
    for lines, size, ink, shape, pos, angle in stamps:
        st = make_stamp(lines, size, ink, shape)
        paste_stamp(page, st, pos, angle)
    img = page.convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((750 - 110, 940), "THIS PASSPORT CONTAINS 32 PAGES",
           font=font(SANS, 9), fill=LABEL_GREY)

    img.save(OUT, optimize=True)
    n = os.path.getsize(OUT)
    sha = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"saved {OUT}: {img.size}, {n} bytes, sha256 {sha[:16]}…")
    print("MRZ:", l1)
    print("MRZ:", l2)
    assert n <= 1048576, "entry.png over 1 MiB"
    return OUT


if __name__ == "__main__":
    render()
