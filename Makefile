TOX=tox

.PHONY: lint
lint:
	$(TOX) -c tox.ini -e lint

.PHONY: fmt
fmt:
	isort --recursive setup.py src tests
	black .

.PHONY: fmt-travis
fmt-travis:
	isort --recursive --diff --check-only setup.py src tests
	black . --check

.PHONY: coverage
coverage:
	$(TOX) -c tox.ini -e coverage

.PHONY: test
test:
	$(TOX) -c tox.ini -e test

.PHONY: archive
archive:
	git archive --output=./justbases.tar.gz HEAD

.PHONY: upload-release
upload-release:
	python setup.py register sdist upload

.PHONY: yamllint
yamllint:
	yamllint --strict .github/workflows/main.yml
