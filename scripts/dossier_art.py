"""Render a self-contained pixel identity card inspired by the supplied reference."""
from html import escape
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BG, PANEL, INK, MUTED = '#050e11', '#111d20', '#afc2c5', '#71898e'
# Five-column bitmap lettering: no installed fonts or remote resources required.
GLYPHS = {
    'A':'01110/10001/10001/11111/10001/10001/10001',
    'B':'11110/10001/10001/11110/10001/10001/11110',
    'C':'01111/10000/10000/10000/10000/10000/01111',
    'D':'11110/10001/10001/10001/10001/10001/11110',
    'E':'11111/10000/10000/11110/10000/10000/11111',
    'F':'11111/10000/10000/11110/10000/10000/10000',
    'G':'01111/10000/10000/10111/10001/10001/01111',
    'H':'10001/10001/10001/11111/10001/10001/10001',
    'I':'11111/00100/00100/00100/00100/00100/11111',
    'J':'00111/00010/00010/00010/10010/10010/01100',
    'K':'10001/10010/10100/11000/10100/10010/10001',
    'L':'10000/10000/10000/10000/10000/10000/11111',
    'M':'10001/11011/10101/10101/10001/10001/10001',
    'N':'10001/11001/10101/10011/10001/10001/10001',
    'O':'01110/10001/10001/10001/10001/10001/01110',
    'P':'11110/10001/10001/11110/10000/10000/10000',
    'Q':'01110/10001/10001/10001/10101/10010/01101',
    'R':'11110/10001/10001/11110/10100/10010/10001',
    'S':'01111/10000/10000/01110/00001/00001/11110',
    'T':'11111/00100/00100/00100/00100/00100/00100',
    'U':'10001/10001/10001/10001/10001/10001/01110',
    'V':'10001/10001/10001/10001/10001/01010/00100',
    'W':'10001/10001/10001/10101/10101/10101/01010',
    'X':'10001/10001/01010/00100/01010/10001/10001',
    'Y':'10001/10001/01010/00100/00100/00100/00100',
    'Z':'11111/00001/00010/00100/01000/10000/11111',
    '0':'01110/10001/10011/10101/11001/10001/01110',
    '1':'00100/01100/00100/00100/00100/00100/01110',
    '2':'01110/10001/00001/00010/00100/01000/11111',
    '3':'11110/00001/00001/01110/00001/00001/11110',
    '4':'00010/00110/01010/10010/11111/00010/00010',
    '5':'11111/10000/10000/11110/00001/00001/11110',
    '6':'01110/10000/10000/11110/10001/10001/01110',
    '7':'11111/00001/00010/00100/01000/01000/01000',
    '8':'01110/10001/10001/01110/10001/10001/01110',
    '9':'01110/10001/10001/01111/00001/00001/01110',
    '-':'00000/00000/00000/11111/00000/00000/00000',
    '.':'00000/00000/00000/00000/00000/00110/00110',
    '/':'00001/00001/00010/00100/01000/10000/10000',
    ':':'00000/00100/00100/00000/00100/00100/00000',
    ' ':'00000/00000/00000/00000/00000/00000/00000',
}


def label(value, x, y, size=2, color=INK):
    commands = []
    for index, char in enumerate(value.upper()):
        for row, bits in enumerate(GLYPHS[char].split('/')):
            for col, bit in enumerate(bits):
                if bit == '1':
                    commands.append(f'M{x + index * size * 6 + col * size:g} {y + row * size:g}h{size:g}v{size:g}h-{size:g}z')
    return f'<path fill="{color}" aria-label="{escape(value)}" d="{"".join(commands)}"/>'


def portrait():
    image = Image.open(ROOT / 'assets/design.png').convert('RGB')
    difference = ImageChops.difference(image, Image.new('RGB', image.size, 'white'))
    bounds = difference.convert('L').point(lambda v: 255 if v > 35 else 0).getbbox()
    if bounds:
        image = image.crop(bounds)
    image = ImageOps.pad(image.convert('L'), (132, 132), color='white')
    image = ImageEnhance.Contrast(image).enhance(1.15)
    matrix = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    palette = ['#14272c', '#365d65', '#59858e', '#8bb9bf']
    paths = [[] for _ in palette]
    for y in range(132):
        levels = [max(0, min(3, int(image.getpixel((x, y)) / 255 * 3 + (matrix[y % 4][x % 4] + .5) / 16))) for x in range(132)]
        x = 0
        while x < 132:
            level, start = levels[x], x
            while x < 132 and levels[x] == level:
                x += 1
            paths[level].append(f'M{start} {y}h{x-start}v1h-{x-start}z')
    return '<g transform="translate(22 132) scale(2)">' + ''.join(f'<path fill="{color}" d="{"".join(commands)}"/>' for color, commands in zip(palette, paths)) + '</g>'


def dossier():
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="560" height="744" viewBox="0 0 560 744" role="img" aria-labelledby="title description" shape-rendering="crispEdges">',
        '<title id="title">Eden Chang — Technical Product Manager</title>',
        '<desc id="description">A cyan pixel identity card. Background: industrial design, metalwork, exhibition planning. Working practice: planning, user experience, collaboration across users, business and engineering, and front-end. Curious builder.</desc>',
        f'<rect width="560" height="744" fill="{BG}"/>',
        f'<rect x="12" y="12" width="536" height="720" fill="none" stroke="{MUTED}"/>',
        f'<path d="M12 54H548M12 122H548M12 406H548M12 674H548M296 122V406" stroke="{MUTED}" fill="none"/>',
        f'<rect x="13" y="55" width="534" height="66" fill="{PANEL}"/>',
        label('ED / ID', 24, 28, 2.5), label('SIGNAL LOW', 312, 29, 2, MUTED),
        '<g fill="none" stroke="#afc2c5"><path d="M490 26h40v18h-40zM531 31h4v8h-4"/></g>',
        '<path fill="#afc2c5" d="M494 30h6v10h-6zM503 30h6v10h-6zM512 30h6v10h-6zM521 30h5v10h-5z"/>',
        label('PERSONNEL', 24, 65, 1.7, MUTED), label('ACCESS', 474, 65, 1.5, MUTED),
        label('EDEN CHANG', 24, 87, 3.5), label('GRANTED', 464, 91, 1.5),
        portrait(),
        f'<rect x="21" y="131" width="266" height="266" fill="none" stroke="{INK}"/>',
        label('TECHNICAL', 310, 139, 2.3),
        label('PRODUCT', 310, 164, 2.3),
        label('MANAGER', 310, 189, 2.3),
        label('SEC CODE', 310, 230, 1.8, MUTED),
        label('EDEN-0118', 310, 250, 2.1),
        label('INDUSTRIAL DESIGN', 310, 286, 1.8),
        label('METALWORK', 310, 307, 1.8),
        label('EXHIBITION', 310, 328, 1.8),
        label('PLANNING', 310, 349, 1.8),
        '<g fill="#71898e"><path d="M310 374h6v19h-6zM320 367h6v26h-6zM330 378h6v15h-6z"/></g>',
        label('CURIOUS BUILDER', 349, 378, 1.8, MUTED),
        label('WORKING PRACTICE', 24, 427, 2.3),
        label('PLANNING / USER EXPERIENCE', 24, 464, 2),
        label('COLLABORATION / FRONT-END', 24, 491, 2),
        label('USERS / BUSINESS / ENGINEERING', 24, 533, 2, MUTED),
        label('FROM INDUSTRIAL DESIGN AND METALWORK', 24, 575, 2),
        label('TO EXHIBITION PLANNING AND PRODUCT', 24, 601, 2),
        label('DEVELOPMENT. ALWAYS A CURIOUS BUILDER.', 24, 627, 2),
        label('PROPERTY OF EDEN CHANG', 154, 691, 1.8, MUTED),
        label('PRODUCT DEVELOPMENT UNIT', 137, 713, 1.8, MUTED),
    ]
    # Corner registration marks and asymmetric wings echo the reference's footer.
    parts.append('<g fill="none" stroke="#afc2c5"><path d="M12 23V12h11M537 12h11v11M12 721v11h11M537 732h11v-11M21 142v-11h11M276 131h11v11M21 386v11h11M276 397h11v-11"/></g>')
    for x in (28, 487):
        parts.append(f'<path fill="{MUTED}" d="M{x} 687h39v3h-39zM{x+5} 693h29v3h-29zM{x+10} 699h19v3h-19zM{x+15} 705h9v3h-9zM{x+17} 708h5v14h-5z"/>')
    parts.append('</svg>')
    return ''.join(parts)


if __name__ == '__main__':
    (ROOT / 'assets/profile-dossier.svg').write_text(dossier())
    print('Generated pixel identity card')
