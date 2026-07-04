"""Entry point for the ``seo-playbook`` console script (declared in pyproject.toml)."""

from __future__ import annotations

from cli.commands import cli

if __name__ == "__main__":  # pragma: no cover
    cli()
