#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copia le immagini hero/logo scelte in import-assets/ (con nomi deterministici,
convertendo formati non sicuri per WP come .avif in .png) e genera il file di
import WordPress (WXR) import/certificazioni.wxr.xml.

Il WXR contiene: termini tassonomia (ISO/Macchine), allegati hero+logo (scaricati
dall'importer via raw URL GitHub) e i post mas_certificazione con campi e meta.
La featured image usa _thumbnail_id (rimappato dall'importer); il logo usa un
marker _mas_cert_is_logo_for risolto dal plugin dopo l'import. In più, un marker
_mas_cert_is_hero_for permette al plugin di reimpostare la featured image in modo
robusto, indipendentemente dalla versione dell'importer.
"""
import os, json, shutil, re, html, datetime
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
ASSETS = os.path.join(BASE, "import-assets")
OUT = os.path.join(BASE, "import", "certificazioni.wxr.xml")
SRC_ROOT = "/tmp/maci-src/loghi iso e certificazioni"
COVER_ISO = "COPERTINA CERTIFICAZIONI ISO"
RAW = "https://raw.githubusercontent.com/alessiomonzillo/maci-certificazioni/main/import-assets/"

SAFE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}  # formati accettati da WP
NOW = "2026-06-19 10:00:00"

def find_src(folder, name):
    """Trova il file sorgente (può stare nella cartella cert o nella copertina ISO)."""
    for base in ([folder] if folder else []) + [COVER_ISO]:
        p = os.path.join(SRC_ROOT, base, name)
        if os.path.exists(p):
            return p
    # ricerca ricorsiva di sicurezza
    for root, _, files in os.walk(SRC_ROOT):
        if name in files:
            return os.path.join(root, name)
    return None

def copy_asset(src, dest_stem):
    """Copia in import-assets/ con estensione sicura; converte avif->png. Ritorna filename."""
    ext = os.path.splitext(src)[1].lower()
    if ext not in SAFE_EXT:
        dest = dest_stem + ".png"
        Image.open(src).convert("RGBA").save(os.path.join(ASSETS, dest))
    else:
        dest = dest_stem + ext
        shutil.copyfile(src, os.path.join(ASSETS, dest))
    return dest

def cdata(s):
    s = s if s is not None else ""
    return "<![CDATA[" + s.replace("]]>", "]]]]><![CDATA[>") + "]]>"

def esc(s):
    return html.escape(s or "", quote=True)

def postmeta(key, value):
    return ("\t\t<wp:postmeta>\n"
            f"\t\t\t<wp:meta_key>{cdata(key)}</wp:meta_key>\n"
            f"\t\t\t<wp:meta_value>{cdata(str(value))}</wp:meta_value>\n"
            "\t\t</wp:postmeta>\n")

def attachment_item(pid, parent, slug, role, url, fname):
    marker = "_mas_cert_is_hero_for" if role == "hero" else "_mas_cert_is_logo_for"
    return (
        "\t<item>\n"
        f"\t\t<title>{esc(fname)}</title>\n"
        f"\t\t<link>{esc(url)}</link>\n"
        f"\t\t<dc:creator>{cdata('admin')}</dc:creator>\n"
        f"\t\t<guid isPermaLink=\"false\">{esc(url)}</guid>\n"
        "\t\t<description></description>\n"
        "\t\t<content:encoded><![CDATA[]]></content:encoded>\n"
        "\t\t<excerpt:encoded><![CDATA[]]></excerpt:encoded>\n"
        f"\t\t<wp:post_id>{pid}</wp:post_id>\n"
        f"\t\t<wp:post_date>{cdata(NOW)}</wp:post_date>\n"
        f"\t\t<wp:post_date_gmt>{cdata(NOW)}</wp:post_date_gmt>\n"
        f"\t\t<wp:post_name>{cdata(slug + '-' + role)}</wp:post_name>\n"
        "\t\t<wp:status><![CDATA[inherit]]></wp:status>\n"
        f"\t\t<wp:post_parent>{parent}</wp:post_parent>\n"
        "\t\t<wp:menu_order>0</wp:menu_order>\n"
        "\t\t<wp:post_type><![CDATA[attachment]]></wp:post_type>\n"
        "\t\t<wp:post_password></wp:post_password>\n"
        "\t\t<wp:is_sticky>0</wp:is_sticky>\n"
        f"\t\t<wp:attachment_url>{cdata(url)}</wp:attachment_url>\n"
        + postmeta(marker, slug) +
        "\t</item>\n"
    )

def post_item(pid, c, hero_id):
    cat = c["category"]
    nicename = "iso" if cat == "ISO" else "macchine"
    out = (
        "\t<item>\n"
        f"\t\t<title>{esc(c['title'])}</title>\n"
        "\t\t<link></link>\n"
        f"\t\t<dc:creator>{cdata('admin')}</dc:creator>\n"
        f"\t\t<guid isPermaLink=\"false\">cert-{esc(c['slug'])}</guid>\n"
        "\t\t<description></description>\n"
        f"\t\t<content:encoded>{cdata(c['content_html'])}</content:encoded>\n"
        f"\t\t<excerpt:encoded>{cdata(c['excerpt'])}</excerpt:encoded>\n"
        f"\t\t<wp:post_id>{pid}</wp:post_id>\n"
        f"\t\t<wp:post_date>{cdata(NOW)}</wp:post_date>\n"
        f"\t\t<wp:post_date_gmt>{cdata(NOW)}</wp:post_date_gmt>\n"
        f"\t\t<wp:post_name>{cdata(c['slug'])}</wp:post_name>\n"
        "\t\t<wp:status><![CDATA[publish]]></wp:status>\n"
        "\t\t<wp:post_parent>0</wp:post_parent>\n"
        f"\t\t<wp:menu_order>{c['menu_order']}</wp:menu_order>\n"
        "\t\t<wp:post_type><![CDATA[mas_certificazione]]></wp:post_type>\n"
        "\t\t<wp:post_password></wp:post_password>\n"
        "\t\t<wp:is_sticky>0</wp:is_sticky>\n"
        f"\t\t<category domain=\"mas_cert_categoria\" nicename=\"{nicename}\">{cdata(cat)}</category>\n"
        + postmeta("_mas_cert_sottotitolo", c["subtitle"])
        + postmeta("_thumbnail_id", hero_id)
        + "\t</item>\n"
    )
    return out

def main():
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    certs = json.load(open(os.path.join(os.path.dirname(__file__), "manifest.json")))
    sel = json.load(open(os.path.join(os.path.dirname(__file__), "images_selection.json")))

    items_xml, log = [], []
    pid = 1000
    for c in certs:
        title = c["title"]; slug = c["slug"]
        s = sel.get(title, {})
        folder = s.get("folder")
        hero_name, logo_name = s.get("hero"), s.get("logo")
        post_id = pid; pid += 1
        hero_id = logo_id = 0
        if hero_name:
            src = find_src(folder, hero_name)
            if src:
                fn = copy_asset(src, f"{slug}-hero")
                hero_id = pid; pid += 1
                items_xml.append(attachment_item(hero_id, post_id, slug, "hero", RAW + fn, fn))
        if logo_name:
            src = find_src(folder, logo_name)
            if src:
                fn = copy_asset(src, f"{slug}-logo")
                logo_id = pid; pid += 1
                items_xml.append(attachment_item(logo_id, post_id, slug, "logo", RAW + fn, fn))
        items_xml.append(post_item(post_id, c, hero_id))
        log.append(f"{c['menu_order']:>2} {title:13} {c['category']:8} hero={'sì' if hero_id else 'NO'} logo={'sì' if logo_id else 'NO'}")

    terms = (
        "\t<wp:term><wp:term_id>101</wp:term_id><wp:term_taxonomy>mas_cert_categoria</wp:term_taxonomy>"
        "<wp:term_slug>iso</wp:term_slug><wp:term_name><![CDATA[ISO]]></wp:term_name></wp:term>\n"
        "\t<wp:term><wp:term_id>102</wp:term_id><wp:term_taxonomy>mas_cert_categoria</wp:term_taxonomy>"
        "<wp:term_slug>macchine</wp:term_slug><wp:term_name><![CDATA[Macchine]]></wp:term_name></wp:term>\n"
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
        "\t<title>MA.CI Certificazioni</title>\n"
        "\t<link>https://www.masprevenzione.it</link>\n"
        "\t<description>Import certificazioni MA.CI</description>\n"
        f"\t<pubDate>{datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>\n"
        "\t<language>it-IT</language>\n"
        "\t<wp:wxr_version>1.2</wp:wxr_version>\n"
        "\t<wp:base_site_url>https://www.masprevenzione.it</wp:base_site_url>\n"
        "\t<wp:base_blog_url>https://www.masprevenzione.it</wp:base_blog_url>\n"
        "\t<wp:author><wp:author_id>1</wp:author_id><wp:author_login><![CDATA[admin]]></wp:author_login>"
        "<wp:author_email><![CDATA[]]></wp:author_email><wp:author_display_name><![CDATA[admin]]></wp:author_display_name>"
        "<wp:author_first_name><![CDATA[]]></wp:author_first_name><wp:author_last_name><![CDATA[]]></wp:author_last_name></wp:author>\n"
        + terms
    )
    foot = "</channel>\n</rss>\n"
    open(OUT, "w", encoding="utf-8").write(head + "".join(items_xml) + foot)
    print("\n".join(log))
    print("\nWXR:", OUT)
    print("Assets in:", ASSETS, "->", len(os.listdir(ASSETS)), "file")

if __name__ == "__main__":
    main()
