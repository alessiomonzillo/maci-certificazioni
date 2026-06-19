#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera il file di import WordPress (WXR) per la nuova certificazione "PED"
(categoria Macchine), distinta da "Marcatura CE".

Particolarità: il docx PED contiene tabelle (box "Sintesi Normativa" e tabella
"Moduli di Conformità"). Questo parser è TABLE-AWARE: cammina il <w:body> in
ordine processando sia i paragrafi <w:p> (con stili Word) sia le tabelle <w:tbl>,
e produce HTML con <h2>/<h3>/<ul>/<table>.

Output: import/certificazione-ped.wxr.xml (1 post + termine Macchine, nessun allegato).
NB: build-time, non gira nel runtime WordPress.
"""
import os, re, zipfile, html, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(__file__), "sources", "Certificazione_PED.docx")
OUT = os.path.join(BASE, "import", "certificazione-ped.wxr.xml")

TITLE = "Certificazione PED"
SLUG = "certificazione-ped"
SUBTITLE = "Guida Tecnica ai Requisiti, Classificazione di Rischio e Valutazione della Conformità"
CATEGORY = "Macchine"
MENU_ORDER = 19
NOW = "2026-06-19 10:00:00"

def runs_text(xml_fragment):
    """Testo concatenato dei <w:t> di un frammento, ripulito."""
    # NB: <w:t(?:\s...)?> per non agganciare per errore <w:tcW>, <w:tcPr>, <w:tab/> ecc.
    t = "".join(re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", xml_fragment, re.S))
    t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
           .replace("&quot;", '"').replace("&#39;", "'"))
    return re.sub(r"\s+", " ", t).strip()

def para_role(p_xml):
    sty = re.search(r'<w:pStyle w:val="([^"]+)"', p_xml)
    style = (sty.group(1) if sty else "").lower()
    if style in ("titolo", "title"):
        return "title"
    if style in ("titolo1", "heading1"):
        return "heading"
    if style.startswith("titolo") or style.startswith("heading"):
        return "subheading"
    if "elenco" in style or "list" in style or "punto" in style:
        return "list"
    return "para"

def parse_table(tbl_xml):
    """Ritorna lista di righe; ogni riga = lista di celle (testo)."""
    rows = []
    for tr in re.findall(r"<w:tr\b[^>]*>(.*?)</w:tr>", tbl_xml, re.S):
        cells = [runs_text(tc) for tc in re.findall(r"<w:tc>(.*?)</w:tc>", tr, re.S)]
        rows.append(cells)
    return rows

def table_html(rows):
    if not rows:
        return ""
    # tabella a cella unica = box/callout evidenziato
    if len(rows) == 1 and len(rows[0]) == 1:
        return '<table class="mas-cert-callout"><tbody><tr><td>%s</td></tr></tbody></table>' % html.escape(rows[0][0], quote=False)
    out = ["<table>"]
    head, body = rows[0], rows[1:]
    out.append("<thead><tr>" + "".join("<th>%s</th>" % html.escape(c, quote=False) for c in head) + "</tr></thead>")
    out.append("<tbody>")
    for r in body:
        out.append("<tr>" + "".join("<td>%s</td>" % html.escape(c, quote=False) for c in r) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)

def build():
    xml = zipfile.ZipFile(SRC).read("word/document.xml").decode("utf-8", "ignore")
    body = re.search(r"<w:body>(.*)</w:body>", xml, re.S).group(1)

    # Cammina top-level: paragrafi e tabelle in ordine di documento.
    blocks = []
    for m in re.finditer(r"<w:tbl>.*?</w:tbl>|<w:p\b.*?</w:p>", body, re.S):
        frag = m.group(0)
        if frag.startswith("<w:tbl"):
            blocks.append({"type": "table", "rows": parse_table(frag)})
        else:
            txt = runs_text(frag)
            if txt:
                blocks.append({"type": "para", "role": para_role(frag), "text": txt})

    # title_line + subtitle (li abbiamo fissi da decisione utente)
    excerpt = ""
    out, ul_open = [], False
    def close_ul():
        nonlocal ul_open
        if ul_open:
            out.append("</ul>"); ul_open = False

    title_seen = False
    for b in blocks:
        if b["type"] == "table":
            close_ul()
            out.append(table_html(b["rows"]))
            continue
        role, t = b["role"], b["text"]
        esc = html.escape(t, quote=False)
        if role == "title" or (not title_seen and role == "para" and t.upper().startswith("LA CERTIFICAZIONE PED")):
            title_seen = True
            continue  # il titolo va nel post_title, non nel contenuto
        if not title_seen and role == "para" and t == SUBTITLE:
            continue
        # salta la riga sottotitolo se ripetuta
        if t == SUBTITLE:
            continue
        if role == "heading":
            close_ul(); out.append("<h2>%s</h2>" % esc)
        elif role == "subheading":
            close_ul(); out.append("<h3>%s</h3>" % esc)
        elif role == "list":
            if not ul_open:
                out.append("<ul>"); ul_open = True
            out.append("<li>%s</li>" % esc)
        else:
            # primo paragrafo lungo = excerpt (intro), non entra nel contenuto
            if not excerpt and len(t) > 60:
                excerpt = t; continue
            close_ul(); out.append("<p>%s</p>" % esc)
    close_ul()
    content_html = "\n".join(out)
    return content_html, excerpt

def cdata(s):
    s = s or ""
    return "<![CDATA[" + s.replace("]]>", "]]]]><![CDATA[>") + "]]>"

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    content_html, excerpt = build()

    item = (
        "\t<item>\n"
        f"\t\t<title>{html.escape(TITLE)}</title>\n"
        "\t\t<link></link>\n"
        f"\t\t<dc:creator>{cdata('admin')}</dc:creator>\n"
        f"\t\t<guid isPermaLink=\"false\">cert-{SLUG}</guid>\n"
        "\t\t<description></description>\n"
        f"\t\t<content:encoded>{cdata(content_html)}</content:encoded>\n"
        f"\t\t<excerpt:encoded>{cdata(excerpt)}</excerpt:encoded>\n"
        "\t\t<wp:post_id>1200</wp:post_id>\n"
        f"\t\t<wp:post_date>{cdata(NOW)}</wp:post_date>\n"
        f"\t\t<wp:post_date_gmt>{cdata(NOW)}</wp:post_date_gmt>\n"
        f"\t\t<wp:post_name>{cdata(SLUG)}</wp:post_name>\n"
        "\t\t<wp:status><![CDATA[publish]]></wp:status>\n"
        "\t\t<wp:post_parent>0</wp:post_parent>\n"
        f"\t\t<wp:menu_order>{MENU_ORDER}</wp:menu_order>\n"
        "\t\t<wp:post_type><![CDATA[mas_certificazione]]></wp:post_type>\n"
        "\t\t<wp:post_password></wp:post_password>\n"
        "\t\t<wp:is_sticky>0</wp:is_sticky>\n"
        f"\t\t<category domain=\"mas_cert_categoria\" nicename=\"macchine\">{cdata(CATEGORY)}</category>\n"
        "\t\t<wp:postmeta>\n"
        f"\t\t\t<wp:meta_key>{cdata('_mas_cert_sottotitolo')}</wp:meta_key>\n"
        f"\t\t\t<wp:meta_value>{cdata(SUBTITLE)}</wp:meta_value>\n"
        "\t\t</wp:postmeta>\n"
        "\t</item>\n"
    )
    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<rss version=\"2.0\"\n"
        "  xmlns:excerpt=\"http://wordpress.org/export/1.2/excerpt/\"\n"
        "  xmlns:content=\"http://purl.org/rss/1.0/modules/content/\"\n"
        "  xmlns:wfw=\"http://wellformedweb.org/CommentAPI/\"\n"
        "  xmlns:dc=\"http://purl.org/dc/elements/1.1/\"\n"
        "  xmlns:wp=\"http://wordpress.org/export/1.2/\">\n"
        "<channel>\n"
        "\t<title>MA.CI Certificazioni - PED</title>\n"
        "\t<link>https://www.masprevenzione.it</link>\n"
        "\t<description>Import certificazione PED</description>\n"
        f"\t<pubDate>{datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>\n"
        "\t<language>it-IT</language>\n"
        "\t<wp:wxr_version>1.2</wp:wxr_version>\n"
        "\t<wp:base_site_url>https://www.masprevenzione.it</wp:base_site_url>\n"
        "\t<wp:base_blog_url>https://www.masprevenzione.it</wp:base_blog_url>\n"
        "\t<wp:author><wp:author_id>1</wp:author_id><wp:author_login><![CDATA[admin]]></wp:author_login>"
        "<wp:author_email><![CDATA[]]></wp:author_email><wp:author_display_name><![CDATA[admin]]></wp:author_display_name>"
        "<wp:author_first_name><![CDATA[]]></wp:author_first_name><wp:author_last_name><![CDATA[]]></wp:author_last_name></wp:author>\n"
        "\t<wp:term><wp:term_id>102</wp:term_id><wp:term_taxonomy>mas_cert_categoria</wp:term_taxonomy>"
        "<wp:term_slug>macchine</wp:term_slug><wp:term_name><![CDATA[Macchine]]></wp:term_name></wp:term>\n"
    )
    foot = "</channel>\n</rss>\n"
    open(OUT, "w", encoding="utf-8").write(head + item + foot)
    print("Excerpt:", excerpt[:160])
    print("\nContent HTML:\n", content_html)
    print("\nWXR ->", OUT)

if __name__ == "__main__":
    main()
