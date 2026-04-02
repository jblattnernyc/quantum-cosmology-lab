.DEFAULT_GOAL := help

PYTHON ?= python
PIP := $(PYTHON) -m pip
MINISUPERSPACE_DIR := experiments/minisuperspace_frw
PARTICLE_CREATION_DIR := experiments/particle_creation_flrw
GUT_TOY_GAUGE_DIR := experiments/gut_toy_gauge

.PHONY: help install test test-unittest compile check \
	benchmark run-local run-aer analyze minisuperspace \
	run-ibm run-ibm-local particle-benchmark particle-run-local particle-run-aer \
	particle-analyze particle-creation particle-run-ibm particle-run-ibm-local \
	gut-benchmark gut-run-local gut-run-aer gut-analyze gut-toy-gauge \
	gut-run-ibm gut-run-ibm-local \
	phase6-milestone-report phase6-release-manifest phase6-release \
	clean-cache clean-build clean

help:
	@printf '%s\n' \
		'Quantum Cosmology Lab Makefile' \
		'' \
		'Targets:' \
		'  install         Create or update the editable development install in the active Python environment.' \
		'  test            Run the pytest suite.' \
		'  test-unittest   Run the baseline unittest suite.' \
		'  compile         Compile Python sources as a syntax smoke check.' \
		'  check           Run pytest, unittest, and compile checks.' \
		'  benchmark       Run the minisuperspace FRW benchmark.' \
		'  run-local       Run the minisuperspace exact local workflow.' \
		'  run-aer         Run the minisuperspace noisy local Aer workflow.' \
		'  analyze         Run the minisuperspace analysis workflow.' \
		'  minisuperspace  Run benchmark, exact local, noisy local, and analysis for the official Phase 2 experiment.' \
		'  run-ibm         Run the minisuperspace IBM Runtime workflow. Override BACKEND=<backend-name>.' \
		'  run-ibm-local   Run the minisuperspace IBM Runtime local-testing workflow. Override LOCAL_TESTING_BACKEND=<fake-backend-class>.' \
		'  particle-benchmark   Run the particle-creation FLRW benchmark.' \
		'  particle-run-local   Run the particle-creation exact local workflow.' \
		'  particle-run-aer     Run the particle-creation noisy local Aer workflow.' \
		'  particle-analyze     Run the particle-creation analysis workflow.' \
		'  particle-creation    Run benchmark, exact local, noisy local, and analysis for the official Phase 3 experiment.' \
		'  particle-run-ibm     Run the particle-creation IBM Runtime workflow. Override BACKEND=<backend-name>.' \
		'  particle-run-ibm-local Run the particle-creation IBM Runtime local-testing workflow. Override LOCAL_TESTING_BACKEND=<fake-backend-class>.' \
		'  gut-benchmark     Run the toy-gauge benchmark.' \
		'  gut-run-local     Run the toy-gauge exact local workflow.' \
		'  gut-run-aer       Run the toy-gauge noisy local Aer workflow.' \
		'  gut-analyze       Run the toy-gauge analysis workflow.' \
		'  gut-toy-gauge     Run benchmark, exact local, noisy local, and analysis for the official Phase 5 experiment.' \
		'  gut-run-ibm       Run the toy-gauge IBM Runtime workflow. Override BACKEND=<backend-name>.' \
		'  gut-run-ibm-local Run the toy-gauge IBM Runtime local-testing workflow. Override LOCAL_TESTING_BACKEND=<fake-backend-class>.' \
		'  phase6-milestone-report  Generate the default Phase 6 versioned milestone report.' \
		'  phase6-release-manifest Generate the default Phase 6 archival release manifest.' \
		'  phase6-release     Generate both Phase 6 repository-level release outputs.' \
		'  clean-cache     Remove local cache files and test artifacts.' \
		'  clean-build     Remove local build metadata.' \
		'  clean           Remove local caches and build metadata.' \
		'' \
		'Notes:' \
		'  These targets assume that the repository virtual environment is already active,' \
		'  unless PYTHON is overridden explicitly on the command line.'

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e '.[dev]'

test:
	$(PYTHON) -m pytest

test-unittest:
	$(PYTHON) -m unittest discover -s tests -v

compile:
	$(PYTHON) -m compileall src tests scripts experiments

check: test test-unittest compile

benchmark:
	$(PYTHON) $(MINISUPERSPACE_DIR)/benchmark.py

run-local:
	$(PYTHON) $(MINISUPERSPACE_DIR)/run_local.py

run-aer:
	$(PYTHON) $(MINISUPERSPACE_DIR)/run_aer.py

analyze:
	$(PYTHON) $(MINISUPERSPACE_DIR)/analyze.py

minisuperspace: benchmark run-local run-aer analyze

run-ibm:
	@if [ -z "$(BACKEND)" ]; then \
		printf '%s\n' 'BACKEND is required. Usage: make run-ibm BACKEND=<backend-name>'; \
		exit 1; \
	fi
	$(PYTHON) $(MINISUPERSPACE_DIR)/run_ibm.py --backend-name $(BACKEND)

run-ibm-local:
	@if [ -z "$(LOCAL_TESTING_BACKEND)" ]; then \
		printf '%s\n' 'LOCAL_TESTING_BACKEND is required. Usage: make run-ibm-local LOCAL_TESTING_BACKEND=<fake-backend-class>'; \
		exit 1; \
	fi
	$(PYTHON) $(MINISUPERSPACE_DIR)/run_ibm.py --local-testing-backend $(LOCAL_TESTING_BACKEND)

particle-benchmark:
	$(PYTHON) $(PARTICLE_CREATION_DIR)/benchmark.py

particle-run-local:
	$(PYTHON) $(PARTICLE_CREATION_DIR)/run_local.py

particle-run-aer:
	$(PYTHON) $(PARTICLE_CREATION_DIR)/run_aer.py

particle-analyze:
	$(PYTHON) $(PARTICLE_CREATION_DIR)/analyze.py

particle-creation: particle-benchmark particle-run-local particle-run-aer particle-analyze

particle-run-ibm:
	@if [ -z "$(BACKEND)" ]; then \
		printf '%s\n' 'BACKEND is required. Usage: make particle-run-ibm BACKEND=<backend-name>'; \
		exit 1; \
	fi
	$(PYTHON) $(PARTICLE_CREATION_DIR)/run_ibm.py --backend-name $(BACKEND)

particle-run-ibm-local:
	@if [ -z "$(LOCAL_TESTING_BACKEND)" ]; then \
		printf '%s\n' 'LOCAL_TESTING_BACKEND is required. Usage: make particle-run-ibm-local LOCAL_TESTING_BACKEND=<fake-backend-class>'; \
		exit 1; \
	fi
	$(PYTHON) $(PARTICLE_CREATION_DIR)/run_ibm.py --local-testing-backend $(LOCAL_TESTING_BACKEND)

gut-benchmark:
	$(PYTHON) $(GUT_TOY_GAUGE_DIR)/benchmark.py

gut-run-local:
	$(PYTHON) $(GUT_TOY_GAUGE_DIR)/run_local.py

gut-run-aer:
	$(PYTHON) $(GUT_TOY_GAUGE_DIR)/run_aer.py

gut-analyze:
	$(PYTHON) $(GUT_TOY_GAUGE_DIR)/analyze.py

gut-toy-gauge: gut-benchmark gut-run-local gut-run-aer gut-analyze

gut-run-ibm:
	@if [ -z "$(BACKEND)" ]; then \
		printf '%s\n' 'BACKEND is required. Usage: make gut-run-ibm BACKEND=<backend-name>'; \
		exit 1; \
	fi
	$(PYTHON) $(GUT_TOY_GAUGE_DIR)/run_ibm.py --backend-name $(BACKEND)

gut-run-ibm-local:
	@if [ -z "$(LOCAL_TESTING_BACKEND)" ]; then \
		printf '%s\n' 'LOCAL_TESTING_BACKEND is required. Usage: make gut-run-ibm-local LOCAL_TESTING_BACKEND=<fake-backend-class>'; \
		exit 1; \
	fi
	$(PYTHON) $(GUT_TOY_GAUGE_DIR)/run_ibm.py --local-testing-backend $(LOCAL_TESTING_BACKEND)

phase6-milestone-report:
	$(PYTHON) scripts/release/build_phase6_milestone_report.py

phase6-release-manifest:
	$(PYTHON) scripts/release/build_archival_release_manifest.py

phase6-release: phase6-milestone-report phase6-release-manifest

clean-cache:
	rm -rf .pytest_cache .hypothesis .mypy_cache .ruff_cache
	rm -f .coverage coverage.xml
	rm -rf htmlcov
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

clean-build:
	rm -rf build dist
	find src -maxdepth 2 -type d -name '*.egg-info' -prune -exec rm -rf {} +

clean: clean-cache clean-build
