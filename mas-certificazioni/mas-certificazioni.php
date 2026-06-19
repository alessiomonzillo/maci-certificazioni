<?php
/**
 * Plugin Name: MAS Certificazioni
 * Plugin URI:  https://www.masprevenzione.it/
 * Description: Gestione delle certificazioni (ISO / Macchine) come post WordPress nativi, con meta box native (sottotitolo, PDF, logo) e front-end allineato al tema Edge/Qode + WPBakery. Autosufficiente: nessuna dipendenza obbligatoria (no ACF).
 * Version:     1.0.0
 * Author:      Upthere
 * Author URI:  https://upthere.it/
 * Text Domain: mas-certificazioni
 * Domain Path: /languages
 * License:     GPL-2.0-or-later
 *
 * NOTA SULLA SICUREZZA PDF:
 * La "protezione" del PDF (nessun bottone di download, solo visualizzazione inline)
 * è esclusivamente lato UI. L'URL dell'allegato resta tecnicamente raggiungibile
 * da chi conosce il link diretto. Non è una protezione reale del file.
 */

// Blocco accesso diretto al file.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/* -------------------------------------------------------------------------
 * COSTANTI DI BASE
 * ---------------------------------------------------------------------- */

// Versione plugin (usata per il versioning di CSS/JS in enqueue).
define( 'MAS_CERT_VERSION', '1.0.0' );

// Percorso assoluto della cartella del plugin (con slash finale).
define( 'MAS_CERT_PATH', plugin_dir_path( __FILE__ ) );

// URL pubblico della cartella del plugin (con slash finale).
define( 'MAS_CERT_URL', plugin_dir_url( __FILE__ ) );

// Slug del Custom Post Type.
define( 'MAS_CERT_CPT', 'mas_certificazione' );

// Slug della tassonomia gerarchica.
define( 'MAS_CERT_TAX', 'mas_cert_categoria' );

/**
 * ID del form Contact Form 7 da iniettare nella single.
 * Configurabile: per cambiarlo basta ridefinire la costante in wp-config.php
 * PRIMA che il plugin venga caricato, es:
 *   define( 'MAS_CERT_CF7_ID', 1234 );
 * Il destinatario (info@masprevenzione.it) resta configurato lato CF7 admin:
 * questo plugin NON invia email.
 */
if ( ! defined( 'MAS_CERT_CF7_ID' ) ) {
	define( 'MAS_CERT_CF7_ID', 3163 );
}

/* -------------------------------------------------------------------------
 * CARICAMENTO CLASSI
 * ---------------------------------------------------------------------- */

require_once MAS_CERT_PATH . 'includes/class-cpt.php';
require_once MAS_CERT_PATH . 'includes/class-meta.php';
require_once MAS_CERT_PATH . 'includes/class-templates.php';
require_once MAS_CERT_PATH . 'includes/class-assets.php';
require_once MAS_CERT_PATH . 'includes/class-import-logos.php';

/* -------------------------------------------------------------------------
 * BOOTSTRAP
 * ---------------------------------------------------------------------- */

/**
 * Inizializza tutti i moduli del plugin agganciandoli ai rispettivi hook.
 */
function mas_cert_bootstrap() {
	// CPT + tassonomia.
	$cpt = new MAS_Cert_CPT();
	$cpt->register_hooks();

	// Meta box native.
	$meta = new MAS_Cert_Meta();
	$meta->register_hooks();

	// Override dei template di archivio e singolo.
	$templates = new MAS_Cert_Templates();
	$templates->register_hooks();

	// Enqueue di CSS e JS (front-end).
	$assets = new MAS_Cert_Assets();
	$assets->register_hooks();

	// Risolutore post-import (collega logo + immagine in evidenza dopo il WXR).
	$import = new MAS_Cert_Import_Logos();
	$import->register_hooks();
}
add_action( 'plugins_loaded', 'mas_cert_bootstrap' );

/* -------------------------------------------------------------------------
 * ATTIVAZIONE / DISATTIVAZIONE
 * ---------------------------------------------------------------------- */

/**
 * In attivazione:
 *  1. registra CPT + tassonomia (necessario perché il flush abbia le rewrite rules corrette)
 *  2. crea i termini di default "ISO" e "Macchine"
 *  3. flush delle rewrite rules per attivare gli slug /certificazioni/
 */
function mas_cert_activate() {
	// Registriamo CPT e tassonomia "a mano" durante l'attivazione,
	// perché in questo momento gli hook 'init' del bootstrap non sono ancora girati.
	$cpt = new MAS_Cert_CPT();
	$cpt->register_cpt();
	$cpt->register_taxonomy();
	$cpt->maybe_create_default_terms();

	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'mas_cert_activate' );

/**
 * In disattivazione: flush delle rewrite rules per ripulire gli endpoint.
 * Non eliminiamo CPT/termini/post: i dati del cliente restano intatti.
 */
function mas_cert_deactivate() {
	flush_rewrite_rules();
}
register_deactivation_hook( __FILE__, 'mas_cert_deactivate' );
