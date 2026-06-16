/**
 * MAS Certificazioni — front-end
 * - Tab: filtro per categoria (data-categoria) senza reload
 * - Ricerca: filtro testuale su titolo+sottotitolo (data-search) senza reload
 * - Lightbox PDF: visualizzazione inline via <embed>, NESSUN download
 *
 * NOTA SICUREZZA: la mancanza del bottone "download" è solo lato UI.
 * L'URL del PDF resta tecnicamente accessibile a chi conosce il link.
 */
(function () {
	'use strict';

	document.addEventListener('DOMContentLoaded', function () {

		var i18n = window.masCertI18n || { closeLabel: 'Chiudi', pdfMissing: 'PDF non disponibile.' };

		/* =================================================================
		 * 1) FILTRO TAB + RICERCA  (solo se siamo nell'archivio)
		 * ============================================================== */
		var grid = document.getElementById('mas-cert-grid');

		if (grid) {
			var tabs       = Array.prototype.slice.call(document.querySelectorAll('.mas-cert-tab'));
			var cards      = Array.prototype.slice.call(grid.querySelectorAll('.mas-cert-card'));
			var searchEl   = document.getElementById('mas-cert-search-input');
			var noResults  = document.getElementById('mas-cert-no-results');

			// Stato corrente del filtro.
			var currentCategory = '*';
			var currentSearch   = '';

			/**
			 * Applica i filtri combinati (categoria + testo) e mostra/nasconde le card.
			 */
			function applyFilters() {
				var visibleCount = 0;

				cards.forEach(function (card) {
					// --- match categoria ---
					var cardCats = (card.getAttribute('data-categoria') || '').split(/\s+/);
					var matchCat = (currentCategory === '*') || cardCats.indexOf(currentCategory) !== -1;

					// --- match ricerca ---
					var blob = (card.getAttribute('data-search') || '').toLowerCase();
					var matchSearch = (currentSearch === '') || blob.indexOf(currentSearch) !== -1;

					if (matchCat && matchSearch) {
						card.hidden = false;
						visibleCount++;
					} else {
						card.hidden = true;
					}
				});

				// Messaggio "nessun risultato".
				if (noResults) {
					noResults.hidden = (visibleCount !== 0);
				}
			}

			// Click sui tab.
			tabs.forEach(function (tab) {
				tab.addEventListener('click', function () {
					tabs.forEach(function (t) { t.classList.remove('is-active'); });
					tab.classList.add('is-active');
					currentCategory = tab.getAttribute('data-filter') || '*';
					applyFilters();
				});
			});

			// Input ricerca (con debounce leggero).
			if (searchEl) {
				var debounceTimer = null;
				searchEl.addEventListener('input', function () {
					clearTimeout(debounceTimer);
					debounceTimer = setTimeout(function () {
						currentSearch = searchEl.value.trim().toLowerCase();
						applyFilters();
					}, 120);
				});
			}
		}

		/* =================================================================
		 * 2) LIGHTBOX PDF  (archivio + single)
		 * ============================================================== */
		var lightbox        = document.getElementById('mas-cert-lightbox');
		var lightboxContent = document.getElementById('mas-cert-lightbox-content');

		/**
		 * Apre la lightbox con il PDF indicato.
		 * @param {string} pdfUrl
		 */
		function openPdf(pdfUrl) {
			if (!lightbox || !lightboxContent) { return; }

			if (!pdfUrl) {
				lightboxContent.innerHTML = '<p class="mas-cert-pdf-missing">' + i18n.pdfMissing + '</p>';
			} else {
				// Visualizzazione inline. #toolbar=0 nasconde la barra (incluso download) nei viewer
				// che lo supportano: è comunque solo un suggerimento lato UI, non una protezione reale.
				var src = pdfUrl + '#toolbar=0&navpanes=0&view=FitH';
				lightboxContent.innerHTML =
					'<embed src="' + encodeURI(src) + '" type="application/pdf" class="mas-cert-pdf-embed" />';
			}

			lightbox.hidden = false;
			lightbox.setAttribute('aria-hidden', 'false');
			document.body.classList.add('mas-cert-lightbox-open');
		}

		/**
		 * Chiude la lightbox e svuota il contenuto (ferma il rendering del PDF).
		 */
		function closePdf() {
			if (!lightbox || !lightboxContent) { return; }
			lightbox.hidden = true;
			lightbox.setAttribute('aria-hidden', 'true');
			lightboxContent.innerHTML = '';
			document.body.classList.remove('mas-cert-lightbox-open');
		}

		// Apertura: qualsiasi elemento con attributo data-pdf (icona occhio card + bottone hero).
		document.addEventListener('click', function (e) {
			var trigger = e.target.closest ? e.target.closest('[data-pdf]') : null;
			if (trigger) {
				e.preventDefault();
				openPdf(trigger.getAttribute('data-pdf'));
			}
		});

		// Chiusura: overlay, bottone X, tasto ESC.
		if (lightbox) {
			lightbox.addEventListener('click', function (e) {
				if (e.target.getAttribute('data-close') === '1') {
					closePdf();
				}
			});
		}
		document.addEventListener('keydown', function (e) {
			if (e.key === 'Escape' && lightbox && !lightbox.hidden) {
				closePdf();
			}
		});
	});
})();
