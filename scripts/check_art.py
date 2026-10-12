#!/usr/bin/env python3
"""Validate the self-contained dossier, startup animation, and references."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'svg': 'http://www.w3.org/2000/svg'}


def main():
    path = ROOT / 'assets/profile-card.svg'
    content = path.read_text()
    root = ET.fromstring(content)
    assert path.stat().st_size < 220_000, 'Artwork exceeds the download budget'
    assert len(list(root.iter())) < 200, 'Too many rendering elements'
    assert not root.findall('.//svg:image', NS), 'External or raster image dependency'
    assert not root.findall('.//svg:script', NS), 'JavaScript is not supported in image embeds'
    for node in root.iter():
        assert not any(key.split('}')[-1].startswith('on') for key in node.attrib), 'Event handler returned'
    assert root.find('svg:title', NS) is not None and root.find('svg:desc', NS) is not None
    assert root.find('.//svg:g[@id="portrait"]', NS) is not None
    stages = root.findall('.//svg:g[@data-stage]', NS)
    assert [g.get('data-stage') for g in stages] == ['structure', 'journey', 'alignment', 'delivery']
    animations = root.findall('.//svg:animate', NS)
    assert len(animations) == 1, 'Only the startup pulse should animate'
    animation = animations[0]
    assert animation.get('repeatCount') == '1' and animation.get('dur') == '0.8s'
    assert animation.get('values').split(';')[-1] == '0', 'Startup overlay must end invisible'
    assert 'prefers-reduced-motion' in content
    ids = [node.get('id') for node in root.iter() if node.get('id')]
    assert len(ids) == len(set(ids)), 'Duplicate SVG identifiers'
    referenced = set()
    for page in ('README.md', 'preview.html'):
        for name in re.findall(r'(?:src|srcset)="(?:\./)?(assets/[^\"]+)"', (ROOT / page).read_text()):
            assert (ROOT / name).is_file(), f'Missing image: {name}'
            ET.parse(ROOT / name)
            referenced.add(name)
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'assets').glob('*')}
    assert actual == referenced, f'Unused artwork: {actual - referenced}'
    assert len(referenced) == 1, 'The dossier should be one image'
    print(f'Profile dossier checked: {path.stat().st_size // 1024} KB, four practices, one-shot startup, no external resources')


if __name__ == '__main__':
    main()
