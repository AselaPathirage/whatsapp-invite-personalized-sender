"""
======================================================================
  Wedding Invitation Personalizer (batch)
======================================================================
  HOW TO USE
  1. Put your base card path in BASE_IMAGE below.
  2. Choose a FONT (uncomment one).
  3. List your guests in GUESTS (one name per line), OR put them in a
     file called  guests.txt  (one name per line) and set USE_FILE=True.
  4. Run:   python make_invitations.py
  5. Finished PNGs land in the  ./invitations/  folder, one per guest.

======================================================================
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- SETUP
BASE_IMAGE = "base_inv.png"      # <-- your base invitation

# Pick ONE font (download the .ttf into a ./fonts/ folder):
FONT = "fonts/GreatVibes.ttf"      # elegant wedding script  (recommended)
# FONT = "fonts/Tangerine.ttf"     # fine calligraphy
# FONT = "fonts/Playfair.ttf"      # classic serif (matches the names)
# FONT = "fonts/Poppins.ttf"       # clean printed (matches body text)

USE_FILE = True                   # True = read names from guests.txt
GUESTS = [
    "Mr. & Mrs. Fernando",
    "The Perera Family"
]

# ---------------------------------------------------- CARD GEOMETRY
# (measured from the card — leave as-is unless you
#  change the base image)
CENTER_X   = 714
BASELINE_Y = 1150
MAX_WIDTH  = 800
TOP_LIMIT  = 1060           # name won't rise above this (clear of "INVITING")
BOTTOM_LIMIT = 1190         # descenders won't drop below this (16px above "TO CELEBRATE")
MAX_FONT_SIZE = 100         # never render a name LARGER than this (keeps sizes consistent)
INK        = (116, 81, 30)         # warm brown, matches the card

# ---------------------------------------------------------------- ENGINE
def _fit_font(font_path, text, max_width, max_ascent, max_descent, max_size=MAX_FONT_SIZE):
    # measure with anchor='ls' (origin on the baseline) so -top is the TRUE
    # height above the baseline, and b is the TRUE depth below it. The search
    # is also capped at max_size so short names don't balloon.
    lo, hi, best = 8, max_size, 8
    while lo <= hi:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(font_path, mid)
        l, t, r, b = f.getbbox(text, anchor="ls")
        if (r - l) <= max_width and (-t) <= max_ascent and b <= max_descent:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return ImageFont.truetype(font_path, best)

def personalize(name, base, font_path, out_path):
    img = Image.open(base).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = _fit_font(font_path, name, MAX_WIDTH,
                     BASELINE_Y - TOP_LIMIT, BOTTOM_LIMIT - BASELINE_Y)
    draw.text((CENTER_X, BASELINE_Y), name, font=font, fill=INK, anchor="ms")
    img.save(out_path, "PNG")

def safe_filename(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "guest"

# ---------------------------------------------------------------- RUN
if __name__ == "__main__":
    names = GUESTS
    if USE_FILE:
        names = [ln.strip() for ln in Path("guests.txt").read_text().splitlines() if ln.strip()]

    outdir = Path("invitations")
    outdir.mkdir(exist_ok=True)

    for n in names:
        out = outdir / f"A_A_{safe_filename(n)}.png"
        personalize(n, BASE_IMAGE, FONT, out)
        print("  saved", out)

    print(f"\nDone — {len(names)} invitation(s) in ./invitations/")