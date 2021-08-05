TOX=tox

.PHONY: lint
lint:
	pylint setup.py
	pylint src/hs_dbus_signature
	pylint tests

.PHONY: fmt
fmt:
	isort setup.py src tests
	black .

.PHONY: fmt-travis
fmt-travis:
	isort --diff --check-only setup.py src tests
	black . --check

.PHONY: coverage
coverage:
	coverage --version
	coverage run --timid --branch -m unittest discover tests
	coverage report -m --fail-under=100 --show-missing --include="./src/*"

.PHONY: test
test:
	python3 -m unittest discover --verbose tests

.PHONY: archive
archive:
	git archive --output=./justbases.tar.gz HEAD

.PHONY: upload-release
upload-release:
	python setup.py register sdist upload

.PHONY: yamllint
yamllint:
	yamllint --strict .github/workflows/main.yml
