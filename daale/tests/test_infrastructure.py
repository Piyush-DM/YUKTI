"""Tests for DAALE prototype infrastructure utilities."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import logging
import unittest

from daale.config import configured_dependencies, load_config, load_env_file
from daale.doctor import (
    all_checks_passed,
    check_api_keys,
    check_python_version,
    check_repository_structure,
    check_virtual_environment,
)
from daale.logging import LOGGER_NAME, initialize_logging
from daale.reports import build_report_paths, prepare_report_directory


class ConfigLoaderTests(unittest.TestCase):
    """Configuration loader checks."""

    def test_load_env_file_ignores_missing_file(self) -> None:
        """A missing `.env` file should produce an empty mapping."""
        with TemporaryDirectory() as directory:
            env = load_env_file(Path(directory) / ".env")

        self.assertEqual(env, {})

    def test_load_config_reads_env_and_pyproject(self) -> None:
        """The loader should read `.env` and doctor settings from TOML."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("EXAMPLE_API_KEY=value\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "\n".join(
                    (
                        "[project]",
                        'name = "example"',
                        'requires-python = ">=3.12"',
                        'dependencies = ["httpx"]',
                        "",
                        "[dependency-groups]",
                        'dev = ["pytest"]',
                        "",
                        "[tool.daale.doctor]",
                        'reports_dir = "reports"',
                        'required_api_keys = ["EXAMPLE_API_KEY"]',
                        'required_paths = ["pyproject.toml"]',
                    )
                ),
                encoding="utf-8",
            )

            config = load_config(root)

        self.assertEqual(config.env["EXAMPLE_API_KEY"], "value")
        self.assertEqual(config.doctor.required_api_keys, ("EXAMPLE_API_KEY",))
        self.assertEqual(config.doctor.reports_dir, Path("reports"))
        self.assertEqual(configured_dependencies(config), ("httpx", "pytest"))


class ReportUtilityTests(unittest.TestCase):
    """Report path utility checks."""

    def test_build_report_paths_does_not_create_files(self) -> None:
        """Path construction should not generate report files."""
        with TemporaryDirectory() as directory:
            paths = build_report_paths(Path(directory) / "reports", date(2026, 7, 10))

            self.assertEqual(paths.date_directory.name, "2026-07-10")
            self.assertFalse(paths.report_markdown.exists())
            self.assertFalse(paths.metadata_json.exists())

    def test_prepare_report_directory_creates_only_directories(self) -> None:
        """Preparing a report directory should not create report contents."""
        with TemporaryDirectory() as directory:
            paths = prepare_report_directory(
                Path(directory) / "reports", date(2026, 7, 10)
            )

            self.assertTrue(paths.root.exists())
            self.assertTrue(paths.date_directory.exists())
            self.assertFalse(paths.report_markdown.exists())
            self.assertFalse(paths.metadata_json.exists())


class LoggingUtilityTests(unittest.TestCase):
    """Logging initialization checks."""

    def test_initialize_logging_returns_package_logger(self) -> None:
        """Logging setup should configure the package logger only."""
        logger = initialize_logging(logging.DEBUG)

        self.assertEqual(logger.name, LOGGER_NAME)
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertFalse(logger.propagate)
        self.assertTrue(logger.handlers)


class DoctorChecksTests(unittest.TestCase):
    """Doctor check behavior."""

    def test_check_python_version_uses_pyproject_requirement(self) -> None:
        """Python version checks should follow `requires-python`."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                "\n".join(
                    (
                        "[project]",
                        'name = "example"',
                        'requires-python = ">=3.12"',
                        "",
                        "[tool.daale.doctor]",
                    )
                ),
                encoding="utf-8",
            )
            config = load_config(root)

        self.assertTrue(check_python_version(config, (3, 12, 0)).passed)
        self.assertFalse(check_python_version(config, (3, 11, 9)).passed)

    def test_check_virtual_environment_can_be_supplied(self) -> None:
        """Virtual environment checks should be testable without shell state."""
        self.assertTrue(check_virtual_environment(True).passed)
        self.assertFalse(check_virtual_environment(False).passed)

    def test_check_api_keys_uses_configured_names_only(self) -> None:
        """API key checks should not infer provider-specific names."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("EXAMPLE_API_KEY=value\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "\n".join(
                    (
                        "[project]",
                        'name = "example"',
                        'requires-python = ">=3.12"',
                        "",
                        "[tool.daale.doctor]",
                        'required_api_keys = ["EXAMPLE_API_KEY"]',
                    )
                ),
                encoding="utf-8",
            )
            config = load_config(root)

        self.assertTrue(check_api_keys(config, {}).passed)

    def test_check_repository_structure_reports_missing_paths(self) -> None:
        """Repository structure checks should use configured paths."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                "\n".join(
                    (
                        "[project]",
                        'name = "example"',
                        'requires-python = ">=3.12"',
                        "",
                        "[tool.daale.doctor]",
                        'required_paths = ["missing"]',
                    )
                ),
                encoding="utf-8",
            )
            config = load_config(root)

        result = check_repository_structure(config)

        self.assertFalse(result.passed)
        self.assertIn("missing", result.detail)

    def test_all_checks_passed_detects_failure(self) -> None:
        """Aggregate status should fail if any check failed."""
        passing = check_virtual_environment(True)
        failing = check_virtual_environment(False)

        self.assertTrue(all_checks_passed((passing,)))
        self.assertFalse(all_checks_passed((passing, failing)))


if __name__ == "__main__":
    unittest.main()
