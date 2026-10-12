#!/usr/bin/env python3
"""Check the shipped artwork's animation cadence, size, and README references."""
import base64
import io
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
NS = {'svg': 'http://www.w3.org/2000/svg'}


def check_cover(path):
    content = path.read_text()
    root = ET.fromstring(content)
    assert path.stat().st_size < 1_100_000, f'{path.name}: exceeds the download budget'
    assert len(list(root.iter())) < 32, f'{path.name}: too many live rendering elements'
    motion = root.find('.//svg:image[@class="portrait-motion"]', NS)
    still = root.find('.//svg:image[@class="portrait-still"]', NS)
    assert motion is not None and still is not None
    assert 'prefers-reduced-motion' in content
    animation = Image.open(io.BytesIO(base64.b64decode(motion.attrib['href'].split(',', 1)[1])))
    total, holds, initial_changes = 0, 0, set()
    for frame in ImageSequence.Iterator(animation):
        duration = frame.info['duration']
        if total < 2100:
            initial_changes.add(frame.convert('RGB').tobytes())
        holds += duration >= 3000
        total += duration
    assert animation.info.get('loop') == 0
    assert total == 28000 and holds == 4, 'Carousel must show all four scenes and repeat'
    assert len(initial_changes) / 2.1 >= 18, 'Visible typing updates fall below 18 fps'
    print(f'{path.name}: {path.stat().st_size // 1024} KB, {len(list(root.iter()))} elements, smooth four-scene loop')


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
    print('README and preview references checked; no unused artwork')


if __name__ == '__main__':
    main()
