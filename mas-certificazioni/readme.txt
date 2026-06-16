=== MAS Certificazioni ===
Autore: Upthere
Versione: 1.0.0
Requisiti: WordPress 5.8+, tema Edge/Qode + WPBakery, Contact Form 7 (per il form).

== Cosa fa ==
Gestione delle certificazioni (ISO / Macchine) come post WordPress NATIVI:
- Custom Post Type "Certificazioni" con titolo, editor, immagine in evidenza, riassunto, ordine (priorità).
- Tassonomia gerarchica con i termini "ISO" e "Macchine" creati automaticamente all'attivazione.
- Meta box native (senza ACF): Sottotitolo, PDF certificazione, Logo certificazione — tutto via Media Library WP.
- Front-end con le classi del tema (eltdf-*, vc_row/wpb_column): archivio /certificazioni/ e dettaglio.
- Tab di filtro per categoria + ricerca testuale (client-side, senza ricaricare).
- PDF visualizzato in lightbox inline (nessun download — protezione solo lato UI).
- Form di contatto tramite Contact Form 7 esistente (ID configurabile, default 3163).

Plugin AUTOSUFFICIENTE: una sola installazione, nessun secondo plugin richiesto (a parte CF7 per il form).

== Installazione ==
1. Carica la cartella "mas-certificazioni" in /wp-content/plugins/ (oppure lo zip da Plugin > Aggiungi nuovo > Carica plugin).
2. Attiva "MAS Certificazioni". All'attivazione vengono creati i termini "ISO" e "Macchine" e aggiornati i permalink.
3. Vai su "Certificazioni" nel menu admin e aggiungi le certificazioni:
   - Titolo (es. "ISO 22000")
   - Riassunto = anteprima 3 righe in card
   - Immagine in evidenza = card + hero
   - Categoria (ISO / Macchine) = alimenta tab e label
   - Ordine pagina = priorità (ASC)
   - Editor = contenuto approfondito (sezioni con H2/liste)
   - Meta box: Sottotitolo, PDF, Logo

== Configurazione ID Contact Form 7 ==
Default 3163. Per cambiarlo, in wp-config.php (prima del caricamento del plugin):
    define( 'MAS_CERT_CF7_ID', 1234 );
Il destinatario (info@masprevenzione.it) resta configurato in CF7 admin: il plugin NON invia email.

== STEP 0 — Verifica classi del tema (IMPORTANTE prima del go-live) ==
I template usano le classi standard Edge/Qode su WPBakery
(eltdf-btn eltdf-btn-medium eltdf-btn-solid per i bottoni; wrapper vc_row/wpb_column).
Ispeziona la sezione "Corsi" esistente del sito e, se le classi di card/immagine/titolo/CTA
differiscono, allineale nei file:
  - templates/archive-certificazione.php
  - templates/single-certificazione.php
Le misure (margin/padding) seguono il sito attuale; il Figma è indicativo.

== Aspetto (mockup MA.CI) ==
Il front-end replica il mockup Figma "MA.CI":
- Colore accento ROSSO (#e12227) usato per tab attivo, icona occhio (quadrato),
  CTA "Apri documento" (bottone pieno a tutta larghezza) e bottone "Visualizza PDF".
- Archivio: titolo e tab (ISO/Macchine) centrati, ricerca full-width con icona.
- Dettaglio: "Torna indietro", label "Certificazioni <categoria>", titolo, sottotitolo,
  intro, hero con bottone PDF, sezioni, logo, form CF7.
Il colore accento è una variabile CSS in assets/certificazioni.css:
    :root { --mas-cert-accent: #e12227; }
Modificala lì per cambiare l'identità cromatica senza toccare il resto.

== Operazioni finali a sito (da fare a mano) ==
1. Aspetto > Menu: aggiungi una voce "Certificazioni" come "Link personalizzato"
   che punta a /certificazioni/.
2. Alleggerisci la pagina Servizi > Qualità: lascia l'introduzione e aggiungi
   un link alla nuova sezione /certificazioni/.

== Nota PDF ==
La visualizzazione del PDF è inline in lightbox, senza bottone di download.
Questa è una protezione SOLO lato interfaccia: l'URL del file resta tecnicamente
accessibile a chi conosce il link diretto.
