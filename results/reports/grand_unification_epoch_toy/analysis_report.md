# Grand-Unification-Epoch Toy Analysis Report

## Benchmark

- Ground-state energy: -0.820472
- Order-parameter expectation: 0.894192
- Domain-wall density: 0.029822
- Transverse-coherence expectation: 0.283399

## Execution Comparison

- Exact local order-parameter value: 0.894192
- Noisy local order-parameter value: 0.867366
- Exact local domain-wall density: 0.029822
- Noisy local domain-wall density: 0.057610

## Interpretation

The exact local workflow reproduces the direct diagonalization benchmark for the reduced two-site Z2 toy model.
The noisy local workflow should be read as a degradation study for declared observables, not as evidence of literal Grand-Unification-Epoch structure.

The IBM Runtime tier, when present, remains subordinate to the benchmark, exact-local, and noisy-local tiers and must be read through the associated hardware report and metadata capture.

IBM execution JSON: `data/processed/grand_unification_epoch_toy/ibm_runtime.json`
IBM metadata JSON: `data/raw/grand_unification_epoch_toy/ibm_runtime_metadata.json`
IBM hardware report: `results/reports/grand_unification_epoch_toy/ibm_runtime_report.md`

Table: `results/tables/grand_unification_epoch_toy/observable_summary.md`

Figure: `results/figures/grand_unification_epoch_toy/observable_comparison.png`
