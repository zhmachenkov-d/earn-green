"""Smoke tests for the Typer CLI scaffold and console-script entry."""

from __future__ import annotations

from importlib.metadata import entry_points

from typer.testing import CliRunner

from earngreen import __version__
from earngreen.surfaces.cli import app

runner = CliRunner()


def test_version_flag_prints_package_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_help_flag_exits_zero() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "EarnGreen" in result.stdout


def test_console_script_entry_points_to_cli_app() -> None:
    matches = [ep for ep in entry_points().select(group="console_scripts") if ep.name == "earngreen"]
    assert matches, "console script 'earngreen' missing from package metadata"
    assert matches[0].value == "earngreen.surfaces.cli:app"
