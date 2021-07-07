.PHONY: translations install_precommit test_precommit fmt

# Create the .po and .mo files used for i18n
translations:
	cd src/logpipe && \
	django-admin makemessages -a && \
	django-admin compilemessages

install_precommit:
	pre-commit install

test_precommit: install_precommit
	pre-commit run --all-files

fmt:
	black .
