# Create the .po and .mo files used for i18n
.PHONY: translations
translations:
	cd logpipe && \
	django-admin makemessages -a && \
	django-admin compilemessages

.PHONY: install_precommit
install_precommit:
	pre-commit install

.PHONY: test_precommit
test_precommit: install_precommit
	pre-commit run --all-files

.PHONY: docs_serve
docs_serve: docs_vendor
	DJANGO_SETTINGS_MODULE=logpipe.docgen_setup uv run zensical serve

.PHONY: docs_build
docs_build: docs_vendor
	DJANGO_SETTINGS_MODULE=logpipe.docgen_setup uv run zensical build --strict
	uv run python bin/check-docs-csp.py build/mkdocs \
		--unused https://unpkg.com/ace-builds@ \
		--unused https://unpkg.com/pyodide@ \
		--unused https://cdn.jsdelivr.net/pyodide/ \
		--unused https://unpkg.com/resize-observer-polyfill \
		--unused https://unpkg.com/glightbox@ \
		--unused https://unpkg.com/mermaid@

.PHONY: docs_vendor
docs_vendor:
	uv run python bin/vendor-docs-assets.py

docs: docs_build
	rm -rf public/ && \
	mkdir -p public/ && \
	cp -r build/mkdocs/* public/
