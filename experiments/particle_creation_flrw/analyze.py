"""Analysis for the reduced FLRW particle-creation toy model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

import matplotlib.pyplot as plt

from qclab.plotting import apply_publication_style
from qclab.observables import ObservableEvaluation
from qclab.utils.paths import repository_relative_path

from experiments.particle_creation_flrw.benchmark import (
    comparison_records_for_evaluations,
    compute_benchmark,
)
from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    load_experiment_definition,
)
from experiments.particle_creation_flrw.observables import build_observables


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _evaluation_map(execution_payload: dict) -> dict[str, float]:
    return {
        evaluation["observable_name"]: float(evaluation["value"])
        for evaluation in execution_payload["evaluations"]
    }


def _format_table_value(value: float | None) -> str:
    """Format a scalar value for markdown table output."""

    if value is None:
        return "n/a"
    return f"{value:.6f}"


def _write_observable_summary_table(
    *,
    benchmark_values: dict[str, float],
    exact_values: dict[str, float],
    noisy_values: dict[str, float],
    exact_absolute_errors: dict[str, float],
    noisy_absolute_errors: dict[str, float],
    output_path: Path,
    ibm_values: dict[str, float] | None = None,
    ibm_absolute_errors: dict[str, float] | None = None,
) -> Path:
    """Write a markdown summary table for benchmarked observables."""

    headers = [
        "Observable",
        "Benchmark",
        "Exact local",
        "Exact abs. error",
        "Noisy local",
        "Noisy abs. error",
    ]
    if ibm_values is not None:
        headers.extend(["IBM Runtime", "IBM abs. error"])

    lines = [
        "# Particle-Creation FLRW Observable Summary Table",
        "",
        "|" + "|".join(headers) + "|",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for observable_name, benchmark_value in benchmark_values.items():
        row = [
            observable_name,
            _format_table_value(benchmark_value),
            _format_table_value(exact_values.get(observable_name)),
            _format_table_value(exact_absolute_errors.get(observable_name)),
            _format_table_value(noisy_values.get(observable_name)),
            _format_table_value(noisy_absolute_errors.get(observable_name)),
        ]
        if ibm_values is not None:
            row.extend(
                [
                    _format_table_value(ibm_values.get(observable_name)),
                    _format_table_value(
                        None
                        if ibm_absolute_errors is None
                        else ibm_absolute_errors.get(observable_name)
                    ),
                ]
            )
        lines.append("|" + "|".join(row) + "|")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def _plot_observable_comparison(
    *,
    benchmark_values: dict[str, float],
    candidate_series: dict[str, dict[str, float]],
    output_path: Path,
) -> Path:
    """Plot grouped observable values across benchmark and execution tiers."""

    apply_publication_style()
    observable_names = list(benchmark_values)
    x_positions = list(range(len(observable_names)))
    series_labels = ["Benchmark", *candidate_series.keys()]
    bar_width = 0.8 / len(series_labels)

    figure, axis = plt.subplots(figsize=(9.2, 4.8))
    axis.bar(
        [position - 0.4 + 0.5 * bar_width for position in x_positions],
        [benchmark_values[name] for name in observable_names],
        width=bar_width,
        label="Benchmark",
    )
    for series_index, (series_label, values) in enumerate(candidate_series.items(), start=1):
        axis.bar(
            [
                position - 0.4 + (series_index + 0.5) * bar_width
                for position in x_positions
            ],
            [values[name] for name in observable_names],
            width=bar_width,
            label=series_label,
        )
    axis.set_xticks(x_positions, observable_names, rotation=15)
    axis.set_ylabel("Expectation value")
    axis.set_title("Reduced FLRW particle-creation observable comparison")
    axis.legend()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path)
    plt.close(figure)
    return output_path


def run_analysis(config_path: str = str(DEFAULT_CONFIG_PATH)) -> dict[str, str]:
    """Analyze benchmarked exact and noisy outputs for the default experiment."""

    experiment = load_experiment_definition(config_path)
    benchmark = compute_benchmark(experiment.parameters)
    benchmark_values = benchmark.expected_observable_values()

    exact_payload = _load_json(experiment.artifacts.exact_local_json)
    noisy_payload = _load_json(experiment.artifacts.noisy_local_json)
    series = {
        "Exact local": _evaluation_map(exact_payload),
        "Noisy local": _evaluation_map(noisy_payload),
    }
    ibm_payload = None
    if experiment.artifacts.ibm_runtime_json.exists():
        ibm_payload = _load_json(experiment.artifacts.ibm_runtime_json)
        series["IBM Runtime"] = _evaluation_map(ibm_payload)

    figure_path = _plot_observable_comparison(
        benchmark_values=benchmark_values,
        candidate_series=series,
        output_path=experiment.artifacts.comparison_figure,
    )

    observable_lookup = {
        observable.name: observable for observable in build_observables(experiment.parameters)
    }
    exact_evaluations = tuple(
        ObservableEvaluation(
            observable=observable_lookup[item["observable_name"]],
            value=float(item["value"]),
            uncertainty=float(item.get("uncertainty", 0.0)),
            shots=item.get("shots"),
            metadata={},
        )
        for item in exact_payload["evaluations"]
    )
    noisy_evaluations = tuple(
        ObservableEvaluation(
            observable=observable_lookup[item["observable_name"]],
            value=float(item["value"]),
            uncertainty=float(item.get("uncertainty", 0.0)),
            shots=item.get("shots"),
            metadata={},
        )
        for item in noisy_payload["evaluations"]
    )
    exact_comparisons = comparison_records_for_evaluations(
        exact_evaluations,
        benchmark,
        tier_label="Exact local",
    )
    noisy_comparisons = comparison_records_for_evaluations(
        noisy_evaluations,
        benchmark,
        tier_label="Noisy local Aer",
    )

    summary_payload = {
        "benchmark_values": benchmark_values,
        "exact_local_values": series["Exact local"],
        "noisy_local_values": series["Noisy local"],
        "exact_local_absolute_errors": {
            record.observable_name: record.absolute_error for record in exact_comparisons
        },
        "noisy_local_absolute_errors": {
            record.observable_name: record.absolute_error for record in noisy_comparisons
        },
        "comparison_figure": repository_relative_path(figure_path),
    }
    if ibm_payload is not None:
        summary_payload["ibm_runtime_values"] = series["IBM Runtime"]
        summary_payload["ibm_runtime_json"] = repository_relative_path(
            experiment.artifacts.ibm_runtime_json
        )
        summary_payload["ibm_runtime_comparisons_json"] = repository_relative_path(
            experiment.artifacts.ibm_runtime_comparisons_json
        )
        ibm_evaluations = tuple(
            ObservableEvaluation(
                observable=observable_lookup[item["observable_name"]],
                value=float(item["value"]),
                uncertainty=float(item.get("uncertainty", 0.0)),
                shots=item.get("shots"),
                metadata={},
            )
            for item in ibm_payload["evaluations"]
        )
        ibm_comparisons = comparison_records_for_evaluations(
            ibm_evaluations,
            benchmark,
            tier_label="IBM Runtime",
        )
        summary_payload["ibm_runtime_absolute_errors"] = {
            record.observable_name: record.absolute_error for record in ibm_comparisons
        }
        if experiment.artifacts.ibm_runtime_metadata_json.exists():
            summary_payload["ibm_runtime_metadata_json"] = repository_relative_path(
                experiment.artifacts.ibm_runtime_metadata_json
            )
        if experiment.artifacts.ibm_runtime_report_markdown.exists():
            summary_payload["ibm_runtime_report_markdown"] = repository_relative_path(
                experiment.artifacts.ibm_runtime_report_markdown
            )
    else:
        ibm_comparisons = None

    summary_table_path = _write_observable_summary_table(
        benchmark_values=benchmark_values,
        exact_values=series["Exact local"],
        noisy_values=series["Noisy local"],
        exact_absolute_errors=summary_payload["exact_local_absolute_errors"],
        noisy_absolute_errors=summary_payload["noisy_local_absolute_errors"],
        ibm_values=None if ibm_payload is None else series["IBM Runtime"],
        ibm_absolute_errors=(
            None
            if ibm_comparisons is None
            else summary_payload["ibm_runtime_absolute_errors"]
        ),
        output_path=experiment.artifacts.observable_summary_table_markdown,
    )
    summary_payload["observable_summary_table_markdown"] = repository_relative_path(
        summary_table_path
    )

    experiment.artifacts.analysis_summary_json.parent.mkdir(parents=True, exist_ok=True)
    experiment.artifacts.analysis_summary_json.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report_lines = [
        "# Particle-Creation FLRW Analysis Report",
        "",
        "## Benchmark",
        "",
        (
            "- Single-mode particle number expectation: "
            f"{benchmark.single_mode_particle_number_expectation:.6f}"
        ),
        (
            "- Total particle number expectation: "
            f"{benchmark.total_particle_number_expectation:.6f}"
        ),
        (
            "- Pairing correlator expectation: "
            f"{benchmark.pairing_correlator_expectation:.6f}"
        ),
        "",
        "## Execution Comparison",
        "",
        (
            "- Exact local total particle number: "
            f"{series['Exact local']['total_particle_number_expectation']:.6f}"
        ),
        (
            "- Noisy local total particle number: "
            f"{series['Noisy local']['total_particle_number_expectation']:.6f}"
        ),
        (
            "- Exact local absolute total-particle error: "
            f"{summary_payload['exact_local_absolute_errors']['total_particle_number_expectation']:.6e}"
        ),
        (
            "- Noisy local absolute total-particle error: "
            f"{summary_payload['noisy_local_absolute_errors']['total_particle_number_expectation']:.6e}"
        ),
        "",
        "## Interpretation",
        "",
        (
            "The exact local workflow reproduces the exact discrete benchmark of "
            "the retained two-mode FLRW particle-creation toy model."
        ),
        (
            "The noisy local workflow preserves a nonzero particle-number signal "
            "and the sign of the pairing correlator under the explicit Aer noise "
            "model, but it is not interpreted as evidence for a full continuum "
            "curved-spacetime field theory."
        ),
    ]
    if ibm_payload is not None:
        report_lines.extend(
            [
                (
                    "The IBM Runtime tier, when present, remains subordinate to the "
                    "benchmark, exact-local, and noisy-local tiers and must be read "
                    "through the associated hardware report and metadata capture."
                ),
                "",
                (
                    "IBM execution JSON: "
                    f"`{repository_relative_path(experiment.artifacts.ibm_runtime_json)}`"
                ),
            ]
        )
        if experiment.artifacts.ibm_runtime_metadata_json.exists():
            report_lines.append(
                (
                    "IBM metadata JSON: "
                    f"`{repository_relative_path(experiment.artifacts.ibm_runtime_metadata_json)}`"
                )
            )
        if experiment.artifacts.ibm_runtime_report_markdown.exists():
            report_lines.append(
                (
                    "IBM hardware report: "
                    f"`{repository_relative_path(experiment.artifacts.ibm_runtime_report_markdown)}`"
                )
            )
    report_lines.extend(
        [
            "",
            f"Table: `{repository_relative_path(summary_table_path)}`",
            "",
            f"Figure: `{repository_relative_path(figure_path)}`",
        ]
    )
    experiment.artifacts.analysis_report_markdown.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )
    outputs = {
        "analysis_summary_json": repository_relative_path(
            experiment.artifacts.analysis_summary_json
        ),
        "analysis_report_markdown": repository_relative_path(
            experiment.artifacts.analysis_report_markdown
        ),
        "observable_summary_table_markdown": repository_relative_path(summary_table_path),
        "comparison_figure": repository_relative_path(figure_path),
    }
    if ibm_payload is not None:
        outputs["ibm_runtime_json"] = repository_relative_path(
            experiment.artifacts.ibm_runtime_json
        )
        outputs["ibm_runtime_comparisons_json"] = repository_relative_path(
            experiment.artifacts.ibm_runtime_comparisons_json
        )
        if experiment.artifacts.ibm_runtime_metadata_json.exists():
            outputs["ibm_runtime_metadata_json"] = repository_relative_path(
                experiment.artifacts.ibm_runtime_metadata_json
            )
        if experiment.artifacts.ibm_runtime_report_markdown.exists():
            outputs["ibm_runtime_report_markdown"] = repository_relative_path(
                experiment.artifacts.ibm_runtime_report_markdown
            )
    return outputs


def main(argv: list[str] | None = None) -> int:
    """Run the experiment analysis workflow."""

    parser = argparse.ArgumentParser(
        description="Analyze the reduced FLRW particle-creation benchmarked outputs."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    outputs = run_analysis(args.config)
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
