"""Environment verification for DAALE prototype infrastructure."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Mapping, Sequence
import os
import sys

from daale.config import LoadedConfig, configured_dependencies, load_config
from daale.reports import verify_reports_root_writable


@dataclass(frozen=True)
class CheckResult:
    """Result of a single doctor check."""

    name: str
    passed: bool
    detail: str


def run_doctor(
    root: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> tuple[CheckResult, ...]:
    """Run all configured environment checks."""
    config = load_config(root)
    environment = environ or os.environ

    return (
        check_python_version(config),
        check_virtual_environment(),
        check_installed_dependencies(config),
        check_api_keys(config, environment),
        check_repository_structure(config),
        check_reports_directory(config),
    )


def check_python_version(
    config: LoadedConfig,
    version_info: tuple[int, int, int] | None = None,
) -> CheckResult:
    """Verify that the active Python version satisfies `requires-python`."""
    required = _minimum_python_version(config)
    current = version_info or (
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    passed = current >= required
    detail = (
        f"Python {current[0]}.{current[1]}.{current[2]} >= {required[0]}.{required[1]}"
    )
    return CheckResult("Python version", passed, detail)


def check_virtual_environment(is_virtual: bool | None = None) -> CheckResult:
    """Verify that the process is running inside a Python virtual environment."""
    active = is_virtual if is_virtual is not None else sys.prefix != sys.base_prefix
    detail = "Virtual environment active" if active else "Virtual environment inactive"
    return CheckResult("Virtual environment", active, detail)


def check_installed_dependencies(config: LoadedConfig) -> CheckResult:
    """Verify that configured Python dependencies are installed."""
    missing: list[str] = []
    for dependency in configured_dependencies(config):
        package_name = _package_name(dependency)
        try:
            metadata.version(package_name)
        except metadata.PackageNotFoundError:
            missing.append(package_name)

    if missing:
        return CheckResult(
            "Installed dependencies",
            False,
            f"Missing dependencies: {', '.join(sorted(missing))}",
        )

    return CheckResult(
        "Installed dependencies", True, "All configured dependencies found"
    )


def check_api_keys(
    config: LoadedConfig,
    environ: Mapping[str, str],
) -> CheckResult:
    """Verify that configured API key names are present.

    Key values are not validated beyond presence.
    """
    required_keys = config.doctor.required_api_keys
    if not required_keys:
        return CheckResult("API keys", True, "No API keys configured as required")

    available_keys = set(environ) | set(config.env)
    missing = [key for key in required_keys if key not in available_keys]
    if missing:
        return CheckResult("API keys", False, f"Missing API keys: {', '.join(missing)}")

    return CheckResult("API keys", True, "Configured API keys are present")


def check_repository_structure(config: LoadedConfig) -> CheckResult:
    """Verify that configured repository paths exist."""
    missing = [
        str(path)
        for path in config.doctor.required_paths
        if not (config.root / path).exists()
    ]
    if missing:
        return CheckResult(
            "Repository structure",
            False,
            f"Missing paths: {', '.join(missing)}",
        )

    return CheckResult(
        "Repository structure", True, "Configured repository paths exist"
    )


def check_reports_directory(config: LoadedConfig) -> CheckResult:
    """Verify that the reports directory is writable."""
    reports_root = config.root / config.doctor.reports_dir
    passed, detail = verify_reports_root_writable(reports_root)
    return CheckResult("Reports directory", passed, detail)


def all_checks_passed(results: Sequence[CheckResult]) -> bool:
    """Return whether all doctor checks passed."""
    return all(result.passed for result in results)


def _minimum_python_version(config: LoadedConfig) -> tuple[int, int, int]:
    project = config.pyproject.get("project", {})
    requires_python = project.get("requires-python", ">=3.12")
    if not isinstance(requires_python, str):
        return (3, 12, 0)

    prefix = ">="
    if not requires_python.startswith(prefix):
        return (3, 12, 0)

    version_text = requires_python.removeprefix(prefix).split(",")[0].strip()
    parts = version_text.split(".")
    major = _int_part(parts, 0)
    minor = _int_part(parts, 1)
    patch = _int_part(parts, 2)
    return major, minor, patch


def _int_part(parts: list[str], index: int) -> int:
    if index >= len(parts):
        return 0
    return int("".join(character for character in parts[index] if character.isdigit()))


def _package_name(requirement: str) -> str:
    delimiters = ("<", ">", "=", "!", "~", "[", ";")
    positions = [
        requirement.find(delimiter)
        for delimiter in delimiters
        if requirement.find(delimiter) != -1
    ]
    end = min(positions) if positions else len(requirement)
    return requirement[:end].strip()
