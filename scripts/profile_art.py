#!/usr/bin/env python3
"""Generate lightweight profile artwork from the four source illustrations."""
import argparse
import base64
from functools import lru_cache
import io
from pathlib import Path
import random
import re

from PIL import Image, ImageDraw, ImageFont
from practice_art import diagrams

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('design.png', 'need-sleep.png', 'working.png', 'drink.png')
FRAMES, FRAME_MS, HOLD_MS = 72, 50, 3400
COLS, ROWS = 100, 96
SIZE, SCALE = (300, 286), 2
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


@lru_cache(maxsize=8192)
def render_row(line):
    """Cache small monochrome strips; glyph positions use a fixed ASCII grid."""
    strip = Image.new('L', (SIZE[0] * SCALE, 10), 0)
    draw = ImageDraw.Draw(strip)
    font = ImageFont.load_default(size=8)
    for col, character in enumerate(line):
        if character != ' ':
            x = (24 + col * 792 / COLS) * SIZE[0] / 840 * SCALE
            draw.text((x, 0), character, fill=255, font=font)
    return strip


def render_mask(lines):
    mask = Image.new('L', (SIZE[0] * SCALE, SIZE[1] * SCALE), 0)
    for row, line in enumerate(lines):
        y = round((24 + row * 736 / ROWS) * SIZE[1] / 800 * SCALE)
        strip = render_row(line)
        # Maximum compositing preserves glyph edges where strips overlap.
        from PIL import ImageChops
        area = mask.crop((0, y, strip.width, y + strip.height))
        mask.paste(ImageChops.lighter(area, strip), (0, y))
    return mask.resize(SIZE, Image.Resampling.LANCZOS).point(
        [round(value / 17) for value in range(256)], mode='P')


def carousel_frames(sources):
    frames, durations = [], []
    for slide, source in enumerate(sources):
        lines = ascii_lines(source, COLS, ROWS)
        rng = random.Random(18 + slide)
        timing = [[(rng.uniform(0, .38), rng.uniform(.42, .98))
                   for _ in range(COLS)] for _ in range(ROWS)]
        for frame in range(FRAMES):
            progress = (frame + 1) / FRAMES
            changing = []
            for row, line in enumerate(lines):
                characters = []
                for col, target in enumerate(line):
                    arrival, settled = timing[row][col]
                    if target == ' ' or progress < arrival:
                        characters.append(' ')
                    elif progress >= settled:
                        characters.append(target)
                    else:
                        index = RAMP.index(target)
                        variants = RAMP[max(1, index - 2):min(len(RAMP), index + 3)]
                        characters.append(rng.choice(variants))
                changing.append(''.join(characters))
            frames.append(render_mask(changing))
            durations.append(FRAME_MS)
        frames.append(render_mask(lines))
        durations.append(HOLD_MS)
    return frames, durations, render_mask(ascii_lines(sources[0], COLS, ROWS))


def palette(dark):
    background, ink = ((13, 17, 23), (183, 205, 200)) if dark else ((250, 250, 250), (48, 56, 59))
    colors = [round(background[channel] + (ink[channel] - background[channel]) * level / 15)
              for level in range(16) for channel in range(3)]
    return colors + [0] * (768 - len(colors))


def cover(template, frames, durations, still, dark):
    colored = []
    for frame in frames:
        frame = frame.copy()
        frame.putpalette(palette(dark))
        colored.append(frame)
    animation = io.BytesIO()
    colored[0].save(animation, format='GIF', save_all=True, append_images=colored[1:],
                    duration=durations, loop=0, optimize=True, disposal=1)
    still = still.copy()
    still.putpalette(palette(dark))
    poster = io.BytesIO()
    still.save(poster, format='PNG', optimize=True)
    gif = base64.b64encode(animation.getvalue()).decode('ascii')
    png = base64.b64encode(poster.getvalue()).decode('ascii')
    portrait = ('<style>.portrait-still{display:none}'
                '@media(prefers-reduced-motion:reduce){.portrait-motion{display:none!important}.portrait-still{display:inline!important}}</style>'
                f'<image class="portrait-motion" width="840" height="800" href="data:image/gif;base64,{gif}"/>'
                f'<image class="portrait-still" width="840" height="800" href="data:image/png;base64,{png}"/>')
    return (dark_variant(template) if dark else template).replace('{PORTRAIT}', portrait)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portrait', type=Path, nargs='+',
                        default=[ROOT / name for name in SOURCES],
                        help='Source illustrations in carousel order')
    args = parser.parse_args()
    frames, durations, still = carousel_frames(args.portrait)
    template = (ROOT / 'scripts/design-cover-template.svg').read_text()
    output = diagrams()
    for name, svg in list(output.items()):
        output[name.replace('.svg', '-dark.svg')] = dark_variant(svg)
    output['assets/design-cover.svg'] = cover(template, frames, durations, still, False)
    output['assets/design-cover-dark.svg'] = cover(template, frames, durations, still, True)
    for name, content in output.items():
        (ROOT / name).write_text(content)
    print(f'Generated {len(output)} assets: {len(args.portrait)} scenes, 20 fps, {sum(durations)/1000:g}s loop')


if __name__ == '__main__':
    main()
