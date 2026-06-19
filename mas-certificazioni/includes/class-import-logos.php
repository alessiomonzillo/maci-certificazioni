<?php
/**
 * Risolutore post-import per logo e immagine in evidenza.
 *
 * Il file di import WordPress (WXR) crea gli allegati hero/logo con due marker:
 *   - _mas_cert_is_hero_for = slug della certificazione  (immagine in evidenza)
 *   - _mas_cert_is_logo_for = slug della certificazione  (logo prima del form)
 *
 * L'importer di WordPress NON rimappa i meta con ID allegato custom
 * (es. _mas_cert_logo_id). Questa classe, dopo l'import, collega ogni allegato
 * alla certificazione giusta (per slug), imposta i meta corretti ed elimina i
 * marker. È IDEMPOTENTE: si può rilanciare senza effetti collaterali.
 *
 * Mostra un avviso in admin finché ci sono marker da risolvere.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class MAS_Cert_Import_Logos {

	// Marker usati nel WXR.
	const MARK_HERO = '_mas_cert_is_hero_for';
	const MARK_LOGO = '_mas_cert_is_logo_for';

	const ACTION = 'mas_cert_resolve_imports';

	/**
	 * Aggancia gli hook (solo lato admin).
	 */
	public function register_hooks() {
		add_action( 'admin_init', array( $this, 'maybe_handle_action' ) );
		add_action( 'admin_notices', array( $this, 'maybe_show_notice' ) );
	}

	/**
	 * Conta gli allegati con marker ancora da risolvere.
	 *
	 * @return int
	 */
	private function pending_count() {
		$q = new WP_Query(
			array(
				'post_type'      => 'attachment',
				'post_status'    => 'inherit',
				'posts_per_page' => 1,
				'fields'         => 'ids',
				'no_found_rows'  => false,
				'meta_query'     => array(
					'relation' => 'OR',
					array( 'key' => self::MARK_HERO, 'compare' => 'EXISTS' ),
					array( 'key' => self::MARK_LOGO, 'compare' => 'EXISTS' ),
				),
			)
		);
		return (int) $q->found_posts;
	}

	/**
	 * Mostra l'avviso con il bottone per avviare la risoluzione.
	 */
	public function maybe_show_notice() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}

		// Messaggio di esito (dopo il redirect).
		if ( isset( $_GET['mas_cert_resolved'] ) ) {
			$n = absint( wp_unslash( $_GET['mas_cert_resolved'] ) );
			printf(
				'<div class="notice notice-success is-dismissible"><p>%s</p></div>',
				sprintf(
					/* translators: %d = numero di certificazioni completate. */
					esc_html__( 'Loghi e immagini collegati: %d certificazioni aggiornate.', 'mas-certificazioni' ),
					$n
				)
			);
		}

		if ( $this->pending_count() < 1 ) {
			return;
		}

		$url = wp_nonce_url(
			add_query_arg( 'mas_cert_action', self::ACTION, admin_url( 'index.php' ) ),
			self::ACTION
		);
		printf(
			'<div class="notice notice-warning"><p><strong>%s</strong> %s</p><p><a href="%s" class="button button-primary">%s</a></p></div>',
			esc_html__( 'MAS Certificazioni:', 'mas-certificazioni' ),
			esc_html__( 'rilevate immagini importate da collegare alle certificazioni (logo + immagine in evidenza).', 'mas-certificazioni' ),
			esc_url( $url ),
			esc_html__( 'Completa loghi importati', 'mas-certificazioni' )
		);
	}

	/**
	 * Gestisce il click sul bottone: risolve i marker e reindirizza con esito.
	 */
	public function maybe_handle_action() {
		if ( ! isset( $_GET['mas_cert_action'] ) || self::ACTION !== $_GET['mas_cert_action'] ) {
			return;
		}
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		check_admin_referer( self::ACTION );

		$updated = $this->resolve();

		$redirect = add_query_arg( 'mas_cert_resolved', $updated, admin_url( 'index.php' ) );
		wp_safe_redirect( $redirect );
		exit;
	}

	/**
	 * Collega gli allegati marcati alle rispettive certificazioni.
	 *
	 * @return int Numero di certificazioni toccate.
	 */
	private function resolve() {
		$touched = array();

		// HERO -> immagine in evidenza (_thumbnail_id).
		foreach ( $this->find_marked( self::MARK_HERO ) as $att_id ) {
			$slug = get_post_meta( $att_id, self::MARK_HERO, true );
			$post = $this->find_cert_by_slug( $slug );
			if ( $post ) {
				set_post_thumbnail( $post, $att_id );
				$touched[ $post ] = true;
			}
			delete_post_meta( $att_id, self::MARK_HERO );
		}

		// LOGO -> meta custom (_mas_cert_logo_id).
		foreach ( $this->find_marked( self::MARK_LOGO ) as $att_id ) {
			$slug = get_post_meta( $att_id, self::MARK_LOGO, true );
			$post = $this->find_cert_by_slug( $slug );
			if ( $post ) {
				update_post_meta( $post, MAS_Cert_Meta::META_LOGO_ID, $att_id );
				$touched[ $post ] = true;
			}
			delete_post_meta( $att_id, self::MARK_LOGO );
		}

		return count( $touched );
	}

	/**
	 * Restituisce gli ID allegato con un certo marker.
	 *
	 * @param string $marker Chiave meta marker.
	 * @return int[]
	 */
	private function find_marked( $marker ) {
		$q = new WP_Query(
			array(
				'post_type'      => 'attachment',
				'post_status'    => 'inherit',
				'posts_per_page' => -1,
				'fields'         => 'ids',
				'meta_query'     => array(
					array( 'key' => $marker, 'compare' => 'EXISTS' ),
				),
			)
		);
		return $q->posts;
	}

	/**
	 * Trova la certificazione dal suo slug (post_name).
	 *
	 * @param string $slug Slug del post.
	 * @return int|false ID del post oppure false.
	 */
	private function find_cert_by_slug( $slug ) {
		$slug = sanitize_title( $slug );
		if ( ! $slug ) {
			return false;
		}
		$post = get_page_by_path( $slug, OBJECT, MAS_CERT_CPT );
		return $post ? (int) $post->ID : false;
	}
}
