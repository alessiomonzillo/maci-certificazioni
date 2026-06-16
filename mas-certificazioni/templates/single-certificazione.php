<?php
/**
 * TEMPLATE SINGOLO — /certificazioni/{slug}/
 *
 * Ordine: "Torna indietro" + label categoria + titolo + sottotitolo + intro,
 * hero (featured image con bottone "Visualizza PDF" sovrapposto),
 * post_content (sezioni numerate), logo_certificazione, blocco form CF7.
 *
 * =====================================================================
 * STEP 0 — classi bottone del tema (eltdf-btn ...): vedi nota nell'archivio.
 * Verifica sul sito reale e allinea se necessario.
 * =====================================================================
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

while ( have_posts() ) :
	the_post();

	$post_id     = get_the_ID();
	$sottotitolo = MAS_Cert_Templates::get_sottotitolo( $post_id );
	$pdf_url     = MAS_Cert_Templates::get_pdf_url( $post_id );
	$logo_id     = MAS_Cert_Templates::get_logo_id( $post_id );
	$cat_label   = MAS_Cert_Templates::get_categoria_label( $post_id );

	// URL dell'archivio per il "Torna indietro".
	$archive_url = get_post_type_archive_link( MAS_CERT_CPT );
	?>

	<div class="vc_row wpb_row vc_row-fluid mas-cert-single">
		<div class="wpb_column vc_column_container vc_col-sm-12">
			<div class="vc_column-inner">
				<div class="wpb_wrapper">

					<!-- TORNA INDIETRO -->
					<?php if ( $archive_url ) : ?>
						<a href="<?php echo esc_url( $archive_url ); ?>" class="mas-cert-back">
							<span aria-hidden="true">&larr;</span> <?php esc_html_e( 'Torna indietro', 'mas-certificazioni' ); ?>
						</a>
					<?php endif; ?>

					<!-- LABEL CATEGORIA — mockup: "Certificazioni ISO" -->
					<?php if ( $cat_label ) : ?>
						<p class="mas-cert-single-cat">
							<?php
							/* translators: %s = nome categoria (es. ISO, Macchine). */
							printf( esc_html__( 'Certificazioni %s', 'mas-certificazioni' ), esc_html( $cat_label ) );
							?>
						</p>
					<?php endif; ?>

					<!-- TITOLO -->
					<h1 class="mas-cert-single-title"><?php the_title(); ?></h1>

					<!-- SOTTOTITOLO -->
					<?php if ( $sottotitolo ) : ?>
						<p class="mas-cert-single-subtitle"><?php echo esc_html( $sottotitolo ); ?></p>
					<?php endif; ?>

					<!-- INTRO = excerpt nativo (riga introduttiva sopra l'hero) -->
					<?php if ( has_excerpt() ) : ?>
						<div class="mas-cert-single-intro"><?php the_excerpt(); ?></div>
					<?php endif; ?>

					<!-- HERO: featured image + bottone "Visualizza PDF" sovrapposto -->
					<?php if ( has_post_thumbnail() ) : ?>
						<div class="mas-cert-hero">
							<?php the_post_thumbnail( 'full', array( 'class' => 'mas-cert-hero-img' ) ); ?>

							<?php if ( $pdf_url ) : ?>
								<!-- Bottone "Visualizza PDF" rosso con icona occhio (apre lightbox, no download). -->
								<button
									type="button"
									class="eltdf-btn eltdf-btn-medium eltdf-btn-solid mas-cert-hero-pdf"
									data-pdf="<?php echo esc_url( $pdf_url ); ?>"
								>
									<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">
										<path fill="currentColor" d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7zm0 11a4 4 0 110-8 4 4 0 010 8zm0-6a2 2 0 100 4 2 2 0 000-4z"/>
									</svg>
									<span class="eltdf-btn-text"><?php esc_html_e( 'Visualizza PDF', 'mas-certificazioni' ); ?></span>
								</button>
							<?php endif; ?>
						</div>
					<?php endif; ?>

					<!-- CONTENUTO APPROFONDITO = post_content (intro + sezioni numerate) -->
					<div class="mas-cert-single-content">
						<?php the_content(); ?>
					</div>

					<!-- LOGO CERTIFICAZIONE: subito prima del form. NON è la featured image. -->
					<?php if ( $logo_id ) : ?>
						<div class="mas-cert-logo">
							<?php
							echo wp_get_attachment_image(
								$logo_id,
								'medium',
								false,
								array( 'class' => 'mas-cert-logo-img', 'alt' => esc_attr( get_the_title() ) )
							);
							?>
						</div>
					<?php endif; ?>

					<?php
					/*
					 * BLOCCO FORM — wrapper del tema replicato ESATTAMENTE come da specifica,
					 * con lo shortcode CF7 iniettato al posto indicato.
					 * Il destinatario (info@masprevenzione.it) è configurato lato CF7 admin:
					 * questo plugin NON invia email.
					 */
					$cf7_shortcode = sprintf( '[contact-form-7 id="%d"]', (int) MAS_CERT_CF7_ID );
					?>
					<div class="vc_row wpb_row vc_row-fluid vc_row-has-fill"><div class="wpb_column vc_column_container vc_col-sm-12"><div class="vc_column-inner"><div class="wpb_wrapper"><div class="eltdf-elements-holder eltdf-one-column eltdf-responsive-mode-768"><div class="eltdf-eh-item"><div class="eltdf-eh-item-inner"><div class="eltdf-eh-item-content" style="padding:13px 40px 30px 40px"><div class="wpb_text_column wpb_content_element"><div class="wpb_wrapper"><h3><?php esc_html_e( 'Ricevi più informazioni su questa certificazione', 'mas-certificazioni' ); ?></h3></div></div> <?php echo do_shortcode( $cf7_shortcode ); ?> </div></div></div></div></div></div></div></div>

				</div>
			</div>
		</div>
	</div>

	<!-- Lightbox PDF (stesso markup dell'archivio, riusato dal JS) -->
	<div class="mas-cert-lightbox" id="mas-cert-lightbox" hidden aria-hidden="true" role="dialog" aria-modal="true">
		<div class="mas-cert-lightbox-overlay" data-close="1"></div>
		<div class="mas-cert-lightbox-inner">
			<button type="button" class="mas-cert-lightbox-close" data-close="1" aria-label="<?php esc_attr_e( 'Chiudi', 'mas-certificazioni' ); ?>">&times;</button>
			<div class="mas-cert-lightbox-content" id="mas-cert-lightbox-content"></div>
		</div>
	</div>

	<?php
endwhile;

get_footer();
