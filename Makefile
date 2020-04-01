.DEFAULT_GOAL := lint

# Get variables from ENV
TWINE_USERNAME := ${TWINE_USERNAME}
TWINE_PASSWORD := ${TWINE_PASSWORD}
TWINE_REPOSITORY_URL := ${TWINE_REPOSITORY_URL}

# If .env file is found, assign variables from this source (overriding existing)
ifneq (,$(wildcard .env))
    $(info FOUND .env File.)
    include .env
endif


REQUIREMENTS="requirements-dev.txt"
REQUIREMENTS27="requirements-dev-py27.txt"
REQUIREMENTS_DOCS="docs/requirements.txt"
PROJECT="workflow_tools"

isort = isort --recursive --check-only ${PROJECT}
black = black --check ${PROJECT}
flake8 = flake8 ${PROJECT}
pytest = pytest tests -vvs --cov=${PROJECT}

ifeq ($(PYTHON_VERSION),2.7)
    install_deps = pip install -U -r ${REQUIREMENTS27}
    black = @echo "Skip black for Python 2.7"
else
    install_deps = pip install -U -r ${REQUIREMENTS}
    black = black --check ${PROJECT}
endif

install:
	@echo "Install package and its dependencies"
	$(install_deps)
	pip install -e .
	@echo "Done"

hooks:
	@echo "Install pre-commit hooks"
	pre-commit install --install-hooks
	@echo "Done"

uninstall:
	@echo "Uninstall package"
	@pip uninstall ${PROJECT} -y
	@echo "Done"

lint:
	@echo "Run linters"
	$(isort)
	$(black)
	$(flake8)
	@echo "Done"

test:
	@echo "Run tests"
	$(pytest)
	@echo "Done"


check-package:
	@echo "Check package"
	python setup.py check -ms
	python setup.py sdist
	twine check dist/*
	@echo "Done"

build:
	@echo "Build and push Python package"
	python setup.py sdist bdist_wheel
	twine upload dist/*
	@echo "Done"

build_docs:
	@echo "Build documentation"
	pip install -r ${REQUIREMENTS_DOCS}
	make -C docs html
	@echo "Done"

docs: install build_docs

clean:
	@echo "Clean up files"
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	python setup.py clean
	@echo "Done"

.PHONY: install hooks uninstall lint test check-package build build_docs docs clean
