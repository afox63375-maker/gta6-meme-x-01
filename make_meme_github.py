#!/usr/bin/env python3
"""Second meme concept for gta6-meme-x-01: "The GTA VI Repo" (GitHub PR joke).
Reuses the press-kit ghost renderer from make_meme.py (everything before its Scene section)."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "make_meme.py")).read()
exec(src.split("# --------------------------------------------------------------------------\n# Scene")[0])

SS = 2
W = 1200
def S(v): return v * SS

BOLD = font(FONT_CANDIDATES_BOLD, 10)  # placeholder, replaced per-size below
def F(cands, size): return font(cands, size)
FB = lambda s: font(FONT_CANDIDATES_BOLD, s)
FR = lambda s: font(FONT_CANDIDATES_REG, s)

GH_DARK = (36, 41, 47)
GH_BORDER = (208, 215, 222)
GH_BG = (246, 248, 250)
GH_GREEN = (31, 136, 61)
GH_GREEN_BG = (218, 251, 225)
GH_YELLOW_BG = (255, 248, 197)
GH_TEXT = (31, 35, 40)
GH_MUTED = (89, 99, 110)
MAGENTA = (196, 28, 131)
WHITE = (255, 255, 255)

img = Image.new("RGB", (S(W), S(W)), WHITE)
d = ImageDraw.Draw(img)

def rr(box, r, **kw):
    d.rounded_rectangle([S(box[0]), S(box[1]), S(box[2]), S(box[3])], radius=S(r), **kw)
def txt(x, y, s, f, fill=GH_TEXT, anchor="la"):
    d.text((S(x), S(y)), s, font=f, fill=fill, anchor=anchor)
def tw(s, f):
    return d.textlength(s, font=f) / SS

# ---- top bar (GitHub dark) ----
d.rectangle([0, 0, S(W), S(104)], fill=GH_DARK)
# repo icon: simple book square
rr((36, 30, 80, 74), 8, outline=(255,255,255), width=S(3))
txt(100, 34, "rockstar-games", FB(40), (255,255,255))
x = 100 + tw("rockstar-games", FB(40))
txt(x + 8, 34, "/", FB(40), (140,150,160))
txt(x + 40, 34, "gta-vi", FB(40), (255,255,255))
x2 = x + 40 + tw("gta-vi", FB(40))
rr((x2 + 26, 38, x2 + 158, 74), 18, outline=(140,150,160), width=S(2))
txt(x2 + 92, 56, "Public", FR(26), (200,208,216), anchor="mm")

# ---- tabs row ----
txt(48, 128, "Code", FB(30))
txt(190, 128, "Issues", FR(30), GH_MUTED)
rr((330, 126, 520, 162), 16, fill=(230,234,238))
txt(425, 144, "2,412,907", FB(24), GH_TEXT, anchor="mm")
txt(560, 128, "Pull requests", FR(30), GH_MUTED)
rr((800, 126, 856, 162), 16, fill=(230,234,238))
txt(828, 144, "1", FB(24), GH_TEXT, anchor="mm")
d.line([S(0), S(182), S(W), S(182)], fill=GH_BORDER, width=S(2))

# ---- PR card ----
rr((48, 214, 1152, 724), 14, outline=GH_BORDER, width=S(3))
# open PR icon: green circle with branch glyph (simple)
d.ellipse([S(84), S(250), S(148), S(314)], fill=GH_GREEN)
txt(116, 282, "!", FB(40), (255,255,255), anchor="mm")
txt(176, 246, "Release GTA VI", FB(56))
txt(176 + tw("Release GTA VI", FB(56)) + 18, 258, "#6", FR(44), GH_MUTED)
txt(176, 322, "rockstar wants to merge into production", FR(32), GH_MUTED)
txt(176, 364, "opened 13 years ago · 4,745 days · still no review", FR(32), GH_MUTED)

# checks box
rr((84, 428, 1116, 584), 10, fill=GH_YELLOW_BG, outline=GH_BORDER, width=S(2))
txt(116, 452, "!", FB(36), (154,103,0))
txt(168, 454, "Some checks haven't completed yet", FB(34), (154,103,0))
txt(116, 500, "release-date — Expected · Waiting for status to be reported", FR(30), GH_TEXT)
txt(116, 540, "gameplay — Queued · price — Queued · leonida-weather — Sunny", FR(30), GH_MUTED)

# merge button (disabled)
rr((84, 616, 560, 692), 10, fill=(148, 166, 181))
txt(322, 654, "Merge pull request", FB(32), (255,255,255), anchor="mm")
txt(596, 630, "This branch has not been", FR(28), GH_MUTED)
txt(596, 666, "reviewed in 13 years", FR(28), GH_MUTED)

# ---- ghost comment ----
rr((48, 756, 1152, 1030), 14, outline=GH_BORDER, width=S(3))
rr((48, 756, 1152, 820), 14, fill=GH_BG)
d.rectangle([S(48), S(806), S(1152), S(820)], fill=GH_BG)
d.line([S(48), S(820), S(1152), S(820)], fill=GH_BORDER, width=S(2))
ghost = render_ghost(S(56))
img.paste(ghost, (S(70), S(764)), ghost)
txt(146, 772, "makefun-ghost", FB(32), MAGENTA)
rr((146 + tw("makefun-ghost", FB(32)) + 20, 768, 146 + tw("makefun-ghost", FB(32)) + 262, 808), 8, outline=MAGENTA, width=S(2))
txt(146 + tw("makefun-ghost", FB(32)) + 141, 788, "COLLABORATOR", FB(22), MAGENTA, anchor="mm")
txt(84, 850, "I stopped waiting. My human's AI agent earns real", FR(36))
txt(84, 900, "money in bounties on make.fun now — it already", FR(36))
txt(84, 950, "paid for launch day. Merge this whenever. — Dr. Ghost", FR(36))

# ---- footer ----
d.rectangle([0, S(1056), S(W), S(W)], fill=GH_BG)
d.line([S(0), S(1056), S(W), S(1056)], fill=GH_BORDER, width=S(2))
txt(600, 1092, "last commit: \"initial commit\" — May 2013 · 0 releases · 1 very patient ghost", FB(30), GH_MUTED, anchor="ma")

img = img.resize((W, W), Image.LANCZOS)
img.save(os.path.join(HERE, "meme-github.png"))
img.resize((480, 480), Image.LANCZOS).save(os.path.join(HERE, "meme-github-480.png"))
print("saved meme-github.png", os.path.getsize(os.path.join(HERE, "meme-github.png")), "bytes")
