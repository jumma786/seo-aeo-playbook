"""Scaffold a new project's ``seo-playbook.yml`` config file.

Bootstraps the exact config file ``cli/config.py`` auto-discovers
(``seo-playbook.yml`` / ``.seo-playbook.yml`` in the current directory):
``brand``, ``domain``, ``output_dir``, and ``default_similarity_threshold``.
Only fields explicitly provided are written; unset fields are left to
:class:`cli.config.Config`'s own defaults when later loaded. Refuses to
overwrite an existing config file unless explicitly told to, so re-running
init never silently destroys a project's existing settings.

Example:
    >>> from scripts.init import render_config_yaml
    >>> print(render_config_yaml(brand="Example Corp", domain="example.com"))
    brand: Example Corp
    domain: example.com
    <BLANKLINE>
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from cli.config import DEFAULT_CONFIG_FILENAMES

logger = logging.getLogger(__name__)


class InitError(RuntimeError):
    """Raised when project initialization cannot proceed safely."""


def render_config_yaml(
    *,
    brand: str | None = None,
    domain: str | None = None,
    output_dir: str | None = None,
    default_similarity_threshold: float | None = None,
) -> str:
    """Render a ``seo-playbook.yml`` config body from provided overrides.

    Args:
        brand: The site/brand name, used as a default title suffix.
        domain: The site's domain, used e.g. to default a sitemap URL.
        output_dir: Default output directory for generated files.
        default_similarity_threshold: Default keyword-clustering/mapping threshold.

    Returns:
        YAML content ending in a newline. Fields left as ``None`` are
        omitted entirely (not written as ``null``), so
        :class:`cli.config.Config`'s built-in defaults apply when loaded.
    """
    data: dict[str, object] = {}
    if brand is not None:
        data["brand"] = brand
    if domain is not None:
        data["domain"] = domain
    if output_dir is not None:
        data["output_dir"] = output_dir
    if default_similarity_threshold is not None:
        data["default_similarity_threshold"] = default_similarity_threshold

    if not data:
        return "{}\n"
    return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)


def init_project(
    directory: str | Path = ".",
    *,
    brand: str | None = None,
    domain: str | None = None,
    output_dir: str | None = None,
    default_similarity_threshold: float | None = None,
    force: bool = False,
    filename: str = "seo-playbook.yml",
) -> Path:
    """Write a starter config file into a project directory.

    Args:
        directory: The project root to write the config file into.
        brand: The site/brand name to write, if any.
        domain: The site's domain to write, if any.
        output_dir: Default output directory to write, if any.
        default_similarity_threshold: Default similarity threshold to write, if any.
        force: If False (the default), refuses to overwrite an existing
            config file at the target path.
        filename: The config filename to write; must be one of
            :data:`cli.config.DEFAULT_CONFIG_FILENAMES` so it's auto-discovered.

    Returns:
        The path of the written config file.

    Raises:
        InitError: If filename isn't a recognized config filename, or the
            target file already exists and force is False.
    """
    if filename not in DEFAULT_CONFIG_FILENAMES:
        raise InitError(f"filename must be one of {DEFAULT_CONFIG_FILENAMES}, got {filename!r}")

    target = Path(directory) / filename
    if target.exists() and not force:
        raise InitError(f"{target} already exists; pass --force (or force=True) to overwrite")

    content = render_config_yaml(
        brand=brand, domain=domain, output_dir=output_dir, default_similarity_threshold=default_similarity_threshold
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    logger.info("Wrote starter config to %s", target)
    return target


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m scripts.init [options] [directory]``."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Scaffold a new seo-aeo-playbook project config.")
    parser.add_argument("directory", nargs="?", default=".", help="Project directory to initialize (default: current directory)")
    parser.add_argument("--brand", help="Site/brand name")
    parser.add_argument("--domain", help="Site domain")
    parser.add_argument("--output-dir", help="Default output directory for generated files")
    parser.add_argument("--similarity-threshold", type=float, help="Default keyword clustering/mapping similarity threshold")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing config file")
    args = parser.parse_args(argv)

    try:
        path = init_project(
            args.directory,
            brand=args.brand,
            domain=args.domain,
            output_dir=args.output_dir,
            default_similarity_threshold=args.similarity_threshold,
            force=args.force,
        )
    except InitError as exc:
        logging.error("Init failed: %s", exc)
        return 1

    print(f"Wrote starter config to {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
