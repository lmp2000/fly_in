PYTHON := python3
APP := main.py
VENV := .venv
VENV_PY := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

.PHONY: help install run visual debug lint lint-strict clean

help:
	@echo "Fly-in — Autonomous Drone Fleet Routing"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Create virtual environment and install dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run           Run with terminal map selector"
	@echo "  make visual        Run with terminal map selector and pygame visualizer"
	@echo "  make debug         Run with Python debugger"
	@echo ""
	@echo "Quality:"
	@echo "  make lint          Run flake8 and required mypy checks"
	@echo "  make lint-strict   Run flake8 and strict mypy checks"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove Python cache files"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip

install: $(VENV)/bin/activate
	$(VENV_PIP) install -r requirements.txt

run: install
	$(VENV_PY) $(APP)

visual: install
	$(VENV_PY) $(APP) --visual

debug: install
	$(VENV_PY) -m pdb $(APP)

lint: install
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete

test: install
	$(VENV_PY) -m tests.test_phase6
