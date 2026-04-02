"""IBM Runtime execution for the reduced FLRW particle-creation toy model."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    repository_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository_root))
    sys.path.insert(0, str(repository_root / "src"))

from qclab.backends import (
    BackendRequest,
    IBMRuntimeEstimatorExecutor,
    instantiate_local_testing_backend,
    resolve_ibm_runtime_artifact_paths,
    write_ibm_runtime_artifacts,
)
from qclab.backends.base import ExecutionTier, validate_execution_progression

from experiments.particle_creation_flrw.benchmark import (
    comparison_records_for_result,
    compute_benchmark,
    write_benchmark_json,
)
from experiments.particle_creation_flrw.circuit import build_particle_creation_circuit
from experiments.particle_creation_flrw.common import (
    DEFAULT_CONFIG_PATH,
    default_backend_request_kwargs,
    load_experiment_definition,
)
from experiments.particle_creation_flrw.observables import build_observables


def run_ibm_hardware(
    *,
    config_path: str = str(DEFAULT_CONFIG_PATH),
    backend_name: str | None = None,
    instance: str | None = None,
    channel: str | None = None,
    mitigation_enabled: bool = False,
    resilience_level: int | None = None,
    local_testing_backend: str | None = None,
) -> dict[str, str]:
    """Execute the IBM Runtime path after exact-local and noisy-local validation."""

    experiment = load_experiment_definition(config_path)
    exact_validation_available = experiment.artifacts.exact_local_json.exists()
    noisy_validation_available = experiment.artifacts.noisy_local_json.exists()
    benchmark = compute_benchmark(experiment.parameters)
    write_benchmark_json(experiment, benchmark)
    validate_execution_progression(
        ExecutionTier.IBM_HARDWARE,
        benchmark_complete=True,
        exact_local_complete=exact_validation_available,
        noisy_local_complete=noisy_validation_available,
    )

    request_kwargs = default_backend_request_kwargs(experiment, ExecutionTier.IBM_HARDWARE)
    request_options = dict(request_kwargs["options"])
    mitigation_policy = dict(request_options.get("mitigation_policy", {}))
    if resilience_level is not None:
        mitigation_policy["resilience_level"] = resilience_level
    if mitigation_policy:
        request_options["mitigation_policy"] = mitigation_policy
    request_kwargs["options"] = request_options
    request_kwargs["mitigation_enabled"] = mitigation_enabled

    selected_backend_name = local_testing_backend or backend_name or request_kwargs["backend_name"]
    selection_policy = dict(request_options.get("selection_policy", {}))
    selection_strategy = str(selection_policy.get("strategy", "explicit"))
    if (
        local_testing_backend is None
        and selection_strategy == "explicit"
        and selected_backend_name == "ibm_backend_required"
    ):
        raise ValueError(
            "An IBM backend name must be supplied because the configuration leaves it unset."
        )
    request_kwargs["backend_name"] = selected_backend_name
    request = BackendRequest(**request_kwargs)

    service_kwargs = {}
    if instance is not None:
        service_kwargs["instance"] = instance
    if channel is not None:
        service_kwargs["channel"] = channel
    backend = None
    if local_testing_backend is not None:
        backend = instantiate_local_testing_backend(local_testing_backend)
    artifact_paths = resolve_ibm_runtime_artifact_paths(
        execution_json_path=experiment.artifacts.ibm_runtime_json,
        comparison_json_path=experiment.artifacts.ibm_runtime_comparisons_json,
        metadata_json_path=experiment.artifacts.ibm_runtime_metadata_json,
        report_markdown_path=experiment.artifacts.ibm_runtime_report_markdown,
        local_testing_mode=local_testing_backend is not None,
    )

    result = IBMRuntimeEstimatorExecutor().run(
        build_particle_creation_circuit(experiment.parameters),
        build_observables(experiment.parameters),
        request=request,
        service_kwargs=service_kwargs,
        backend=backend,
        transpile_for_backend=True,
    )
    comparison_records = comparison_records_for_result(
        result,
        benchmark,
        tier_label="IBM Runtime hardware",
    )
    artifact_paths = write_ibm_runtime_artifacts(
        experiment_name=experiment.configuration.experiment_name,
        scientific_question=experiment.configuration.scientific_question,
        result=result,
        comparison_records=comparison_records,
        benchmark_complete=True,
        exact_local_complete=exact_validation_available,
        noisy_local_complete=noisy_validation_available,
        execution_json_path=artifact_paths["execution_json_path"],
        comparison_json_path=artifact_paths["comparison_json_path"],
        metadata_json_path=artifact_paths["metadata_json_path"],
        report_markdown_path=artifact_paths["report_markdown_path"],
    )
    outputs = {
        "benchmark_json": str(experiment.artifacts.benchmark_json),
    }
    outputs.update({label: str(path) for label, path in artifact_paths.items()})
    return outputs


def main(argv: list[str] | None = None) -> int:
    """Run the IBM Runtime hardware workflow."""

    parser = argparse.ArgumentParser(
        description="Run the IBM Runtime reduced FLRW particle-creation workflow."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--backend-name", default=None)
    parser.add_argument("--instance", default=None)
    parser.add_argument("--channel", default=None)
    parser.add_argument(
        "--mitigation",
        action="store_true",
        help="Enable at least the default resilience policy for the IBM Runtime request.",
    )
    parser.add_argument(
        "--resilience-level",
        type=int,
        choices=(0, 1, 2),
        default=None,
        help="Override the configured IBM Runtime resilience level.",
    )
    parser.add_argument(
        "--local-testing-backend",
        default=None,
        help=(
            "Instantiate a fake backend from qiskit_ibm_runtime.fake_provider for "
            "credential-free IBM Runtime local testing mode."
        ),
    )
    args = parser.parse_args(argv)
    outputs = run_ibm_hardware(
        config_path=args.config,
        backend_name=args.backend_name,
        instance=args.instance,
        channel=args.channel,
        mitigation_enabled=args.mitigation,
        resilience_level=args.resilience_level,
        local_testing_backend=args.local_testing_backend,
    )
    for label, path in outputs.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
