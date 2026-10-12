"""Typer CLI surface — scaffold entrypoint only."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Annotated, Optional

import typer

app = typer.Typer(
    name="earngreen",
    help="EarnGreen — verify that green tests were earned.",
    no_args_is_help=True,
    add_completion=False,
)


def _package_version() -> str:
    try:
        return version("earngreen")
    except PackageNotFoundError:
        from earngreen import __version__

        return __version__


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(_package_version())
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            help="Show package version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """EarnGreen CLI (scaffold)."""
    _ = version
