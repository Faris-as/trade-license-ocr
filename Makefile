# Trade License OCR — dev commands
# Requires `make` and python3 (3.10–3.11). On Windows, follow the manual
# commands in README.md — or use WSL, where this file works as-is.

VENV       := .venv
PYTHON     := $(VENV)/bin/python
PIP        := $(VENV)/bin/pip
MODEL_PATH := ml_models/roboflow_model/model.pt
MODEL_URL  := https://github.com/Faris-as/trade-license-ocr/releases/download/v1.0.0/model.pt

.DEFAULT_GOAL := help
.PHONY: help setup model serve serve-prod test test-model test-ocr clean

help:
	@echo "Trade License OCR commands:"
	@echo "  make setup      create venv + install deps (incl. pytest)"
	@echo "  make model      download model.pt from the v1.0.0 release"
	@echo "  make serve      run the dev server (uvicorn + autoreload)"
	@echo "  make serve-prod production-style server (no reload)"
	@echo "  make test       run parser unit tests (no model needed)"
	@echo "  make test-model manual YOLO detection harness"
	@echo "  make test-ocr   manual OCR pipeline harness"
	@echo "  make clean      remove venv, caches, and runtime artifacts"

# The venv itself is the real target: reruns only refresh the deps
$(PYTHON):
	python3 -m venv $(VENV)
	$(PIP) install --quiet -e ".[dev]"

setup: $(PYTHON)
	@echo "✅ setup done — next: make model"

$(MODEL_PATH):
	@mkdir -p $(dir $(MODEL_PATH))
	curl -L -o $(MODEL_PATH) $(MODEL_URL)

model: $(MODEL_PATH)
	@du -sh $(MODEL_PATH)

serve: setup model
	$(PYTHON) run.py

serve-prod: setup model
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

test: setup
	$(PYTHON) -m pytest tests/ -q

test-model: setup model
	@test -f uploads/trade_license_sample.jpg \
		|| (echo "❌ Need a sample license at uploads/trade_license_sample.jpg"; exit 1)
	$(PYTHON) test_model.py

test-ocr: setup model
	@test -f uploads/trade_license_sample.jpg \
		|| (echo "❌ Need a sample license at uploads/trade_license_sample.jpg"; exit 1)
	$(PYTHON) test_ocr_pipeline.py

clean:
	rm -rf $(VENV) .pytest_cache
	find . -name "__pycache__" -exec rm -rf {} +
	find uploads -mindepth 1 -not -name ".gitkeep" -exec rm -rf {} +
	@echo "✅ clean — next: make setup && make model to restore"
