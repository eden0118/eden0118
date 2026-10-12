#!/usr/bin/env python3
"""Validate graphic-only assets and the editable Markdown layout."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'svg': 'http://www.w3.org/2000/svg'}
EXPECTED = {'profile-avatar', 'practice-planning', 'practice-experience', 'practice-collaboration', 'practice-frontend'}


def main():
    referenced = set()
    for page in ('README.md', 'preview.html'):
        for name in re.findall(r'(?:src|srcset)="(?:\./)?(assets/[^\"]+)"', (ROOT / page).read_text()):
            path = ROOT / name
            assert path.is_file(), f'Missing image: {name}'
            root = ET.parse(path).getroot()
            assert path.stat().st_size < 100_000, 'Asset exceeds download budget'
            assert not root.findall('.//svg:text', NS), 'Visible profile text belongs in README.md'
            for element in ('image', 'script', 'animate', 'animateMotion'):
                assert not root.findall(f'.//svg:{element}', NS), f'Unexpected {element} element'
            assert root.find('svg:title', NS) is not None
            ids = [node.get('id') for node in root.iter() if node.get('id')]
            assert len(ids) == len(set(ids)), 'Duplicate SVG identifiers'
            referenced.add(name)
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'assets').glob('*.svg')}
    assert actual == referenced, f'Unused artwork: {actual - referenced}'
    assert {Path(name).stem for name in referenced} == EXPECTED
    print('Five graphic-only SVGs checked; all visible profile text is editable in README.md')


if __name__ == '__main__':
    main()
