#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estrae i testi delle certificazioni MA.CI da DOCX (stdlib, via stili Word) e
PDF (OCR tesseract, i pdf forniti sono immagini), li normalizza nei campi del
plugin e produce tools/manifest.json.

Ruoli blocco: 'title' | 'heading' | 'list' | 'para'.
NB: script "di build", non gira nel runtime WordPress.
"""
import json, os, re, zipfile, glob, html

SRC = "/tmp/maci-src/TESTI DA INSERIRE SITO"
OUT = os.path.join(os.path.dirname(__file__), "manifest.json")

# ---------- DOCX (per stili Word) ----------
def docx_blocks(path):
    z = zipfile.ZipFile(path)
    xml = z.read("word/document.xml").decode("utf-8", "ignore")
    blocks = []
    for p in re.split(r"</w:p>", xml):
        texts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S)
        line = "".join(texts)
        line = (line.replace("&amp;", "&").replace("&lt;", "<")
                    .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
        line = clean_text(line.strip())
        if not line:
            continue
        sty = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        style = (sty.group(1) if sty else "").lower()
        if style in ("titolo", "title"):
            role = "title"
        elif style in ("titolo1", "heading1"):
            role = "heading"            # H2 (sezione numerata)
        elif style.startswith("titolo") or style.startswith("heading"):
            role = "subheading"         # H3 (Titolo2/3)
        elif "numeroelenco" in style or "listnumber" in style:
            role = "olist"              # elenco numerato <ol>
        elif "elenco" in style or "list" in style or "punto" in style:
            role = "list"               # elenco puntato <ul>
        elif re.match(r"^\d+\.\s+\S", line):
            role = "heading"
        else:
            role = "para"
        blocks.append({"text": line, "role": role})
    return blocks

# ---------- PDF (OCR) ----------
# Artefatti OCR dei bullet: '•' diventa spesso 'e', '©', '®', '*', '-', '°'.
BULLET = re.compile(r"^\s*(?:[•●▪◦°©®*]|[eE](?=\s+[A-ZÀ-Ù]))\s+")

def pdf_blocks(path):
    import fitz, io, pytesseract
    from PIL import Image
    doc = fitz.open(path)
    raw = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        raw.append(pytesseract.image_to_string(img, lang="ita"))
    text = "\n".join(raw)
    blocks = []
    for para in re.split(r"\n\s*\n", text):
        lines = [l.strip() for l in para.splitlines() if l.strip()]
        if not lines:
            continue
        joined = clean_text(" ".join(lines))
        if re.match(r"^\d+\.\s+\S", joined):
            blocks.append({"text": joined, "role": "heading"})
        elif any(BULLET.match(l) for l in lines):
            cur = None
            for l in lines:
                if BULLET.match(l):
                    if cur:
                        blocks.append({"text": clean_text(cur), "role": "list"})
                    cur = BULLET.sub("", l).strip()
                else:
                    cur = (cur + " " + l).strip() if cur else l
            if cur:
                blocks.append({"text": clean_text(cur), "role": "list"})
        else:
            blocks.append({"text": joined, "role": "para"})
    # Fix OCR: heading numerato spezzato ("1." isolato, titolo nel blocco dopo).
    merged, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        if re.fullmatch(r"\d+\.?", b["text"].strip()) and i + 1 < len(blocks):
            merged.append({"text": b["text"].strip().rstrip(".") + ". " + blocks[i + 1]["text"], "role": "heading"})
            i += 2
        else:
            merged.append(b); i += 1
    # Fix OCR: "N. Termine: definizione lunga" è in realtà un bullet, non una sezione.
    for b in merged:
        if b["role"] == "heading":
            m = re.match(r"^\d+\.\s+(.*)", b["text"])
            if m and ":" in m.group(1) and len(m.group(1)) > 55:
                b["role"] = "list"; b["text"] = m.group(1)
    return merged

# ---------- pulizia testo ----------
def clean_text(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(\d{4,5})([A-Za-zÀ-ù])", r"\1 \2", s)   # "15189nei" -> "15189 nei"
    return s

# ---------- titolo/sottotitolo ----------
YEAR = re.compile(r":?\s*20\d{2}\b")
CODE = re.compile(r"(ISO\s*/?\s*IEC\s*\d+|ISO\s*\d+|UNI\s*/?\s*PdR\s*\d+|PAS\s*\d+)", re.I)
ACCENTI = {"Qualita": "Qualità", "Sostenibilita": "Sostenibilità", "Parita": "Parità",
           "Continuita": "Continuità", "Responsabilita": "Responsabilità", "Citta": "Città"}

def fix_accents(s):
    for a, b in ACCENTI.items():
        s = re.sub(r"\b" + a + r"\b", b, s)
    return s

def strip_lead(s):
    return re.sub(r"^[\s:–\-—,]+", "", s).strip()

def decode_fname(fname):
    base = os.path.splitext(fname)[0]
    base = re.sub(r"#U([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), base)
    return base.lstrip("_").strip()

def norm_code(code):
    code = re.sub(r"\s+", " ", code).strip()
    code = re.sub(r"(?i)uni\s*/?\s*pdr", "UNI/PdR", code)
    code = re.sub(r"(?i)iso\s*/?\s*iec\s*", "ISO ", code)  # -> "ISO NNNN"
    code = re.sub(r"(?i)^iso", "ISO", code)
    code = re.sub(r"(?i)^pas", "PAS", code)
    return code

def title_from_filename(fname):
    """Titolo canonico + sottotitolo di fallback dal NOME FILE (affidabile)."""
    base = re.sub(r"\s+", " ", decode_fname(fname).replace("_", " ")).strip()
    low = base.lower()
    if "modello 231" in low:
        return "Modello 231", ""
    if "marcatura" in low or "sicurezza macchine" in low:
        return "Marcatura CE", "Guida alla Conformità Europea"
    if "15189" in low:
        return "ISO 15189", ""
    m = CODE.search(base)
    if m:
        return norm_code(m.group(1)), fix_accents(strip_lead(base[m.end():]))
    return base, ""

def doc_subtitle(title_line):
    """Sottotitolo ricavato dalla riga-titolo del documento (dopo il codice)."""
    m = CODE.search(title_line)
    if not m:
        return ""
    rest = strip_lead(YEAR.sub("", title_line[m.end():]))
    return rest

def good_subtitle(s):
    if not s or len(s) > 85 or s[0].islower() or re.match(r"^(è|e)\b", s):
        return False
    return True

# ---------- HTML ----------
def build_html(blocks):
    out = []
    cur_list = None  # None | 'ul' | 'ol'
    def close_list():
        nonlocal cur_list
        if cur_list:
            out.append("</%s>" % cur_list); cur_list = None
    def open_list(kind):
        nonlocal cur_list
        if cur_list != kind:
            close_list(); out.append("<%s>" % kind); cur_list = kind
    esc = lambda t: html.escape(t, quote=False)  # apostrofi/virgolette restano leggibili nel CDATA
    for b in blocks:
        t, role = b["text"], b["role"]
        if role == "heading":
            close_list(); out.append("<h2>%s</h2>" % esc(t))
        elif role == "subheading":
            close_list(); out.append("<h3>%s</h3>" % esc(t))
        elif role == "list":
            open_list("ul"); out.append("<li>%s</li>" % esc(t))
        elif role == "olist":
            open_list("ol"); out.append("<li>%s</li>" % esc(t))
        else:
            close_list(); out.append("<p>%s</p>" % esc(t))
    close_list()
    return "\n".join(out)

# ---------- categoria / ordine ----------
def category(fname):
    low = fname.lower()
    return "Macchine" if ("marcatura" in low or "sicurezza_macchine" in low) else "ISO"

def order_key(title):
    m = re.search(r"(\d{3,5})", title)
    return int(m.group(1)) if m else 99999

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("/", "-")).strip("-")

def process(path):
    fname = os.path.basename(path)
    blocks = docx_blocks(path) if fname.lower().endswith(".docx") else pdf_blocks(path)
    if not blocks:
        return {"source": fname, "error": "no text extracted"}

    title, sub_fb = title_from_filename(fname)

    # riga-titolo del documento: blocco role title, altrimenti il primo
    title_line = next((b["text"] for b in blocks if b["role"] == "title"), blocks[0]["text"])
    ds = doc_subtitle(title_line)
    subtitle = ds if good_subtitle(ds) else sub_fb

    # Casi speciali (titolo senza codice norma nella 1ª riga).
    low = fname.lower()
    if not subtitle and "modello 231" in low:
        subtitle = "Integrazione con i Sistemi di Gestione ISO"
    if "15189" in low:
        subtitle = next((b["text"] for b in blocks[:4]
                         if "importanza" in b["text"].lower()), subtitle)

    # excerpt = primo paragrafo "corpo" lungo, diverso da titolo e sottotitolo
    excerpt_idx, excerpt = None, ""
    for i, b in enumerate(blocks):
        if b["role"] == "para" and len(b["text"]) > 40 \
           and b["text"] != title_line and b["text"] != subtitle:
            excerpt_idx, excerpt = i, b["text"]; break

    # contenuto = blocchi dopo l'excerpt (esclude titolo/sottotitolo/remnant iniziali),
    # togliendo l'eventuale ripetizione del sottotitolo
    start = (excerpt_idx + 1) if excerpt_idx is not None else 0
    content_blocks = [b for b in blocks[start:] if b["text"] != subtitle]
    content_html = build_html(content_blocks)

    return {
        "source": fname,
        "title": title,
        "subtitle": subtitle or "",
        "excerpt": excerpt,
        "content_html": content_html,
        "category": category(fname),
        "slug": slugify(title),
        "order": order_key(title),
        "n_sections": sum(1 for b in content_blocks if b["role"] == "heading"),
        "n_list": sum(1 for b in content_blocks if b["role"] == "list"),
    }

def main():
    items = [process(p) for p in sorted(glob.glob(os.path.join(SRC, "*.docx")) +
                                        glob.glob(os.path.join(SRC, "*.pdf")))]
    items.sort(key=lambda x: (x.get("category") == "Macchine", x.get("order", 99999)))
    for i, it in enumerate(items, 1):
        it["menu_order"] = i
    json.dump(items, open(OUT, "w"), ensure_ascii=False, indent=2)
    for it in items:
        warn = "  ⚠️" if it.get("error") or not it["excerpt"] or not it["subtitle"] else ""
        print(f"[{it.get('menu_order','?'):>2}] {it['category']:8} {it['title']:14} | "
              f"sez={it.get('n_sections','?')} li={it.get('n_list','?')} "
              f"sub={'sì' if it.get('subtitle') else 'NO'} intro={'sì' if it['excerpt'] else 'NO'}{warn}")

if __name__ == "__main__":
    main()
