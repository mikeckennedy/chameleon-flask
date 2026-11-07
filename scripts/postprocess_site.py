#!/usr/bin/env python3
"""Post-process the mirrored docs/ site after a Great Docs build.

Run by build_docs.py after mirroring great-docs/_site -> docs/. Each fix is narrow and
idempotent, and the replacement count is printed so a silent no-op is visible when a
future Great Docs release changes its output markup.

Fixes:
1. The navbar version badge comes from the latest GitHub Release at build time, so docs
   built before that release is published (the normal order: build docs, commit, tag,
   release) show the previous version. The badge is rewritten to the pyproject.toml
   version. Its "Released" date comes from, in order: the GitHub release Great Docs
   fetched (when its version matches), the git tag for that version, or nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
PACKAGE_META = ROOT / 'great-docs' / '_package_meta.json'
_VERSION_BADGE = re.compile(r'<span class="version-badge"[^>]*>[^<]*</span>')


def project_version() -> str:
    return tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']


def release_date(version: str) -> str | None:
    """YYYY-MM-DD for `version`, or None when it has not been released or tagged yet."""
    if PACKAGE_META.is_file():
        meta = json.loads(PACKAGE_META.read_text(encoding='utf-8'))
        if meta.get('version') == version and meta.get('published_at'):
            return meta['published_at'][:10]

    tag = subprocess.run(
        ['git', 'log', '-1', '--format=%cs', f'refs/tags/v{version}'],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if tag.returncode == 0 and tag.stdout.strip():
        return tag.stdout.strip()
    return None


def version_badge() -> str:
    """Badge HTML for the pyproject.toml version."""
    version = project_version()
    date = release_date(version)
    if date is None:
        print(
            f'[postprocess_site] WARNING: v{version} has no GitHub release or git tag yet; badge has no date',
            file=sys.stderr,
        )
        return f'<span class="version-badge">v{version}</span>'
    return f'<span class="version-badge" title="Released {date}">v{version}</span>'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--site', type=Path, default=DOCS, help='built site directory (default: docs/)')
    args = parser.parse_args(argv)
    site: Path = args.site

    if not site.is_dir():
        print(f'site directory missing: {site}', file=sys.stderr)
        return 1

    badge = version_badge()
    pages = 0
    badges = 0
    for page in sorted(site.rglob('*.html')):
        text = page.read_text(encoding='utf-8')
        new_text, n = _VERSION_BADGE.subn(badge, text)
        pages += 1
        badges += n
        if new_text != text:
            page.write_text(new_text, encoding='utf-8')

    print(f'[postprocess_site] version badges ({badge}): {badges} across {pages} pages')
    if badges == 0:
        print(
            '[postprocess_site] WARNING: no version badge found; Great Docs may have changed its markup '
            '(or the repo has no GitHub releases, in which case no badge is emitted)',
            file=sys.stderr,
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
