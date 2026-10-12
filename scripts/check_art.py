#!/usr/bin/env python3
"""Check the ASCII carousel, connected workflow, and README references."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'svg': 'http://www.w3.org/2000/svg'}
SCENES = ['design', 'need-sleep', 'working', 'drink']


def check_cover(path):
    content = path.read_text()
    root = ET.fromstring(content)
    assert path.stat().st_size < 220_000, f'{path.name}: exceeds the download budget'
    assert len(list(root.iter())) < 950, f'{path.name}: too many live rendering elements'
    assert not root.findall('.//svg:image', NS), 'Frame-swapping raster animation returned'
    scenes = root.findall('.//svg:g[@data-scene]', NS)
    assert [scene.attrib['data-scene'] for scene in scenes] == SCENES
    animations = root.findall('.//svg:animate', NS)
    assert animations
    for animation in animations:
        assert animation.attrib['calcMode'] == 'linear', 'Motion must be continuous'
        assert animation.attrib['dur'] == '28s' and animation.attrib['repeatCount'] == 'indefinite'
        times = [float(time) for time in animation.attrib['keyTimes'].split(';')]
        assert times[0] == 0 and times[-1] == 1
        assert all(a < b for a, b in zip(times, times[1:])), 'Invalid interpolation timeline'
        assert len(times) == len(animation.attrib['values'].split(';'))
    clips = root.findall('.//svg:clipPath', NS)
    assert not clips, 'The character carousel should crossfade without scanning masks'
    assert not root.findall('.//svg:use[@class="portrait-noise"]', NS), 'Character noise returned'
    assert 'prefers-reduced-motion' in content and 'portrait-first' in content
    print(f'{path.name}: {path.stat().st_size // 1024} KB, continuous four-scene SVG loop')


def check_workflow(path):
    content = path.read_text()
    root = ET.fromstring(content)
    expected = ['structure', 'journey', 'alignment', 'delivery']
    assert [g.get('data-stage') for g in root.findall('.//svg:g[@data-stage]', NS)] == expected
    assert [g.get('data-active') for g in root.findall('.//svg:g[@data-active]', NS)] == expected
    assert not root.findall('.//svg:animateMotion', NS), 'Independent traveling dots returned'
    assert not root.findall('.//svg:animateTransform', NS), 'Independent sliding shapes returned'
    assert 'prefers-reduced-motion' in content
    animations = root.findall('.//svg:animate', NS)
    assert len(animations) == 4
    for animation in animations:
        assert animation.get('attributeName') == 'opacity'
        assert animation.get('dur') == '28s'
        times = [float(t) for t in animation.get('keyTimes').split(';')]
        assert times[0] == 0 and times[-1] == 1
        assert all(a < b for a, b in zip(times, times[1:]))
        assert len(times) == len(animation.get('values').split(';'))
    ids = [node.get('id') for node in root.iter() if node.get('id')]
    assert len(ids) == len(set(ids)), 'Duplicate SVG identifiers'
    assert path.stat().st_size < 30_000
    print(f'{path.name}: four connected stages, shared 28s highlight cycle')


def main():
    for suffix in ('', '-dark'):
        check_cover(ROOT / f'assets/design-cover{suffix}.svg')
        check_workflow(ROOT / f'assets/practice-workflow{suffix}.svg')
    referenced = set()
    for page in ('README.md', 'preview.html'):
        for name in re.findall(r'(?:src|srcset)="(?:\./)?(assets/[^\"]+)"', (ROOT / page).read_text()):
            assert (ROOT / name).is_file(), f'Missing image: {name}'
            ET.parse(ROOT / name)
            referenced.add(name)
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / 'assets').glob('*')}
    assert actual == referenced, f'Unused artwork: {actual - referenced}'
    print('References checked; no unused artwork')


if __name__ == '__main__':
    main()
