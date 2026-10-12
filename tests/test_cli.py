"""Smoke tests for the Typer CLI scaffold and console-script entry."""

from __future__ import annotations

from importlib.metadata import entry_points

from earngreen import __version__
from earngreen.surfaces.cli import app
from typer.testing import CliRunner

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
    eps = entry_points()
    selected = (
        eps.select(group="console_scripts")
        if hasattr(eps, "select")
        else eps.get("console_scripts", [])
    )
    matches = [ep for ep in selected if ep.name == "earngreen"]
    assert matches, "console script 'earngreen' missing from package metadata"
    assert matches[0].value == "earngreen.surfaces.cli:app"
