<?php
/**
 * TEMPLATE ARCHIVIO — /certificazioni/
 *
 * Struttura: header + barra tab (ISO / Macchine) + campo ricerca + griglia card.
 * Tutte le certificazioni vengono renderizzate (filtro/ricerca client-side via JS).
 *
 * =====================================================================
 * STEP 0 — DA VERIFICARE SUL SITO REALE PRIMA DEL GO-LIVE
 * ---------------------------------------------------------------------
 * Le classi qui sotto (eltdf-btn eltdf-btn-medium eltdf-btn-solid, wrapper
 * vc_row/wpb_column ecc.) sono quelle STANDARD dei temi Edge/Qode su WPBakery.
 * Ispeziona la sezione "Corsi" del sito MAS e, se trovi classi diverse per
 * card / immagine / titolo / bottone CTA, allineale qui. In particolare:
 *   - bottone CTA: tipicamente <a class="eltdf-btn eltdf-btn-medium eltdf-btn-solid">
 *   - card corso: cerca il contenitore della singola card e replica wrapper/classi.
 * Le misure (margin/padding) seguono il sito attuale: il Figma è indicativo.
 * =====================================================================
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

// Recupero TUTTE le certificazioni, ordinate per menu_order ASC (priorità).
$cert_query = new WP_Query(
	array(
		'post_type'      => MAS_CERT_CPT,
		'post_status'    => 'publish',
		'posts_per_page' => -1,
		'orderby'        => 'menu_order',
		'order'          => 'ASC',
	)
);

// Recupero i termini esistenti per costruire i tab dinamicamente.
$cert_terms = get_terms(
	array(
		'taxonomy'   => MAS_CERT_TAX,
		'hide_empty' => false,
		'orderby'    => 'name',
		'order'      => 'ASC',
	)
);
?>

<!-- Wrapper esterno con classi WPBakery del tema per ereditare il layout del sito. -->
<div class="vc_row wpb_row vc_row-fluid mas-cert-archive">
	<div class="wpb_column vc_column_container vc_col-sm-12">
		<div class="vc_column-inner">
			<div class="wpb_wrapper">

				<!-- HEADER -->
				<header class="mas-cert-header">
					<h1 class="mas-cert-archive-title"><?php esc_html_e( 'Certificazioni', 'mas-certificazioni' ); ?></h1>
				</header>

				<!-- BARRA TAB + RICERCA -->
				<div class="mas-cert-toolbar">

					<div class="mas-cert-tabs" role="tablist" aria-label="<?php esc_attr_e( 'Filtra per categoria', 'mas-certificazioni' ); ?>">
						<!-- Tab "Tutte" sempre presente come reset -->
						<button type="button" class="mas-cert-tab is-active" data-filter="*">
							<?php esc_html_e( 'Tutte', 'mas-certificazioni' ); ?>
						</button>
						<?php
						if ( ! empty( $cert_terms ) && ! is_wp_error( $cert_terms ) ) :
							foreach ( $cert_terms as $term ) :
								?>
								<button type="button" class="mas-cert-tab" data-filter="<?php echo esc_attr( $term->slug ); ?>">
									<?php echo esc_html( $term->name ); ?>
								</button>
								<?php
							endforeach;
						endif;
						?>
					</div>

					<div class="mas-cert-search">
						<!-- Icona ricerca interna (mockup) -->
						<svg class="mas-cert-search-icon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
							<path fill="currentColor" d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 10-.7.7l.27.28v.79l5 5L20.49 19l-5-5zm-6 0A4.5 4.5 0 1114 9.5 4.49 4.49 0 019.5 14z"/>
						</svg>
						<input
							type="search"
							id="mas-cert-search-input"
							class="mas-cert-search-input"
							placeholder="<?php esc_attr_e( 'Cerca certificazione', 'mas-certificazioni' ); ?>"
							aria-label="<?php esc_attr_e( 'Cerca certificazione', 'mas-certificazioni' ); ?>"
						/>
					</div>
				</div>

				<!-- GRIGLIA CARD (3 col desktop / 1 col mobile via CSS) -->
				<div class="mas-cert-grid" id="mas-cert-grid">
					<?php
					if ( $cert_query->have_posts() ) :
						while ( $cert_query->have_posts() ) :
							$cert_query->the_post();

							$post_id      = get_the_ID();
							$sottotitolo  = MAS_Cert_Templates::get_sottotitolo( $post_id );
							$pdf_url      = MAS_Cert_Templates::get_pdf_url( $post_id );
							$cat_slugs    = MAS_Cert_Templates::get_categoria_slugs( $post_id );

							// Stringa di ricerca: titolo + sottotitolo (lowercase lato JS).
							$search_blob  = trim( get_the_title() . ' ' . $sottotitolo );
							?>

							<!-- Singola card -->
							<article
								class="mas-cert-card"
								data-categoria="<?php echo esc_attr( $cat_slugs ); ?>"
								data-search="<?php echo esc_attr( $search_blob ); ?>"
							>
								<!-- Immagine card (featured image) + icona occhio per PDF -->
								<div class="mas-cert-card-media">
									<?php if ( has_post_thumbnail() ) : ?>
										<?php the_post_thumbnail( 'large', array( 'class' => 'mas-cert-card-img' ) ); ?>
									<?php endif; ?>

									<?php if ( $pdf_url ) : ?>
										<!-- Icona occhio: apre il PDF in lightbox (solo visualizzazione) -->
										<button
											type="button"
											class="mas-cert-eye"
											data-pdf="<?php echo esc_url( $pdf_url ); ?>"
											aria-label="<?php esc_attr_e( 'Visualizza PDF', 'mas-certificazioni' ); ?>"
											title="<?php esc_attr_e( 'Visualizza PDF', 'mas-certificazioni' ); ?>"
										>
											<!-- Icona occhio inline (SVG) -->
											<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">
												<path fill="currentColor" d="M12 5c-7 0-10 7-10 7s3 7 10 7 10-7 10-7-3-7-10-7zm0 11a4 4 0 110-8 4 4 0 010 8zm0-6a2 2 0 100 4 2 2 0 000-4z"/>
											</svg>
										</button>
									<?php endif; ?>
								</div>

								<!-- Corpo card -->
								<div class="mas-cert-card-body">
									<h3 class="mas-cert-card-title"><?php the_title(); ?></h3>

									<?php if ( $sottotitolo ) : ?>
										<p class="mas-cert-card-subtitle"><?php echo esc_html( $sottotitolo ); ?></p>
									<?php endif; ?>

									<?php if ( has_excerpt() ) : ?>
										<!-- Anteprima 3 righe (excerpt nativo); il clamp a 3 righe è nel CSS -->
										<div class="mas-cert-card-excerpt"><?php the_excerpt(); ?></div>
									<?php endif; ?>

									<!-- CTA verso la single. Classi bottone del tema (STEP 0). -->
									<a href="<?php the_permalink(); ?>" class="eltdf-btn eltdf-btn-medium eltdf-btn-solid mas-cert-card-cta">
										<span class="eltdf-btn-text"><?php esc_html_e( 'Apri documento', 'mas-certificazioni' ); ?></span>
									</a>
								</div>
							</article>

							<?php
						endwhile;
						wp_reset_postdata();
					else :
						?>
						<p class="mas-cert-empty"><?php esc_html_e( 'Nessuna certificazione disponibile al momento.', 'mas-certificazioni' ); ?></p>
						<?php
					endif;
					?>
				</div>

				<!-- Messaggio "nessun risultato" per il filtro client-side (nascosto di default) -->
				<p class="mas-cert-no-results" id="mas-cert-no-results" hidden>
					<?php esc_html_e( 'Nessuna certificazione corrisponde alla ricerca.', 'mas-certificazioni' ); ?>
				</p>

			</div>
		</div>
	</div>
</div>

<!-- Lightbox PDF condivisa (markup unico, riusato da occhio e bottoni) -->
<div class="mas-cert-lightbox" id="mas-cert-lightbox" hidden aria-hidden="true" role="dialog" aria-modal="true">
	<div class="mas-cert-lightbox-overlay" data-close="1"></div>
	<div class="mas-cert-lightbox-inner">
		<button type="button" class="mas-cert-lightbox-close" data-close="1" aria-label="<?php esc_attr_e( 'Chiudi', 'mas-certificazioni' ); ?>">&times;</button>
		<!-- L'embed del PDF viene iniettato qui via JS. Nessun bottone di download. -->
		<div class="mas-cert-lightbox-content" id="mas-cert-lightbox-content"></div>
	</div>
</div>

<?php
get_footer();
