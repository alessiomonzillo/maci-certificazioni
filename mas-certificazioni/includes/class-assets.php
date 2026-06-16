<?php
/**
 * Enqueue di CSS e JS minimali, caricati SOLO sulle pagine
 * di archivio e dettaglio delle certificazioni, per non appesantire il sito.
 *
 * JS: gestione tab (filtro categoria), ricerca testuale client-side, lightbox PDF.
 * CSS: stili minimali; il grosso dell'aspetto è demandato alle classi del tema.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class MAS_Cert_Assets {

	/**
	 * Aggancia gli hook.
	 */
	public function register_hooks() {
		add_action( 'wp_enqueue_scripts', array( $this, 'enqueue_front_assets' ) );
	}

	/**
	 * Carica CSS/JS solo dove servono.
	 */
	public function enqueue_front_assets() {

		// Solo archivio o singolo del CPT.
		if ( ! is_post_type_archive( MAS_CERT_CPT ) && ! is_singular( MAS_CERT_CPT ) ) {
			return;
		}

		// --- CSS ---
		wp_enqueue_style(
			'mas-cert-style',
			MAS_CERT_URL . 'assets/certificazioni.css',
			array(),
			MAS_CERT_VERSION
		);

		// --- JS ---
		wp_enqueue_script(
			'mas-cert-script',
			MAS_CERT_URL . 'assets/certificazioni.js',
			array(),
			MAS_CERT_VERSION,
			true // in footer.
		);

		// Stringhe localizzate (i18n lato JS).
		wp_localize_script(
			'mas-cert-script',
			'masCertI18n',
			array(
				'closeLabel' => __( 'Chiudi', 'mas-certificazioni' ),
				'pdfMissing' => __( 'PDF non disponibile.', 'mas-certificazioni' ),
			)
		);
	}
}
