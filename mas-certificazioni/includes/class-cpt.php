<?php
/**
 * Registrazione del Custom Post Type "mas_certificazione" e della
 * tassonomia gerarchica "mas_cert_categoria", con creazione dei
 * termini di default ("ISO" e "Macchine") in fase di attivazione.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class MAS_Cert_CPT {

	/**
	 * Aggancia i metodi agli hook di WordPress.
	 */
	public function register_hooks() {
		// La tassonomia va registrata prima del CPT su 'init'.
		add_action( 'init', array( $this, 'register_taxonomy' ), 9 );
		add_action( 'init', array( $this, 'register_cpt' ), 10 );
	}

	/**
	 * Registra il CPT delle certificazioni.
	 *
	 * - supports: title, editor, thumbnail (featured image), excerpt, page-attributes (menu_order)
	 * - public, has_archive 'certificazioni', rewrite slug 'certificazioni'
	 * - label in italiano
	 */
	public function register_cpt() {

		$labels = array(
			'name'                  => _x( 'Certificazioni', 'Post type general name', 'mas-certificazioni' ),
			'singular_name'         => _x( 'Certificazione', 'Post type singular name', 'mas-certificazioni' ),
			'menu_name'             => _x( 'Certificazioni', 'Admin Menu text', 'mas-certificazioni' ),
			'name_admin_bar'        => _x( 'Certificazione', 'Add New on Toolbar', 'mas-certificazioni' ),
			'add_new'               => __( 'Aggiungi nuova', 'mas-certificazioni' ),
			'add_new_item'          => __( 'Aggiungi nuova certificazione', 'mas-certificazioni' ),
			'new_item'              => __( 'Nuova certificazione', 'mas-certificazioni' ),
			'edit_item'             => __( 'Modifica certificazione', 'mas-certificazioni' ),
			'view_item'             => __( 'Visualizza certificazione', 'mas-certificazioni' ),
			'all_items'             => __( 'Tutte le certificazioni', 'mas-certificazioni' ),
			'search_items'          => __( 'Cerca certificazioni', 'mas-certificazioni' ),
			'parent_item_colon'     => __( 'Certificazione padre:', 'mas-certificazioni' ),
			'not_found'             => __( 'Nessuna certificazione trovata.', 'mas-certificazioni' ),
			'not_found_in_trash'    => __( 'Nessuna certificazione nel cestino.', 'mas-certificazioni' ),
			'featured_image'        => __( 'Immagine in evidenza (card/hero)', 'mas-certificazioni' ),
			'set_featured_image'    => __( 'Imposta immagine', 'mas-certificazioni' ),
			'remove_featured_image' => __( 'Rimuovi immagine', 'mas-certificazioni' ),
			'use_featured_image'    => __( 'Usa come immagine', 'mas-certificazioni' ),
			'archives'              => __( 'Archivio certificazioni', 'mas-certificazioni' ),
			'item_published'        => __( 'Certificazione pubblicata.', 'mas-certificazioni' ),
			'item_updated'          => __( 'Certificazione aggiornata.', 'mas-certificazioni' ),
		);

		$args = array(
			'labels'             => $labels,
			'public'             => true,
			'show_ui'            => true,
			'show_in_menu'       => true,
			'show_in_rest'       => true, // editor a blocchi + REST.
			'menu_icon'          => 'dashicons-awards',
			'menu_position'      => 25,
			'has_archive'        => 'certificazioni',
			'rewrite'            => array(
				'slug'       => 'certificazioni',
				'with_front' => false,
			),
			'capability_type'    => 'post',
			'hierarchical'       => false,
			'supports'           => array( 'title', 'editor', 'thumbnail', 'excerpt', 'page-attributes' ),
			'taxonomies'         => array( MAS_CERT_TAX ),
		);

		register_post_type( MAS_CERT_CPT, $args );
	}

	/**
	 * Registra la tassonomia gerarchica delle categorie (ISO / Macchine).
	 */
	public function register_taxonomy() {

		$labels = array(
			'name'              => _x( 'Categorie certificazione', 'taxonomy general name', 'mas-certificazioni' ),
			'singular_name'     => _x( 'Categoria certificazione', 'taxonomy singular name', 'mas-certificazioni' ),
			'search_items'      => __( 'Cerca categorie', 'mas-certificazioni' ),
			'all_items'         => __( 'Tutte le categorie', 'mas-certificazioni' ),
			'parent_item'       => __( 'Categoria padre', 'mas-certificazioni' ),
			'parent_item_colon' => __( 'Categoria padre:', 'mas-certificazioni' ),
			'edit_item'         => __( 'Modifica categoria', 'mas-certificazioni' ),
			'update_item'       => __( 'Aggiorna categoria', 'mas-certificazioni' ),
			'add_new_item'      => __( 'Aggiungi nuova categoria', 'mas-certificazioni' ),
			'new_item_name'     => __( 'Nome nuova categoria', 'mas-certificazioni' ),
			'menu_name'         => __( 'Categorie', 'mas-certificazioni' ),
		);

		$args = array(
			'labels'            => $labels,
			'hierarchical'      => true, // gerarchica come da specifica.
			'public'            => true,
			'show_ui'           => true,
			'show_admin_column' => true,
			'show_in_rest'      => true,
			'rewrite'           => array(
				'slug'       => 'categoria-certificazione',
				'with_front' => false,
			),
		);

		register_taxonomy( MAS_CERT_TAX, array( MAS_CERT_CPT ), $args );
	}

	/**
	 * Crea i termini di default "ISO" e "Macchine" se non esistono già.
	 * Idempotente: si può richiamare più volte senza duplicare i termini.
	 */
	public function maybe_create_default_terms() {

		// La tassonomia deve esistere prima di poter inserire termini.
		if ( ! taxonomy_exists( MAS_CERT_TAX ) ) {
			$this->register_taxonomy();
		}

		$default_terms = array( 'ISO', 'Macchine' );

		foreach ( $default_terms as $term_name ) {
			if ( ! term_exists( $term_name, MAS_CERT_TAX ) ) {
				wp_insert_term( $term_name, MAS_CERT_TAX );
			}
		}
	}
}
