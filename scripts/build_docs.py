#!/usr/bin/env python3
"""Build the docs with Great Docs and mirror the static site into the committed docs/ folder.

The great-docs/ build directory is ephemeral (regenerated every build and gitignored);
docs/ is the committed copy that the web server serves at /docs/chameleon-flask via git pull.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPTS.parent  # pyproject.toml + great-docs.yml live here
SITE = REPO_ROOT / 'great-docs' / '_site'
DEST = REPO_ROOT / 'docs'

# Files that must exist in every build. Great Docs reports success even when it silently
# skips some of them (for example llms-full.txt when it cannot import the package), and the
# user guide only appears when great-docs finds user_guide/ at the repo root.
REQUIRED_OUTPUTS = (
    'llms.txt',
    'llms-full.txt',
    'skill.md',
    '.well-known/agent-skills/index.json',
    'user-guide/index.html',
    'user-guide/getting-started.html',
    'user-guide/troubleshooting.html',
)
USER_GUIDE_MARKER = 'This is the User Guide documentation for the package.'


def main() -> int:
    great_docs = Path(sys.executable).with_name('great-docs')
    cmd = [str(great_docs) if great_docs.exists() else 'great-docs', 'build']
    if subprocess.run(cmd, cwd=REPO_ROOT).returncode != 0:
        return 1

    if not SITE.is_dir():
        print(f'Build output missing: {SITE}', file=sys.stderr)
        return 1

    missing = [name for name in REQUIRED_OUTPUTS if not (SITE / name).is_file()]
    if missing:
        print(f'Build output incomplete, missing: {", ".join(missing)}', file=sys.stderr)
        return 1
    if USER_GUIDE_MARKER not in (SITE / 'llms-full.txt').read_text(encoding='utf-8'):
        print(f'llms-full.txt has no user guide section ({USER_GUIDE_MARKER!r} missing)', file=sys.stderr)
        return 1

    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)

    file_count = sum(1 for p in DEST.rglob('*') if p.is_file())
    print(f'Mirrored {SITE} -> {DEST} ({file_count} files)')

    # Fix up Great Docs output that is wrong at build time (e.g. the navbar version badge,
    # which otherwise shows the previous GitHub release). See postprocess_site.py.
    return subprocess.run([sys.executable, str(_SCRIPTS / 'postprocess_site.py')], cwd=REPO_ROOT).returncode


if __name__ == '__main__':
    raise SystemExit(main())
