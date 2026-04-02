"""Repository-aware path-formatting helpers."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_repository_root(repository_root: str | Path | None = None) -> Path:
    """Return the resolved repository root used for path normalization."""

    if repository_root is None:
        return REPO_ROOT
    return Path(repository_root).expanduser().resolve()


def repository_relative_path(
    path: str | Path,
    *,
    repository_root: str | Path | None = None,
) -> str:
    """Return a repository-relative POSIX path when the target is inside the repo."""

    root = resolve_repository_root(repository_root)
    candidate = Path(path).expanduser()
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return str(resolved)
