#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-selezione hero (immagine in evidenza) + logo per ogni certificazione,
dalle cartelle disordinate del cliente. Scarta i file di ispirazione
(IDEE/INSPO/IDEA), classifica per aspect-ratio/alpha/nome, e genera:
  - tools/images_selection.json   (scelte + candidati + confidenza)
  - tools/contact_sheet_1.png / _2.png  (prospetto visivo per conferma)

NB: build-time. La scelta definitiva è dell'utente (conferma sul contact sheet).
"""
import os, glob, json, re
from PIL import Image, ImageDraw, ImageFont

ROOT = "/tmp/maci-src/loghi iso e certificazioni"
OUT_JSON = os.path.join(os.path.dirname(__file__), "images_selection.json")

# Mappa certificazione -> cartella immagini (nomi cartelle irregolari).
FOLDERS = {
    "UNI/PdR 125": "ISO 27001/UNI PDR 125 2022",
    "Modello 231": "IL MODELLO 231",
    "ISO 9001":    "ISO 9001",
    "ISO 14001":   "ISO 14001",
    "ISO 14064":   "ISO 14064",
    "ISO 15189":   "ISO 15189 DA INSERIRE INSIEME  PER CAPIRE COME FARE",
    "ISO 20121":   None,  # nessuna cartella dedicata
    "ISO 22000":   "ISO 22000",
    "ISO 22301":   "ISO 22301",
    "PAS 24000":   "PAS-2400 2022",
    "ISO 27001":   "ISO 27001",
    "ISO 31000":   "ISO 31000",
    "ISO 37001":   "ISO 37001",
    "ISO 42001":   "ISO 42001",
    "ISO 45001":   "ISO 45001",
    "ISO 50001":   "ISO 50001 2018",
    "ISO 55001":   "ISO 55001 2014",
    "Marcatura CE": "COPERTINA SICUREZZA MACCHINE EMARCATURA CE",
}
COVER_ISO = "COPERTINA CERTIFICAZIONI ISO"  # fallback hero per ISO senza cartella

NOISE = re.compile(r"(idee|idea|inspo|inps)", re.I)

def is_noise(name):
    stem = os.path.splitext(os.path.basename(name))[0]
    return bool(NOISE.search(stem)) or stem.lower().startswith("images")

def candidates(folder):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, folder, "*"))):
        if os.path.isdir(f):
            continue
        try:
            im = Image.open(f); w, h = im.size
        except Exception:
            continue
        out.append({
            "path": f, "name": os.path.basename(f), "w": w, "h": h,
            "ar": round(w / h, 3), "fmt": im.format,
            "alpha": im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info),
            "area": w * h, "noise": is_noise(f),
        })
    return out

def pick_hero(cands):
    # landscape, non-noise, area grande
    def score(c):
        s = c["area"]
        if 1.4 <= c["ar"] <= 2.1: s *= 2.0
        elif 1.2 <= c["ar"] < 1.4: s *= 1.3
        elif c["ar"] < 1.0: s *= 0.3
        if c["noise"]: s *= 0.15
        if c["w"] < 500: s *= 0.4
        return s
    return max(cands, key=score) if cands else None

def pick_logo(cands, hero):
    # quadrato, preferenza alpha/png, non = hero
    pool = [c for c in cands if c is not hero]
    def score(c):
        s = 1000.0
        if 0.8 <= c["ar"] <= 1.25: s *= 3.0
        elif 1.25 < c["ar"] <= 1.5: s *= 1.2
        else: s *= 0.3
        if c["alpha"]: s *= 1.8
        if c["fmt"] in ("PNG", "WEBP"): s *= 1.3
        if c["noise"]: s *= 0.2
        if c["w"] < 150: s *= 0.4
        return s
    return max(pool, key=score) if pool else None

def select():
    items = [x["title"] for x in json.load(open(os.path.join(os.path.dirname(__file__), "manifest.json")))]
    sel = {}
    for title in items:
        folder = FOLDERS.get(title)
        cands = candidates(folder) if folder else []
        if not cands and title.startswith("ISO"):
            cands = candidates(COVER_ISO)  # fallback hero generico
        hero = pick_hero(cands)
        logo = pick_logo(cands, hero)
        only_noise = bool(cands) and all(c["noise"] for c in cands)
        sel[title] = {
            "folder": folder,
            "hero": hero["name"] if hero else None,
            "logo": logo["name"] if logo else None,
            "candidates": [c["name"] for c in cands],
            "low_confidence": (not cands) or only_noise or (logo is None),
            "_cands": cands,  # per il contact sheet
        }
    return sel

# ---------- Contact sheet ----------
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def thumb(c, box):
    im = Image.open(c["path"]).convert("RGB")
    im.thumbnail(box)
    bg = Image.new("RGB", box, (245, 245, 245))
    bg.paste(im, ((box[0]-im.width)//2, (box[1]-im.height)//2))
    return bg

def build_sheet(sel, titles, path):
    TW, TH = 200, 150          # thumb
    PAD, LBL = 12, 34
    LEFTW = 150
    rowh = TH + LBL + PAD
    maxc = max(len(sel[t]["_cands"]) for t in titles) or 1
    W = LEFTW + maxc * (TW + PAD) + PAD
    H = PAD + len(titles) * rowh
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    fT, fS = font(15), font(11)
    y = PAD
    for t in titles:
        s = sel[t]
        d.text((8, y + 8), t, fill="black", font=fT)
        if s["low_confidence"]:
            d.text((8, y + 30), "⚠ verifica", fill=(200, 0, 0), font=fS)
        x = LEFTW
        for c in s["_cands"]:
            th = thumb(c, (TW, TH))
            img.paste(th, (x, y))
            role = "HERO" if c["name"] == s["hero"] else ("LOGO" if c["name"] == s["logo"] else "")
            col = (16, 150, 60) if role == "HERO" else (30, 90, 200) if role == "LOGO" else (210, 210, 210)
            d.rectangle([x, y, x + TW, y + TH], outline=col, width=4 if role else 1)
            if role:
                d.rectangle([x, y, x + 54, y + 18], fill=col)
                d.text((x + 4, y + 3), role, fill="white", font=fS)
            nm = (c["name"][:30] + "…") if len(c["name"]) > 31 else c["name"]
            d.text((x, y + TH + 2), nm, fill=(60, 60, 60), font=fS)
            d.text((x, y + TH + 16), f'{c["w"]}x{c["h"]}', fill=(120, 120, 120), font=fS)
            x += TW + PAD
        y += rowh
    img.save(path)
    return path

def main():
    sel = select()
    titles = list(sel.keys())
    half = (len(titles) + 1) // 2
    p1 = build_sheet(sel, titles[:half], os.path.join(os.path.dirname(__file__), "contact_sheet_1.png"))
    p2 = build_sheet(sel, titles[half:], os.path.join(os.path.dirname(__file__), "contact_sheet_2.png"))
    # salva json pulito (senza _cands)
    clean = {t: {k: v for k, v in s.items() if k != "_cands"} for t, s in sel.items()}
    json.dump(clean, open(OUT_JSON, "w"), ensure_ascii=False, indent=2)
    for t, s in clean.items():
        print(f"{t:13} hero={str(s['hero'])[:34]:34} logo={str(s['logo'])[:28]:28} {'⚠' if s['low_confidence'] else ''}")
    print("\nContact sheet:", p1, p2)

if __name__ == "__main__":
    main()
