#!/usr/bin/env python3
"""Build the gta6-meme-x-01 meme picture: "Dr. Ghost's Sick Note".

Programmatic composition with PIL. The make.fun ghost is rendered from the
official press-kit vector (assets/press-kit/make-fun-press-kit/mark.svg) by a
small SVG-path flattener below, so the mascot in the picture is the real brand
mark, drawn into the scene as the doctor who signs the note.

Output: meme.png (1200x1200) next to this script.
"""
import math
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 2  # supersample factor; final image is 1200x1200
W = 1200

INK = (25, 20, 25)
MAGENTA = (196, 28, 131)
GREY = (90, 83, 89)
PAPER = (255, 255, 255)
MINT_TOP = (219, 245, 238)
MINT_BOT = (168, 220, 203)

FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_CANDIDATES_REG = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
FONT_CANDIDATES_BOLDITALIC = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
]


def font(cands, size):
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, int(size * SS))
    raise SystemExit(f"no font found in {cands}")


def S(v):
    return v * SS


# --------------------------------------------------------------------------
# Tiny SVG path flattener (M/L/H/V/C/Q/A/Z, absolute + relative)
# --------------------------------------------------------------------------

TOKEN_RE = re.compile(r"[MLHVCSQTAZmlhvcsqtaz]|-?\d*\.?\d+(?:e[-+]?\d+)?")


def _arc_points(x1, y1, rx, ry, phi_deg, large, sweep, x2, y2):
    """Endpoint -> center parameterisation, sampled every ~6 degrees."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    phi = math.radians(phi_deg)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cos_p * dx + sin_p * dy
    y1p = -sin_p * dx + cos_p * dy
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        co = -co
    cxp = co * rx * y1p / ry
    cyp = -co * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x1 + x2) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (y1 + y2) / 2.0

    def angle(ux, uy, vx, vy):
        dot = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy))
        a = math.acos(max(-1.0, min(1.0, dot)))
        return -a if (ux * vy - uy * vx) < 0 else a

    ux, uy = (x1p - cxp) / rx, (y1p - cyp) / ry
    vx, vy = (-x1p - cxp) / rx, (-y1p - cyp) / ry
    start = angle(1, 0, ux, uy)
    delta = angle(ux, uy, vx, vy)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    if sweep and delta < 0:
        delta += 2 * math.pi
    steps = max(4, int(abs(math.degrees(delta)) / 6) + 1)
    pts = []
    for i in range(1, steps + 1):
        t = start + delta * i / steps
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        pts.append((cos_p * ex - sin_p * ey + cx, sin_p * ex + cos_p * ey + cy))
    return pts


def _cubic(p0, p1, p2, p3, steps=16):
    pts = []
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def _quad(p0, p1, p2, steps=12):
    pts = []
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        pts.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                    mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))
    return pts


def flatten_path(d):
    """Return a list of subpaths; each subpath is a list of (x, y) points."""
    tokens = TOKEN_RE.findall(d)
    subpaths, cur = [], []
    x = y = 0.0
    start = (0.0, 0.0)
    cmd = None
    i = 0

    def num():
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    while i < len(tokens):
        if re.fullmatch(r"[A-Za-z]", tokens[i]):
            cmd = tokens[i]
            i += 1
            if cmd in "Zz":
                if cur:
                    cur.append(start)
                    subpaths.append(cur)
                    cur = []
                x, y = start
                cmd = None
            continue
        if cmd is None:
            break
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            nx, ny = num(), num()
            if rel:
                nx, ny = nx + x, ny + y
            if cur:
                subpaths.append(cur)
            cur = [(nx, ny)]
            x, y = nx, ny
            start = (x, y)
            cmd = "l" if rel else "L"
        elif c == "L":
            nx, ny = num(), num()
            if rel:
                nx, ny = nx + x, ny + y
            cur.append((nx, ny))
            x, y = nx, ny
        elif c == "H":
            nx = num() + (x if rel else 0)
            cur.append((nx, y))
            x = nx
        elif c == "V":
            ny = num() + (y if rel else 0)
            cur.append((x, ny))
            y = ny
        elif c == "C":
            x1, y1, x2, y2, nx, ny = num(), num(), num(), num(), num(), num()
            if rel:
                x1, y1, x2, y2, nx, ny = x1 + x, y1 + y, x2 + x, y2 + y, nx + x, ny + y
            cur.extend(_cubic((x, y), (x1, y1), (x2, y2), (nx, ny)))
            x, y = nx, ny
        elif c == "Q":
            x1, y1, nx, ny = num(), num(), num(), num()
            if rel:
                x1, y1, nx, ny = x1 + x, y1 + y, nx + x, ny + y
            cur.extend(_quad((x, y), (x1, y1), (nx, ny)))
            x, y = nx, ny
        elif c == "A":
            rx, ry, phi, la, sw, nx, ny = num(), num(), num(), num(), num(), num(), num()
            if rel:
                nx, ny = nx + x, ny + y
            cur.extend(_arc_points(x, y, rx, ry, phi, int(la), int(sw), nx, ny))
            x, y = nx, ny
        else:
            raise ValueError(f"unsupported path command {cmd}")
    if cur:
        subpaths.append(cur)
    return subpaths


# --------------------------------------------------------------------------
# The make.fun ghost, from the official mark.svg path data (press kit).
# Group transform in the SVG: translate(3.858 3.202) scale(0.79) in a 32x32
# viewBox. We render the group only (no disc) on transparency.
# --------------------------------------------------------------------------

GHOST_BODY = ("M6.2 13a8.2 8.2 0 0 1 16.4 0v4.6c1 .2 1.8.8 2 2-.2 1.2-1 1.9-2 2.2V25"
              "a2.6 2.6 0 0 1-2.6 2.6c-2 0-4.6 0-5.7-.7-1.1.7-3.7.7-5.5.7"
              "A2.6 2.6 0 0 1 6.2 25v-.7c-1.2.3-3.5.1-3.6-1.9-.1-2.1 1.3-4.8 3.6-6.2z")
GHOST_SLITS = "M6.3 24.1v-2.5m8 5.8v-1.5"
EYE1 = "M13.2 10.6Q13.632 11.968 15 12.4Q13.632 12.832 13.2 14.2Q12.768 12.832 11.4 12.4Q12.768 11.968 13.2 10.6z"
EYE2 = "M19.3 9.8Q19.732 11.168 21.1 11.6Q19.732 12.032 19.3 13.4Q18.868 12.032 17.5 11.6Q18.868 11.168 19.3 9.8z"
STAR = ("M26.926 11.395L27.154 12.811L28.539 13.186L27.262 13.84L27.334 15.273"
        "L26.317 14.261L24.977 14.772L25.625 13.492L24.725 12.375L26.142 12.596z")


def render_ghost(px_w):
    """Render the ghost group at pixel width px_w (supersampled space)."""
    # viewBox-space extents of the group content
    gx0, gy0, gx1, gy1 = 5.9, 6.9, 29.2, 25.1
    scale = px_w / (gx1 - gx0)
    px_h = int((gy1 - gy0) * scale)
    img = Image.new("RGBA", (px_w + 8, px_h + 8), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)

    def T(pt):
        vx = 3.858 + 0.79 * pt[0]
        vy = 3.202 + 0.79 * pt[1]
        return ((vx - gx0) * scale + 4, (vy - gy0) * scale + 4)

    def draw_path(d, fill=None, outline=None, width=1):
        for sub in flatten_path(d):
            pts = [T(p) for p in sub]
            if fill:
                dr.polygon(pts, fill=fill)
            if outline:
                dr.line(pts, fill=outline, width=max(1, int(width)), joint="curve")

    def circle(cx, cy, r, fill):
        cxv = 3.858 + 0.79 * cx
        cyv = 3.202 + 0.79 * cy
        rv = 0.79 * r * scale
        x = (cxv - gx0) * scale + 4
        y = (cyv - gy0) * scale + 4
        dr.ellipse([x - rv, y - rv, x + rv, y + rv], fill=fill)

    # body: black underlay (fill + 3.4-unit stroke), then white fill
    draw_path(GHOST_BODY, fill=INK + (255,), outline=INK + (255,), width=3.4 * 0.79 * scale)
    draw_path(GHOST_BODY, fill=(255, 255, 255, 255))
    # slits
    for sub in flatten_path(GHOST_SLITS):
        pts = [T(p) for p in sub]
        dr.line(pts, fill=INK + (255,), width=max(2, int(1.25 * 0.79 * scale)))
    # eyes
    draw_path(EYE1, fill=INK + (255,))
    draw_path(EYE2, fill=INK + (255,))
    # star coin + bubble
    circle(26.5, 13.4, 5.5, INK + (255,))
    circle(26.5, 13.4, 3.8, MAGENTA + (255,))
    draw_path(STAR, fill=(255, 255, 255, 255))
    circle(24.9, 19.6, 4.0, INK + (255,))
    circle(24.9, 19.6, 2.3, (255, 255, 255, 255))
    return img


# --------------------------------------------------------------------------
# Scene
# --------------------------------------------------------------------------

def fit_font(draw, text, cands, max_w, start):
    size = start
    while size > 12:
        f = font(cands, size)
        if draw.textlength(text, font=f) <= max_w * SS:
            return f, size
        size -= 2
    return font(cands, size), size


def main():
    img = Image.new("RGB", (S(W), S(W)), MINT_TOP)
    dr = ImageDraw.Draw(img, "RGBA")
    # vertical gradient background
    for yy in range(S(W)):
        t = yy / S(W)
        col = tuple(int(MINT_TOP[i] + (MINT_BOT[i] - MINT_TOP[i]) * t) for i in range(3))
        dr.line([(0, yy), (S(W), yy)], fill=col)
    # faint medical crosses in the background
    for (cx, cy, r) in [(90, 130, 26), (1085, 300, 20), (140, 1020, 22), (1020, 90, 16), (90, 560, 15)]:
        a = 46
        dr.rectangle([S(cx - r), S(cy - r // 3), S(cx + r), S(cy + r // 3)], fill=(255, 255, 255, a))
        dr.rectangle([S(cx - r // 3), S(cy - r), S(cx + r // 3), S(cy + r)], fill=(255, 255, 255, a))

    # ---- note card (drawn on its own layer, rotated slightly) ----
    card = Image.new("RGBA", (S(1120), S(1080)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card, "RGBA")
    cd.rounded_rectangle([S(14), S(14), S(1106), S(1066)], radius=S(26), fill=PAPER + (255,))
    # header: magenta cross badge + clinic name
    cd.rounded_rectangle([S(56), S(52), S(120), S(116)], radius=S(14), fill=MAGENTA + (255,))
    cd.rectangle([S(80), S(66), S(96), S(102)], fill=(255, 255, 255, 255))
    cd.rectangle([S(66), S(80), S(110), S(88 + 8)], fill=(255, 255, 255, 255))
    f_clinic, _ = fit_font(cd, "LEONIDA MEDICAL CENTRE", FONT_CANDIDATES_BOLD, 560, 43)
    cd.text((S(142), S(62)), "LEONIDA MEDICAL CENTRE", font=f_clinic, fill=INK + (255,))
    f_sub = font(FONT_CANDIDATES_REG, 27)
    cd.text((S(142), S(112)), "Department of Launch-Day Health", font=f_sub, fill=GREY + (255,))
    cd.line([S(56), S(150), S(1064), S(150)], fill=(226, 222, 225, 255), width=S(3))
    # title
    f_title = font(FONT_CANDIDATES_BOLD, 118)
    cd.text((S(54), S(176)), "SICK NOTE", font=f_title, fill=INK + (255,))
    cd.rectangle([S(58), S(316), S(398), S(328)], fill=MAGENTA + (255,))

    # fields (label, value, start size, max width) — the last two rows keep
    # their right side clear for the ghost standing at the bottom-right.
    rows = [
        ("PATIENT", "EVERYONE", 56, 880),
        ("DIAGNOSIS", "LEONIDA FEVER", 56, 880),
        ("TIME OFF", "NOV 19 — UNTIL FURTHER NOTICE", 52, 880),
        ("PRESCRIPTION", "GTA VI. NO WORK. NO EMAILS.", 50, 640),
        ("TREATMENT BILL", "PAID BY MY AI AGENT ON make.fun", 46, 640),
    ]
    y = 366
    f_label = font(FONT_CANDIDATES_REG, 27)
    for label, value, vsize, vmax in rows:
        cd.text((S(58), S(y)), label, font=f_label, fill=GREY + (255,))
        f_val, _ = fit_font(cd, value, FONT_CANDIDATES_BOLD, vmax, vsize)
        cd.text((S(58), S(y + 34)), value, font=f_val, fill=INK + (255,))
        # dotted rule
        ry = y + 98
        x = 58
        while x < 1000:
            cd.ellipse([S(x), S(ry), S(x + 5), S(ry + 5)], fill=(190, 184, 190, 255))
            x += 18
        y += 112
    # signature block (bottom-left): squiggle first, printed name under it
    sig = []
    for i in range(61):
        t = i / 60
        sig.append((S(70 + t * 250), S(986 + math.sin(t * 9.0) * 10 * (1 - t) - t * 6)))
    cd.line(sig, fill=INK + (255,), width=S(4), joint="curve")
    f_sig = font(FONT_CANDIDATES_BOLDITALIC, 32)
    cd.text((S(70), S(1008)), "Dr. Ghost, MD", font=f_sig, fill=INK + (255,))

    # EXCUSED stamp over the empty top-right of the note
    stamp = Image.new("RGBA", (S(400), S(180)), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp, "RGBA")
    sd.rounded_rectangle([S(10), S(28), S(390), S(152)], radius=S(16), outline=MAGENTA + (215,), width=S(8))
    sd.rounded_rectangle([S(26), S(42), S(374), S(138)], radius=S(11), outline=MAGENTA + (150,), width=S(3))
    f_stamp, _ = fit_font(sd, "EXCUSED", FONT_CANDIDATES_BOLD, 300, 78)
    tw = sd.textlength("EXCUSED", font=f_stamp)
    sd.text(((S(400) - tw) / 2, S(52)), "EXCUSED", font=f_stamp, fill=MAGENTA + (225,))
    stamp_r = stamp.rotate(12, resample=Image.BICUBIC, expand=True)
    card.paste(stamp_r, (S(672), S(150)), stamp_r)

    card_r = card.rotate(1.4, resample=Image.BICUBIC, expand=False)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 110))
    shadow.paste(sh.rotate(1.4, resample=Image.BICUBIC, expand=False), (S(48), S(66)), sh.rotate(1.4, resample=Image.BICUBIC, expand=False))
    shadow = shadow.filter(ImageFilter.GaussianBlur(S(10)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
    img.paste(card_r, (S(40), S(30)), card_r)
    dr = ImageDraw.Draw(img, "RGBA")

    # ---- ghost doctor, standing at the note's bottom-right ----
    ghost = render_ghost(S(340))
    gx, gy = 790, 806
    # soft shadow under ghost, then paste
    gshadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gs = Image.new("RGBA", ghost.size, (0, 0, 0, 90))
    gshadow.paste(gs, (S(gx + 4), S(gy + 4)), ghost)
    gshadow = gshadow.filter(ImageFilter.GaussianBlur(S(8)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), gshadow).convert("RGB"), (0, 0))
    img.paste(ghost, (S(gx), S(gy)), ghost)
    dr = ImageDraw.Draw(img, "RGBA")
    # doctor's head mirror, drawn on the main image so nothing clips:
    # band across the forehead, mirror disc just above it.
    hx = gx + 0.42 * 340
    band_y = gy + 30
    dr.rounded_rectangle([S(hx - 60), S(band_y - 8), S(hx + 60), S(band_y + 8)],
                         radius=S(8), fill=(70, 70, 78, 255))
    mr = 26
    cy_m = band_y - 16
    dr.ellipse([S(hx - mr), S(cy_m - mr), S(hx + mr), S(cy_m + mr)], fill=(212, 216, 222, 255),
               outline=INK + (255,), width=S(3))
    dr.ellipse([S(hx - 8), S(cy_m - 8), S(hx + 8), S(cy_m + 8)], fill=INK + (255,))

    out = img.resize((W, W), Image.LANCZOS)
    path = os.path.join(HERE, "meme.png")
    out.save(path, "PNG")
    print(f"wrote {path} {os.path.getsize(path)} bytes")


if __name__ == "__main__":
    sys.exit(main())
