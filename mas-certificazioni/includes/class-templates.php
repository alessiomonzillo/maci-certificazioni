<?php
/**
 * Override dei template di archivio e di dettaglio tramite il filtro
 * 'template_include'. I template vivono nel plugin (cartella templates/),
 * così il plugin resta autosufficiente e non richiede modifiche al tema.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class MAS_Cert_Templates {

	/**
	 * Aggancia gli hook.
	 */
	public function register_hooks() {
		add_filter( 'template_include', array( $this, 'template_include' ) );

		// Helper riutilizzabili dai template (resi disponibili come funzioni globali).
		// Vengono definiti qui per tenere la logica di lettura dei meta in un solo posto.
	}

	/**
	 * Sceglie il template corretto per archivio e singolo del CPT.
	 *
	 * @param string $template Percorso del template attualmente scelto da WP.
	 * @return string
	 */
	public function template_include( $template ) {

		// ARCHIVIO /certificazioni/
		if ( is_post_type_archive( MAS_CERT_CPT ) ) {
			$plugin_template = MAS_CERT_PATH . 'templates/archive-certificazione.php';
			if ( file_exists( $plugin_template ) ) {
				return $plugin_template;
			}
		}

		// SINGOLO /certificazioni/{slug}/
		if ( is_singular( MAS_CERT_CPT ) ) {
			$plugin_template = MAS_CERT_PATH . 'templates/single-certificazione.php';
			if ( file_exists( $plugin_template ) ) {
				return $plugin_template;
			}
		}

		return $template;
	}

	/* ---------------------------------------------------------------------
	 * HELPER STATICI (usati dai template)
	 * ------------------------------------------------------------------ */

	/**
	 * Restituisce il sottotitolo di una certificazione.
	 *
	 * @param int $post_id ID post.
	 * @return string
	 */
	public static function get_sottotitolo( $post_id ) {
		return (string) get_post_meta( $post_id, MAS_Cert_Meta::META_SOTTOTITOLO, true );
	}

	/**
	 * Restituisce l'URL del PDF di una certificazione (o stringa vuota).
	 *
	 * @param int $post_id ID post.
	 * @return string
	 */
	public static function get_pdf_url( $post_id ) {
		$pdf_id = (int) get_post_meta( $post_id, MAS_Cert_Meta::META_PDF_ID, true );
		if ( $pdf_id <= 0 ) {
			return '';
		}
		$url = wp_get_attachment_url( $pdf_id );
		return $url ? $url : '';
	}

	/**
	 * Restituisce l'ID dell'immagine logo (o 0).
	 *
	 * @param int $post_id ID post.
	 * @return int
	 */
	public static function get_logo_id( $post_id ) {
		return (int) get_post_meta( $post_id, MAS_Cert_Meta::META_LOGO_ID, true );
	}

	/**
	 * Restituisce il/i nome/i della/e categoria/e di una certificazione, come stringa.
	 *
	 * @param int $post_id ID post.
	 * @return string Es. "ISO" oppure "ISO, Macchine".
	 */
	public static function get_categoria_label( $post_id ) {
		$terms = get_the_terms( $post_id, MAS_CERT_TAX );
		if ( empty( $terms ) || is_wp_error( $terms ) ) {
			return '';
		}
		$names = wp_list_pluck( $terms, 'name' );
		return implode( ', ', $names );
	}

	/**
	 * Restituisce gli slug delle categorie (per il filtro client-side via data-categoria).
	 *
	 * @param int $post_id ID post.
	 * @return string Slug separati da spazio.
	 */
	public static function get_categoria_slugs( $post_id ) {
		$terms = get_the_terms( $post_id, MAS_CERT_TAX );
		if ( empty( $terms ) || is_wp_error( $terms ) ) {
			return '';
		}
		$slugs = wp_list_pluck( $terms, 'slug' );
		return implode( ' ', $slugs );
	}
}
