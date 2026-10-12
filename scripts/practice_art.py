"""Four connected working practices, drawn as one compact product map."""
from html import escape

INK, MUTED, BLUE = '#18181b', '#46515f', '#2563eb'
LINE, PAPER, TINT = '#929ba8', '#fafafa', '#edf2ff'


def label(x, y, value, size=17, color=MUTED, anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>'


def box(x, y, w, h, accent=False):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" '
            f'fill="{TINT if accent else PAPER}" stroke="{BLUE if accent else INK}" stroke-width="1.5"/>')


def route(path, arrow=True, color=LINE):
    marker = ' marker-end="url(#arrow)"' if arrow else ''
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.5"{marker}/>'


def structure():
    parts = []
    for x, y in [(54, 205), (93, 239), (132, 191)]:
        parts += [box(x, y, 36, 45), route(f'M{x+8} {y+13}h20M{x+8} {y+23}h15M{x+8} {y+33}h18', False)]
    parts += [route('M179 240H218'), box(240, 191, 86, 32, True),
              route('M283 223V248M243 271V248H323V271', False),
              box(214, 271, 58, 27), box(294, 271, 58, 27)]
    return ''.join(parts)


def journey():
    parts = []
    for i, x in enumerate([474, 591, 708]):
        parts += [box(x, 205, 92, 91), route(f'M{x} 224h92', False, INK),
                  route(f'M{x+12} 241h46M{x+12} 252h63', False),
                  box(x+12, 264, 50, 18, True)]
        if i < 2:
            parts += [route(f'M{x+96} 251h17')]
    return ''.join(parts)


def alignment():
    parts = []
    for y, text in [(477, 'Users'), (516, 'Business'), (555, 'Engineering')]:
        parts += [label(474, y+7, text, 17, INK), route(f'M587 {y+2}H604L632 526')]
    parts += [box(652, 493, 140, 64, True), label(722, 519, 'Shared', 18, INK, 'middle'),
              label(722, 542, 'direction', 18, INK, 'middle')]
    return ''.join(parts)


def delivery():
    return ''.join([
        box(54, 482, 128, 90), route('M54 501h128M88 501V572', False, INK),
        box(101, 513, 65, 21, True), route('M101 548h52M101 558h40', False),
        route('M195 526h37'), box(249, 481, 44, 30), box(316, 481, 44, 30),
        route('M271 511V532H338V511M305 532V554', False), box(281, 554, 48, 27, True)])


def highlight(index):
    offset = index * 7
    if index == 0:
        points = [(0, 1), (6.4, 1), (7, 0), (27.4, 0), (28, 1)]
    else:
        points = [(0, 0), (offset-.6, 0), (offset, 1), (offset+6.4, 1), (offset+7, 0), (28, 0)]
    points = sorted(dict(points).items())
    return ('<animate attributeName="opacity" values="' + ';'.join(str(value) for _, value in points)
            + '" keyTimes="' + ';'.join(f'{time/28:.8f}' for time, _ in points)
            + '" calcMode="linear" dur="28s" repeatCount="indefinite"/>')


def workflow():
    stages = [
        ('structure', 54, 128, 'Shape the problem', structure),
        ('journey', 474, 128, 'Map the journey', journey),
        ('alignment', 474, 414, 'Align the people', alignment),
        ('delivery', 54, 414, 'Make it work', delivery),
    ]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="860" height="530" viewBox="0 0 860 530" '
             'role="img" font-family="Helvetica Neue, Helvetica, Arial, sans-serif">'
             '<title>From loose ends to a working product</title>'
             '<desc>Four connected drawings show how Eden organizes requirements, maps interface journeys, '
             'aligns user, business and engineering needs, and brings decisions into front-end code. '
             'Read across the top, then back across the bottom.</desc>'
             '<style>@media(prefers-reduced-motion:reduce){.stage-active{display:none!important}}</style>'
             '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">'
             f'<path d="M0 0L7 3.5L0 7" fill="{LINE}"/></marker></defs>'
             f'<rect width="860" height="530" fill="{PAPER}"/><g transform="translate(0,-90)">',
             route('M388 246H447'), route('M640 353V385'), route('M447 526H388')]
    for index, (name, x, y, title, renderer) in enumerate(stages):
        parts += [f'<g data-stage="{name}">',
                  label(x, y+3, f'{index+1:02}', 16, MUTED),
                  label(x, y+34, title, 26, INK), renderer(),
                  f'<g class="stage-active" opacity="0" data-active="{name}">',
                  label(x, y+3, f'{index+1:02}', 16, BLUE),
                  label(x, y+34, title, 26, BLUE), highlight(index), '</g></g>']
    parts += ['</g></svg>']
    return ''.join(parts)


def diagrams():
    return {'assets/practice-workflow.svg': workflow()}
