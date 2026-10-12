#!/usr/bin/env python3
"""Generate graphic-only assets for a Markdown personal dossier."""
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageOps
from practice_art import diagrams
from dossier_art import dossier
from terminal_art import graphics

ROOT = Path(__file__).resolve().parents[1]


def portrait():
    image = Image.open(ROOT / 'assets/design.png').convert('RGB')
    difference = ImageChops.difference(image, Image.new('RGB', image.size, 'white'))
    bounds = difference.convert('L').point(lambda v: 255 if v > 35 else 0).getbbox()
    if bounds:
        image = image.crop(bounds)
    image = ImageOps.pad(image.convert('L'), (118, 110), color='white')
    image = ImageEnhance.Contrast(image).enhance(1.15)
    matrix = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
    palette = ['#14272c', '#365d65', '#59858e', '#8bb9bf']
    paths = [[] for _ in palette]
    for y in range(110):
        levels = [max(0, min(3, int(image.getpixel((x,y))/255*3 + (matrix[y%4][x%4]+.5)/16))) for x in range(118)]
        x = 0
        while x < 118:
            level, start = levels[x], x
            while x < 118 and levels[x] == level:
                x += 1
            paths[level].append(f'M{start} {y}h{x-start}v1h-{x-start}z')
    return ('<g id="portrait" transform="translate(14,17) scale(2.6)" shape-rendering="crispEdges">'
            + ''.join(f'<path fill="{color}" d="{"".join(commands)}"/>' for color, commands in zip(palette, paths)) + '</g>')


def main():
    avatar = ('<svg xmlns="http://www.w3.org/2000/svg" width="336" height="320" viewBox="0 0 336 320" role="img">'
              '<title>Pixel character</title><desc>A cyan ordered-dither character drawing at a desk.</desc>'
              '<rect width="336" height="320" fill="#101e23"/>' + portrait()
              + '<path d="M4 14V4H14M322 4H332V14M4 306V316H14M322 316H332V306" fill="none" stroke="#b5ccd0"/>'
              '</svg>')
    output = {'assets/profile-avatar.svg': avatar, 'assets/profile-dossier.svg': dossier(), **diagrams(), **graphics()}
    for name, content in output.items():
        (ROOT / name).write_text(content)
    print(f'Generated {len(output)} assets, including the pixel identity card')


if __name__ == '__main__':
    main()
