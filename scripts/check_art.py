#!/usr/bin/env python3
"""Check continuous SVG motion, lightweight assets, and README references."""
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
    assert len(clips) == 4 and all(len(clip.findall('svg:rect', NS)) == 8 for clip in clips)
    assert 'prefers-reduced-motion' in content and 'portrait-first' in content
    print(f'{path.name}: {path.stat().st_size // 1024} KB, continuous four-scene SVG loop')


def main():
    for suffix in ('', '-dark'):
        check_cover(ROOT / f'assets/design-cover{suffix}.svg')
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
