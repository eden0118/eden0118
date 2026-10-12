#!/usr/bin/env python3
"""Generate the local profile preview from README, or check for stale output."""
import argparse
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]


def render_preview(readme=None):
    if readme is None:
        readme = (ROOT / 'README.md').read_text()
    template = (ROOT / 'scripts/preview-template.html').read_text()
    return template.replace('{{README}}', MarkdownIt('commonmark', {'html': True}).render(readme))


def write_preview():
    (ROOT / 'preview.html').write_text(render_preview())


def check_preview():
    assert (ROOT / 'preview.html').read_text() == render_preview(), (
        'preview.html is out of sync with README.md. Run python scripts/preview.py'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the generated preview is stale')
    args = parser.parse_args()
    if args.check:
        check_preview()
        print('Preview matches README')
    else:
        write_preview()
        print('Generated preview.html from README.md')
