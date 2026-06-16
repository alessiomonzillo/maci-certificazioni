<?php
/**
 * Meta box native per le certificazioni:
 *  - sottotitolo (text)        -> riga descrittiva sotto il titolo
 *  - pdf_certificazione (ID/URL allegato) -> occhio / "Visualizza PDF"
 *  - logo_certificazione (ID immagine)    -> logo mostrato prima del form (NON è la featured image)
 *
 * Tutto tramite la media library nativa di WordPress (wp.media),
 * salvataggio protetto da nonce, sanitizzazione su ogni campo.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class MAS_Cert_Meta {

	// Chiavi meta (con underscore iniziale = nascoste dalle custom fields UI standard).
	const META_SOTTOTITOLO = '_mas_cert_sottotitolo';
	const META_PDF_ID      = '_mas_cert_pdf_id';
	const META_LOGO_ID     = '_mas_cert_logo_id';

	// Nonce.
	const NONCE_ACTION = 'mas_cert_save_meta';
	const NONCE_FIELD  = 'mas_cert_meta_nonce';

	/**
	 * Aggancia gli hook.
	 */
	public function register_hooks() {
		add_action( 'add_meta_boxes', array( $this, 'add_meta_boxes' ) );
		add_action( 'save_post_' . MAS_CERT_CPT, array( $this, 'save_meta' ), 10, 2 );
		// Carica wp.media solo nelle schermate di edit del nostro CPT.
		add_action( 'admin_enqueue_scripts', array( $this, 'enqueue_admin_assets' ) );
	}

	/**
	 * Registra la meta box principale.
	 */
	public function add_meta_boxes() {
		add_meta_box(
			'mas_cert_dettagli',
			__( 'Dettagli certificazione', 'mas-certificazioni' ),
			array( $this, 'render_meta_box' ),
			MAS_CERT_CPT,
			'normal',
			'high'
		);
	}

	/**
	 * Carica gli script della media library + il piccolo JS che gestisce
	 * i bottoni "Seleziona / Rimuovi" dei campi media, solo nelle schermate
	 * di modifica del nostro CPT.
	 *
	 * @param string $hook Hook della schermata admin corrente.
	 */
	public function enqueue_admin_assets( $hook ) {
		// Solo nelle pagine post.php / post-new.php.
		if ( 'post.php' !== $hook && 'post-new.php' !== $hook ) {
			return;
		}

		$screen = get_current_screen();
		if ( ! $screen || MAS_CERT_CPT !== $screen->post_type ) {
			return;
		}

		// Media library nativa.
		wp_enqueue_media();

		// JS inline minimale per i picker (text/plain per evitare file extra).
		wp_register_script( 'mas-cert-admin', '', array( 'jquery' ), MAS_CERT_VERSION, true );
		wp_enqueue_script( 'mas-cert-admin' );
		wp_add_inline_script( 'mas-cert-admin', $this->get_admin_inline_js() );
	}

	/**
	 * Renderizza il contenuto della meta box.
	 *
	 * @param WP_Post $post Post corrente.
	 */
	public function render_meta_box( $post ) {

		// Nonce di sicurezza.
		wp_nonce_field( self::NONCE_ACTION, self::NONCE_FIELD );

		// Valori salvati.
		$sottotitolo = get_post_meta( $post->ID, self::META_SOTTOTITOLO, true );
		$pdf_id      = (int) get_post_meta( $post->ID, self::META_PDF_ID, true );
		$logo_id     = (int) get_post_meta( $post->ID, self::META_LOGO_ID, true );

		$pdf_url   = $pdf_id ? wp_get_attachment_url( $pdf_id ) : '';
		$logo_url  = $logo_id ? wp_get_attachment_image_url( $logo_id, 'medium' ) : '';
		?>
		<style>
			.mas-cert-field { margin: 0 0 22px; }
			.mas-cert-field > label { display:block; font-weight:600; margin-bottom:6px; }
			.mas-cert-field .description { color:#646970; font-style:italic; }
			.mas-cert-media-preview { margin:8px 0; }
			.mas-cert-media-preview img { max-width:160px; height:auto; border:1px solid #dcdcde; border-radius:4px; display:block; }
			.mas-cert-pdf-name { display:inline-block; padding:4px 8px; background:#f0f0f1; border-radius:3px; }
		</style>

		<!-- SOTTOTITOLO -->
		<div class="mas-cert-field">
			<label for="mas_cert_sottotitolo"><?php esc_html_e( 'Sottotitolo', 'mas-certificazioni' ); ?></label>
			<input
				type="text"
				id="mas_cert_sottotitolo"
				name="mas_cert_sottotitolo"
				class="widefat"
				value="<?php echo esc_attr( $sottotitolo ); ?>"
				placeholder="<?php esc_attr_e( 'Es. Sistema di gestione per la sicurezza alimentare', 'mas-certificazioni' ); ?>"
			/>
			<p class="description"><?php esc_html_e( 'Riga descrittiva mostrata sotto il titolo (card e dettaglio).', 'mas-certificazioni' ); ?></p>
		</div>

		<!-- PDF CERTIFICAZIONE -->
		<div class="mas-cert-field">
			<label><?php esc_html_e( 'PDF certificazione', 'mas-certificazioni' ); ?></label>
			<input type="hidden" id="mas_cert_pdf_id" name="mas_cert_pdf_id" value="<?php echo esc_attr( $pdf_id ); ?>" />
			<div class="mas-cert-media-preview" id="mas_cert_pdf_preview">
				<?php if ( $pdf_url ) : ?>
					<span class="mas-cert-pdf-name"><?php echo esc_html( basename( $pdf_url ) ); ?></span>
				<?php endif; ?>
			</div>
			<button type="button" class="button mas-cert-media-select"
				data-target="#mas_cert_pdf_id"
				data-preview="#mas_cert_pdf_preview"
				data-type="application/pdf"
				data-mode="pdf"
				data-title="<?php esc_attr_e( 'Seleziona il PDF della certificazione', 'mas-certificazioni' ); ?>">
				<?php esc_html_e( 'Seleziona PDF', 'mas-certificazioni' ); ?>
			</button>
			<button type="button" class="button mas-cert-media-remove"
				data-target="#mas_cert_pdf_id"
				data-preview="#mas_cert_pdf_preview">
				<?php esc_html_e( 'Rimuovi', 'mas-certificazioni' ); ?>
			</button>
			<p class="description"><?php esc_html_e( 'Aperto in lightbox dall\'icona occhio e dal bottone "Visualizza PDF". Solo visualizzazione, nessun download.', 'mas-certificazioni' ); ?></p>
		</div>

		<!-- LOGO CERTIFICAZIONE -->
		<div class="mas-cert-field">
			<label><?php esc_html_e( 'Logo certificazione', 'mas-certificazioni' ); ?></label>
			<input type="hidden" id="mas_cert_logo_id" name="mas_cert_logo_id" value="<?php echo esc_attr( $logo_id ); ?>" />
			<div class="mas-cert-media-preview" id="mas_cert_logo_preview">
				<?php if ( $logo_url ) : ?>
					<img src="<?php echo esc_url( $logo_url ); ?>" alt="" />
				<?php endif; ?>
			</div>
			<button type="button" class="button mas-cert-media-select"
				data-target="#mas_cert_logo_id"
				data-preview="#mas_cert_logo_preview"
				data-type="image"
				data-mode="image"
				data-title="<?php esc_attr_e( 'Seleziona il logo', 'mas-certificazioni' ); ?>">
				<?php esc_html_e( 'Seleziona logo', 'mas-certificazioni' ); ?>
			</button>
			<button type="button" class="button mas-cert-media-remove"
				data-target="#mas_cert_logo_id"
				data-preview="#mas_cert_logo_preview">
				<?php esc_html_e( 'Rimuovi', 'mas-certificazioni' ); ?>
			</button>
			<p class="description"><?php esc_html_e( 'Mostrato subito prima del form nella pagina di dettaglio. NON è l\'immagine in evidenza.', 'mas-certificazioni' ); ?></p>
		</div>
		<?php
	}

	/**
	 * Salva i meta in modo sicuro.
	 *
	 * @param int     $post_id ID del post.
	 * @param WP_Post $post    Oggetto post.
	 */
	public function save_meta( $post_id, $post ) {

		// 1. Verifica nonce.
		if ( ! isset( $_POST[ self::NONCE_FIELD ] )
			|| ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST[ self::NONCE_FIELD ] ) ), self::NONCE_ACTION ) ) {
			return;
		}

		// 2. Niente salvataggio durante autosave.
		if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
			return;
		}

		// 3. Verifica permessi.
		if ( ! current_user_can( 'edit_post', $post_id ) ) {
			return;
		}

		// 4. Solo il nostro CPT.
		if ( MAS_CERT_CPT !== $post->post_type ) {
			return;
		}

		// --- SOTTOTITOLO (testo) ---
		if ( isset( $_POST['mas_cert_sottotitolo'] ) ) {
			$sottotitolo = sanitize_text_field( wp_unslash( $_POST['mas_cert_sottotitolo'] ) );
			update_post_meta( $post_id, self::META_SOTTOTITOLO, $sottotitolo );
		}

		// --- PDF (ID allegato) ---
		if ( isset( $_POST['mas_cert_pdf_id'] ) ) {
			$pdf_id = absint( wp_unslash( $_POST['mas_cert_pdf_id'] ) );
			if ( $pdf_id > 0 ) {
				update_post_meta( $post_id, self::META_PDF_ID, $pdf_id );
			} else {
				delete_post_meta( $post_id, self::META_PDF_ID );
			}
		}

		// --- LOGO (ID immagine) ---
		if ( isset( $_POST['mas_cert_logo_id'] ) ) {
			$logo_id = absint( wp_unslash( $_POST['mas_cert_logo_id'] ) );
			if ( $logo_id > 0 ) {
				update_post_meta( $post_id, self::META_LOGO_ID, $logo_id );
			} else {
				delete_post_meta( $post_id, self::META_LOGO_ID );
			}
		}
	}

	/**
	 * JS inline per i picker della media library (select + remove).
	 *
	 * @return string
	 */
	private function get_admin_inline_js() {
		return <<<JS
jQuery(function($){
	var frame;

	// Apertura media frame.
	$(document).on('click', '.mas-cert-media-select', function(e){
		e.preventDefault();
		var \$btn     = $(this);
		var target   = \$btn.data('target');
		var preview  = \$btn.data('preview');
		var mode     = \$btn.data('mode');   // 'pdf' | 'image'
		var type     = \$btn.data('type');   // mime/type o 'image'
		var title    = \$btn.data('title');

		frame = wp.media({
			title: title,
			button: { text: 'Usa questo' },
			library: { type: type },
			multiple: false
		});

		frame.on('select', function(){
			var att = frame.state().get('selection').first().toJSON();
			$(target).val(att.id);

			if (mode === 'image') {
				var src = (att.sizes && att.sizes.medium) ? att.sizes.medium.url : att.url;
				$(preview).html('<img src="' + src + '" alt="" />');
			} else {
				var name = att.filename || att.title || 'documento.pdf';
				$(preview).html('<span class="mas-cert-pdf-name">' + name + '</span>');
			}
		});

		frame.open();
	});

	// Rimozione.
	$(document).on('click', '.mas-cert-media-remove', function(e){
		e.preventDefault();
		var \$btn = $(this);
		$(\$btn.data('target')).val('');
		$(\$btn.data('preview')).empty();
	});
});
JS;
	}
}
