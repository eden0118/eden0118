#!/usr/bin/env python3
"""Generate a continuous native SVG carousel and lightweight profile diagrams."""
import argparse
import html
from pathlib import Path
import random
import re

from practice_art import diagrams

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('design.png', 'need-sleep.png', 'working.png', 'drink.png')
COLS, ROWS, BANDS = 100, 96, 8
SLIDE_SECONDS = 7
RAMP = ' .:-=+*#'


def ascii_lines(source, cols=100, rows=96):
    from PIL import Image, ImageChops, ImageEnhance, ImageOps
    image = Image.open(source).convert("RGB")
    if source.name == "working.png":
        # The bottom caption sits below the illustration in this source image.
        image = image.crop((0, 0, image.width, round(image.height * .84)))
    difference = ImageChops.difference(image, Image.new("RGB", image.size, "white"))
    bounds = difference.convert("L").point(lambda value: 255 if value > 35 else 0).getbbox()
    if bounds:
        x0, y0, x1, y1 = bounds
        margin = round(max(x1 - x0, y1 - y0) * .035)
        image = image.crop((max(0, x0 - margin), max(0, y0 - margin),
                            min(image.width, x1 + margin), min(image.height, y1 + margin)))
    # Pad rather than crop so each illustration keeps its full composition.
    image = ImageOps.pad(image.convert("L"), (cols, rows), color="white")
    image = ImageEnhance.Contrast(image).enhance(1.2)
    ramp = " .:-=+*#"
    return ["".join(ramp[round((255 - image.getpixel((col, row))) / 255 * (len(ramp) - 1))]
                    for col in range(cols)) for row in range(rows)]


def dark_variant(svg):
    """Recolor the shared artwork without changing layout or animation timing."""
    palette = {
        "#fafafa": "#0d1117", "#18181b": "#e6edf3",
        "#46515f": "#a6b2c0", "#2563eb": "#8db1ff",
        "#dce0e5": "#30363d", "#929ba8": "#8b98a8",
        "#edf2ff": "#17263d", "#f0f2f5": "#161b22",
        "#e8ecf0": "#161b22", "#bcd0fa": "#23395e",
        "#7ea4ef": "#315486", "#487adb": "#547fc0",
    }
    return re.sub(r"#[0-9a-fA-F]{6}", lambda match: palette.get(match[0].lower(), match[0]), svg)


def timeline(attribute, points, cycle):
    """Interpolate on one shared clock; no discrete frame swapping."""
    ordered = sorted(dict(points).items())
    times = ';'.join(f'{seconds/cycle:.8f}' for seconds, _ in ordered)
    values = ';'.join(f'{value:g}' for _, value in ordered)
    return (f'<animate attributeName="{attribute}" values="{values}" keyTimes="{times}" '
            f'calcMode="linear" dur="{cycle:g}s" repeatCount="indefinite"/>')


def text_rows(lines, ink):
    return ''.join(
        f'<text x="24" y="{32+row*736/ROWS:.2f}" fill="{ink}" font-size="10.2" '
        f'xml:space="preserve" textLength="792" lengthAdjust="spacingAndGlyphs">'
        f'{html.escape(line)}</text>' for row, line in enumerate(lines))


def portrait(sources, dark):
    cycle = len(sources) * SLIDE_SECONDS
    ink = '#b7cdc8' if dark else '#30383b'
    parts = ['<style>.portrait-glyphs{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}'
             '@media(prefers-reduced-motion:reduce){.portrait-scene{display:none!important}'
             '.portrait-first{display:inline!important;opacity:1!important}'
             '.portrait-final{clip-path:none!important}.portrait-noise{display:none!important}}</style>']
    for slide, source in enumerate(sources):
        lines = ascii_lines(source, COLS, ROWS)
        rng = random.Random(18 + slide)
        noise = [''.join(rng.choice(RAMP[max(1, RAMP.index(c)-1):min(len(RAMP), RAMP.index(c)+2)])
                         if c != ' ' else ' ' for c in line) for line in lines]
        parts.append(f'<defs><g id="pose-{slide}" class="portrait-glyphs">{text_rows(lines, ink)}</g>'
                     f'<g id="noise-{slide}" class="portrait-glyphs">{text_rows(noise, ink)}</g></defs>')
        offset = slide * SLIDE_SECONDS
        delays = [0, .35, .1, .65, .2, .8, .45, .05]
        parts.append(f'<clipPath id="reveal-{slide}">')
        for band, delay in enumerate(delays):
            x, width = 24 + band * 99, 99
            begin, finish = offset + delay, offset + delay + 2.8
            parts.append(f'<rect x="{x}" y="16" width="{width}" height="764" data-band="{band}">')
            parts.append(timeline('width', [(0, 0), (begin, 0), (finish, width), (cycle, width)], cycle))
            if band % 2:
                parts.append(timeline('x', [(0, x+width), (begin, x+width), (finish, x), (cycle, x)], cycle))
            parts.append('</rect>')
        parts.append('</clipPath>')
        first = ' portrait-first' if slide == 0 else ''
        parts.append(f'<g class="portrait-scene{first}" opacity="{1 if slide == 0 else 0}" data-scene="{html.escape(source.stem)}">')
        if slide == 0:
            visibility = [(0, 0), (.25, 1), (6.6, 1), (7, 0), (cycle, 0)]
        else:
            visibility = [(0, 0), (offset-.3, 0), (offset, 1),
                          (offset+6.6, 1), (offset+7, 0), (cycle, 0)]
        parts.append(timeline('opacity', visibility, cycle))
        parts.append(f'<use class="portrait-noise" href="#noise-{slide}" opacity="0">')
        parts.append(timeline('opacity', [(0, 0), (offset, .16), (offset+.35, .23),
                                        (offset+1.8, 0), (cycle, 0)], cycle))
        parts.append('</use>')
        parts.append(f'<use class="portrait-final" href="#pose-{slide}" clip-path="url(#reveal-{slide})"/>')
        parts.append('</g>')
    return ''.join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portrait', type=Path, nargs='+',
                        default=[ROOT / name for name in SOURCES])
    args = parser.parse_args()
    template = (ROOT / 'scripts/design-cover-template.svg').read_text()
    output = diagrams()
    for name, svg in list(output.items()):
        output[name.replace('.svg', '-dark.svg')] = dark_variant(svg)
    for dark in (False, True):
        suffix = '-dark' if dark else ''
        base = dark_variant(template) if dark else template
        output[f'assets/design-cover{suffix}.svg'] = base.replace('{PORTRAIT}', portrait(args.portrait, dark))
    for name, content in output.items():
        (ROOT / name).write_text(content)
    print(f'Generated {len(output)} assets: native continuous SVG motion, {len(args.portrait)*SLIDE_SECONDS}s loop')


if __name__ == '__main__':
    main()
