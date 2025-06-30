ifeq ($(origin MONKEYTYPE), undefined)
  PYTHON = python3
else
  PYTHON = MONKEYTYPE_TRACE_MODULES=hs_dbus_signature monkeytype run
endif

.PHONY: lint
lint:
	pylint setup.py
	pylint src/hs_dbus_signature
	pylint tests
	pyright

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
	${PYTHON} -m unittest discover --verbose tests

.PHONY: yamllint
yamllint:
	yamllint --strict .github/workflows/*.yml

.PHONY: package
package:
	(umask 0022; python -m build; python -m twine check --strict ./dist/*)

.PHONY: legacy-package
legacy-package:
	python3 setup.py build
	python3 setup.py install
