"""Configuration loading for DAALE prototype infrastructure.

The loader reads `.env` and `pyproject.toml` only. It does not interpret
business behavior or initialize runtime components.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import tomllib

from dotenv import dotenv_values


@dataclass(frozen=True)
class DoctorConfig:
    """Doctor-specific configuration sourced from `pyproject.toml`."""

    reports_dir: Path
    required_api_keys: tuple[str, ...]
    required_paths: tuple[Path, ...]


@dataclass(frozen=True)
class LoadedConfig:
    """Configuration values loaded from the repository root."""

    root: Path
    env_path: Path
    pyproject_path: Path
    env: Mapping[str, str]
    pyproject: Mapping[str, Any]
    doctor: DoctorConfig


def load_env_file(path: Path) -> dict[str, str]:
    """Load `.env` values without mutating `os.environ`."""
    if not path.exists():
        return {}

    raw_values = dotenv_values(path)
    return {key: value for key, value in raw_values.items() if value is not None}


def load_pyproject(path: Path) -> dict[str, Any]:
    """Load and parse `pyproject.toml`."""
    with path.open("rb") as handle:
        data: dict[str, Any] = tomllib.load(handle)
    return data


def load_config(root: Path | None = None) -> LoadedConfig:
    """Load DAALE environment and project configuration."""
    resolved_root = (root or Path.cwd()).resolve()
    env_path = resolved_root / ".env"
    pyproject_path = resolved_root / "pyproject.toml"
    pyproject = load_pyproject(pyproject_path)

    return LoadedConfig(
        root=resolved_root,
        env_path=env_path,
        pyproject_path=pyproject_path,
        env=load_env_file(env_path),
        pyproject=pyproject,
        doctor=_load_doctor_config(pyproject),
    )


def configured_dependencies(config: LoadedConfig) -> tuple[str, ...]:
    """Return project and development dependencies listed in `pyproject.toml`."""
    project_dependencies = config.pyproject.get("project", {}).get("dependencies", [])
    dependency_groups = config.pyproject.get("dependency-groups", {})
    dev_dependencies = dependency_groups.get("dev", [])

    return tuple(
        dependency
        for dependency in (*project_dependencies, *dev_dependencies)
        if isinstance(dependency, str)
    )


def _load_doctor_config(pyproject: Mapping[str, Any]) -> DoctorConfig:
    tool_section = pyproject.get("tool", {})
    daale_section = (
        tool_section.get("daale", {}) if isinstance(tool_section, dict) else {}
    )
    doctor_section = (
        daale_section.get("doctor", {}) if isinstance(daale_section, dict) else {}
    )

    reports_dir = _string_value(doctor_section, "reports_dir", "reports")
    required_api_keys = _string_tuple(doctor_section, "required_api_keys")
    required_paths = _path_tuple(
        doctor_section,
        "required_paths",
        (
            "daale",
            "daale/tests",
            "pyproject.toml",
            "requirements-dev.txt",
        ),
    )

    return DoctorConfig(
        reports_dir=Path(reports_dir),
        required_api_keys=required_api_keys,
        required_paths=required_paths,
    )


def _string_value(values: Mapping[str, Any], key: str, default: str) -> str:
    value = values.get(key, default)
    return value if isinstance(value, str) else default


def _string_tuple(values: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = values.get(key, [])
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _path_tuple(
    values: Mapping[str, Any], key: str, default: tuple[str, ...]
) -> tuple[Path, ...]:
    value = values.get(key, list(default))
    if not isinstance(value, list):
        value = list(default)
    return tuple(Path(item) for item in value if isinstance(item, str))
