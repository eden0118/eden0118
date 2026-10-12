#!/usr/bin/env python3
"""Validate self-contained profile graphics and references in both previews."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from terminal_art import ascii_portrait
from preview import check_preview

ROOT = Path(__file__).resolve().parents[1]
NS = {'svg': 'http://www.w3.org/2000/svg'}
GENERATED = {f'assets/{name}-{theme}.svg' for name in ('banner', 'signals', 'roots') for theme in ('dark', 'light')}


def main():
    check_preview()
    reference_sets = []
    for page in ('README.md', 'preview.html'):
        content = (ROOT / page).read_text()
        references = set(re.findall(r'(?:src|srcset)="(?:\./)?(assets/[^\"]+)"', content))
        assert references == GENERATED, f'Unexpected artwork references in {page}: {references ^ GENERATED}'
        reference_sets.append(references)
    for path in (ROOT / 'assets').glob('*.svg'):
        root = ET.parse(path).getroot()
        assert path.stat().st_size < 250_000, f'Asset exceeds download budget: {path.name}'
        assert root.find('svg:title', NS) is not None, f'Missing title: {path.name}'
        if str(path.relative_to(ROOT)) in GENERATED:
            assert root.find('svg:desc', NS) is not None, f'Missing description: {path.name}'
        for element in ('image', 'script', 'foreignObject', 'animate', 'animateMotion'):
            assert not root.findall(f'.//svg:{element}', NS), f'Unexpected {element}: {path.name}'
        ids = [node.get('id') for node in root.iter() if node.get('id')]
        assert len(ids) == len(set(ids)), f'Duplicate identifiers: {path.name}'
    portrait = ascii_portrait()
    assert len(portrait) == 76 and all(len(line) == 120 and line.isascii() for line in portrait)
    print('Dark/light profile assets, accessibility labels and ASCII portrait validated')


if __name__ == '__main__':
    main()
