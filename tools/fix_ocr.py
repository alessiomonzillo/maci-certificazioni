#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correzione degli errori OCR nelle 4 certificazioni ex-PDF (ISO 9001, 14001,
27001, 45001). Riscrive il content_html corretto (testo originale dove l'OCR era
giusto; fix puntuali e ricostruzioni dal contesto dove l'OCR ha sbagliato/perso
testo), aggiorna tools/manifest.json SOLO per questi 4, rigenera il WXR per
coerenza, e produce import/correzioni-ocr.md (HTML pronto da incollare nell'editor).

Le altre 14 certificazioni NON vengono toccate.
"""
import json, os, subprocess, html, re

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "manifest.json")
OUT_MD = os.path.join(os.path.dirname(HERE), "import", "correzioni-ocr.md")

# Contenuti corretti (slug -> content_html).
CORRECTED = {
"iso-9001": """<p>Linee guida per una lettura approfondita:</p>
<h2>1. L'Efficienza Operativa e Strategica</h2>
<p>L'implementazione di un Sistema di Gestione della Qualità (SGQ) basato sulla norma ISO 9001 permette alle aziende di:</p>
<ul>
<li>Ottimizzare i processi: Identificare e rimuovere i passaggi ridondanti, riducendo i costi operativi.</li>
<li>Ridurre gli sprechi: Una gestione controllata minimizza gli errori e i rifacimenti, migliorando il margine di profitto.</li>
<li>Miglioramento Continuo: Attraverso il ciclo PDCA (Plan-Do-Check-Act), l'azienda evolve costantemente per rispondere alle sfide del mercato.</li>
</ul>
<h2>2. Il Valore della Sicurezza Integrata</h2>
<p>Un aspetto cruciale, spesso sottovalutato, è il legame tra Qualità e Sicurezza. La norma ISO 9001 pone le basi per un ambiente di lavoro protetto e resiliente:</p>
<ul>
<li>Sicurezza dei Lavoratori: Procedure standardizzate riducono drasticamente l'improvvisazione, che è la causa principale di infortuni sul lavoro.</li>
<li>Sicurezza del Prodotto/Servizio: Garantire standard qualitativi elevati significa immettere sul mercato prodotti sicuri per il consumatore finale, riducendo i rischi legali e reputazionali.</li>
<li>Gestione del Rischio (Risk-based thinking): La norma impone un'analisi preventiva dei rischi, permettendo all'azienda di proteggere i propri asset e la continuità del business.</li>
</ul>
<h2>3. Vantaggi Competitivi e Reputazione</h2>
<p>Ottenere la certificazione apre porte che altrimenti resterebbero chiuse:</p>
<ul>
<li>Accesso facilitato a gare d'appalto e forniture per grandi multinazionali.</li>
<li>Aumento della soddisfazione del cliente.</li>
<li>Immagine di affidabilità e serietà.</li>
</ul>
<h2>4. I Sette Principi della Qualità</h2>
<p>La norma si fonda su pilastri che trasformano la cultura aziendale:</p>
<ul>
<li>Orientamento al cliente: Capire le necessità presenti e future.</li>
<li>Leadership: Unità di intenti e direzione strategica.</li>
<li>Coinvolgimento delle persone: Valorizzare le competenze a ogni livello.</li>
<li>Approccio per processi: Gestire le attività come sistemi interconnessi.</li>
<li>Miglioramento: Focalizzazione costante sull'ottimizzazione.</li>
<li>Processo decisionale basato sulle evidenze: Decisioni basate sull'analisi dei dati reali.</li>
<li>Gestione delle relazioni: Collaborazione proficua con i fornitori.</li>
</ul>
<p>In conclusione, la ISO 9001 è un investimento strategico che garantisce che la qualità e la sicurezza non siano eventi casuali, ma il risultato di un processo deliberato e controllato, essenziale per la longevità di qualsiasi impresa.</p>""",

"iso-14001": """<h2>1. Perché la ISO 14001 è Fondamentale</h2>
<p>L'adozione di questa norma non è solo una scelta etica, ma un vantaggio strategico:</p>
<ul>
<li>Conformità Legislativa: Riduce il rischio di sanzioni garantendo il rispetto delle leggi ambientali vigenti.</li>
<li>Efficienza delle Risorse: Ottimizza l'uso di materie prime, energia e acqua, portando a una riduzione dei costi operativi.</li>
<li>Gestione dei Rifiuti: Migliora i processi di smaltimento e favorisce il riciclo.</li>
<li>Reputazione Green: Migliora l'immagine aziendale agli occhi di consumatori, investitori e partner sempre più attenti all'ambiente.</li>
</ul>
<h2>2. Integrazione con ISO 9001 e ISO 45001</h2>
<p>La ISO 14001 condivide la stessa struttura (HLS) delle norme sulla Qualità e sulla Sicurezza. Un'azienda certificata in tutti e tre gli ambiti ottiene:</p>
<ul>
<li>Visione Olistica: Qualità del prodotto, sicurezza delle persone e rispetto dell'ambiente lavorano in sinergia.</li>
<li>Prevenzione dei Rischi: Il focus si sposta dalla reazione ai problemi alla prevenzione dei danni ambientali e degli incidenti sul lavoro.</li>
<li>Semplificazione Documentale: Procedure comuni riducono la burocrazia interna.</li>
</ul>
<h2>3. Vantaggi Competitivi</h2>
<table>
<thead><tr><th>Area di Impatto</th><th>Vantaggio Riscontrato</th></tr></thead>
<tbody>
<tr><td>Mercato</td><td>Accesso a bandi e gare d'appalto che premiano i criteri ESG (Environmental, Social, Governance).</td></tr>
<tr><td>Assicurazioni</td><td>Potenziale riduzione dei premi per polizze di responsabilità civile ambientale.</td></tr>
<tr><td>Innovazione</td><td>Spinta verso l'eco-design e lo sviluppo di prodotti a basso impatto.</td></tr>
</tbody>
</table>
<p>La certificazione ISO 14001 trasforma l'impegno ambientale da costo a opportunità. Proteggere il pianeta diventa un pilastro della strategia aziendale, garantendo resilienza e successo nel lungo periodo.</p>""",

"iso-27001": """<h2>1. Perché la ISO 27001 è Fondamentale</h2>
<p>L'adozione di questo standard permette di proteggere l'azienda su tre livelli chiave (Triade CIA):</p>
<ul>
<li>Riservatezza (Confidentiality): Assicurare che le informazioni siano accessibili solo a chi ne ha il diritto.</li>
<li>Integrità (Integrity): Garantire che i dati non vengano alterati o manipolati da soggetti non autorizzati.</li>
<li>Disponibilità (Availability): Assicurare che i sistemi e i dati siano pronti all'uso quando necessario.</li>
</ul>
<h2>2. Vantaggi della Certificazione</h2>
<ul>
<li>Resilienza agli Attacchi Cyber: Implementa controlli tecnici e organizzativi per prevenire e mitigare violazioni dei dati (Data Breach).</li>
<li>Conformità al GDPR: Facilita il rispetto del Regolamento Europeo sulla Privacy, riducendo il rischio di sanzioni pesanti.</li>
<li>Continuità Operativa (Business Continuity): Minimizza i tempi di fermo in caso di attacco o incidente informatico.</li>
<li>Vantaggio Competitivo: Dimostra a clienti e partner un impegno serio nella protezione dei loro dati sensibili.</li>
</ul>
<h2>3. Un Sistema di Gestione Integrato</h2>
<p>La ISO 27001 si sposa perfettamente con gli altri standard trattati (9001, 14001, 45001) condividendo la struttura HLS:</p>
<ul>
<li>Qualità (9001): Un servizio di qualità deve essere sicuro e affidabile.</li>
<li>Sicurezza (45001): La sicurezza delle persone oggi passa anche attraverso la protezione dei sistemi che controllano gli impianti.</li>
<li>Ambiente (14001): La digitalizzazione sicura riduce l'impronta cartacea e ottimizza i flussi energetici.</li>
</ul>
<p>La Cyber Security non è un problema dell'ufficio IT, ma una priorità del management. La ISO 27001 trasforma la vulnerabilità in forza, proteggendo il segreto industriale e la fiducia del mercato.</p>""",

"iso-45001": """<h2>1. L'importanza Strategica della ISO 45001</h2>
<p>Implementare un sistema di gestione basato sulla ISO 45001 significa mettere le persone al centro dell'organizzazione. Questo standard fornisce un quadro solido per migliorare la sicurezza dei lavoratori, ridurre i rischi sul luogo di lavoro e creare condizioni di lavoro migliori e più sicure.</p>
<ul>
<li>Riduzione di Infortuni e Malattie: Attraverso una gestione proattiva, l'azienda riduce drasticamente il numero di incidenti sul lavoro e l'insorgenza di malattie professionali.</li>
<li>Aumento della Produttività: Un ambiente di lavoro sicuro riduce i tempi di inattività dovuti a infortuni e migliora il morale dei dipendenti, aumentando l'efficienza complessiva.</li>
<li>Conformità Legale: Aiuta le organizzazioni a soddisfare i requisiti normativi (come il D.Lgs. 81/08 in Italia), riducendo il rischio di sanzioni penali e amministrative.</li>
<li>Miglioramento della Reputazione: Dimostra l'impegno etico dell'azienda, migliorando l'immagine verso clienti, investitori e la comunità.</li>
</ul>
<h2>2. I Pilastri della Norma</h2>
<p>La ISO 45001 si basa sulla struttura ad alto livello (HLS), facilitando l'integrazione con altre norme come la ISO 9001. I suoi elementi chiave includono:</p>
<ul>
<li>Leadership e Partecipazione: consultazione dei lavoratori a tutti i livelli.</li>
<li>Approccio Basato sul Rischio: Identificazione dei pericoli e valutazione dei rischi non solo per la sicurezza fisica, ma anche per la salute mentale.</li>
<li>Ciclo PDCA: Pianificare, Fare, Verificare e Agire per garantire un miglioramento continuo delle prestazioni di sicurezza.</li>
<li>Contesto dell'Organizzazione: analisi dei fattori interni ed esterni che possono influenzare la sicurezza sul lavoro.</li>
</ul>
<h2>3. Vantaggi Economici</h2>
<p>Oltre alla protezione delle vite umane, la certificazione porta benefici finanziari tangibili:</p>
<ul>
<li>Riduzione dei Premi Assicurativi: Molte assicurazioni (come l'INAIL in Italia tramite il modello OT23) offrono sconti significativi sui premi per le aziende certificate.</li>
<li>Accesso a Gare d'Appalto: Spesso la certificazione ISO 45001 è un requisito preferenziale o obbligatorio per partecipare a grandi commesse internazionali.</li>
<li>Riduzione dei Costi Indiretti: Minori costi legati alla sostituzione di personale infortunato, indagini sugli incidenti e danni alle attrezzature.</li>
</ul>
<p>La certificazione ISO 45001 rappresenta la promessa di un'azienda ai propri dipendenti: la garanzia che ogni persona possa tornare a casa sana e salva ogni giorno.</p>""",
}

# Parti RICOSTRUITE dal contesto (OCR aveva perso testo) -> da confermare.
RECON = {
    "iso-9001": ["Sez. 3: ricostruiti gli inizi dei bullet «Aumento della soddisfazione del cliente.» e «Immagine di affidabilità e serietà.» (l'OCR aveva troncato l'inizio)."],
    "iso-14001": ["Sez. 3: tabella «Area di Impatto / Vantaggio» ricomposta (i valori c'erano già, era schiacciata in testo dall'OCR)."],
    "iso-27001": ["Solo fix puntuali (spazi/parentesi/numeri sezione): nessun testo inventato."],
    "iso-45001": ["Sez. 2: ricostruito l'inizio «Leadership e Partecipazione:» del 1° pilastro e la parte centrale di «Contesto dell'Organizzazione: analisi dei fattori interni ed esterni che possono …» (l'OCR aveva perso queste porzioni)."],
}

def main():
    data = json.load(open(MANIFEST))
    by_slug = {x["slug"]: x for x in data}
    for slug, html_corr in CORRECTED.items():
        assert slug in by_slug, f"slug mancante: {slug}"
        by_slug[slug]["content_html"] = html_corr.strip()
    json.dump(data, open(MANIFEST, "w"), ensure_ascii=False, indent=2)
    print("manifest aggiornato per:", ", ".join(CORRECTED))

    # rigenera il WXR per coerenza (sito non interessato)
    subprocess.run(["python3", os.path.join(HERE, "build_wxr.py")], check=True,
                   stdout=subprocess.DEVNULL)
    print("WXR rigenerato.")

    # deliverable markdown da incollare
    titoli = {"iso-9001": "ISO 9001", "iso-14001": "ISO 14001",
              "iso-27001": "ISO 27001", "iso-45001": "ISO 45001"}
    lines = ["# Correzioni OCR — contenuti da incollare\n",
             "Per ogni certificazione: apri il post in WordPress → menu ⋮ in alto a destra → "
             "**Editor di codice** → seleziona tutto e incolla il blocco → torna all'**Editor visuale** → **Aggiorna**.\n",
             "Immagine in evidenza, logo, categoria e ordine restano invariati.\n"]
    for slug in CORRECTED:
        lines.append(f"\n## {titoli[slug]}\n")
        lines.append("**Parti ricostruite (verifica):** " + " ".join(RECON[slug]) + "\n")
        lines.append("```html")
        lines.append(by_slug[slug]["content_html"])
        lines.append("```")
    open(OUT_MD, "w").write("\n".join(lines) + "\n")
    print("Deliverable ->", OUT_MD)

if __name__ == "__main__":
    main()
