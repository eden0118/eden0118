#!/usr/bin/env python3
"""Generate a self-contained, pixel-style personal dossier."""
from pathlib import Path
from html import escape
from PIL import Image, ImageChops, ImageEnhance, ImageOps
from practice_art import panels

ROOT = Path(__file__).resolve().parents[1]
GLYPHS = {
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'J':['00111','00010','00010','00010','00010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10011','10101','11001','10001','01110'],
'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
'/':['00001','00001','00010','00100','01000','10000','10000'],
'.':['00000','00000','00000','00000','00000','00110','00110'],
'-':['00000','00000','00000','11111','00000','00000','00000'],
' ':['00000']*7,
}


def pixel_text(x, y, value, scale=2, color='#b5ccd0'):
    commands = []
    for index, char in enumerate(value.upper()):
        for row, bits in enumerate(GLYPHS[char]):
            for col, bit in enumerate(bits):
                if bit == '1':
                    commands.append(f'M{index*6+col} {row}h1v1h-1z')
    return (f'<g role="img" aria-label="{escape(value)}" transform="translate({x},{y}) scale({scale})">'
            f'<title>{escape(value)}</title><path fill="{color}" d="{"".join(commands)}"/></g>')


def portrait():
    image = Image.open(ROOT / 'design.png').convert('RGB')
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
    return ('<g id="portrait" transform="translate(34,179) scale(2.6)" shape-rendering="crispEdges">'
            + ''.join(f'<path fill="{color}" d="{"".join(commands)}"/>' for color, commands in zip(palette, paths)) + '</g>')


def main():
    template = (ROOT / 'scripts/design-cover-template.svg').read_text()
    header = ''.join([
        pixel_text(40, 37, 'PROFILE / EDEN0118', 2.1),
        pixel_text(524, 37, 'PERSONAL FILE', 1.9, '#7d9fa6'),
        pixel_text(40, 80, 'EDEN CHANG', 5.7),
        '<text x="40" y="145" font-size="23" fill="#a8c6cd">Technical Product Manager</text>',
    ])
    background = ''.join([
        pixel_text(380, 188, 'BACKGROUND', 2.5),
        '<text x="380" y="249" font-size="22">Industrial design</text>',
        '<text x="380" y="323" font-size="22">Metalwork</text>',
        '<text x="380" y="397" font-size="22">Exhibition planning</text>',
        pixel_text(40, 500, 'WORKING PRACTICE', 2.2),
        pixel_text(40, 996, 'CURIOUS BUILDER', 2.2),
    ])
    svg = template.replace('{HEADER}', header).replace('{PORTRAIT}', portrait()).replace('{BACKGROUND}', background).replace('{PANELS}', panels(pixel_text))
    (ROOT / 'assets/profile-card.svg').write_text(svg)
    print(f'Generated profile-card.svg: {len(svg.encode())//1024} KB, one-shot startup, four practices')


if __name__ == '__main__':
    main()
