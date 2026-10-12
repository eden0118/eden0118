"""Four static diagrams sharing the dossier's monochrome pixel grid."""


def box(x, y, w, h, accent=False):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{("#24424b" if accent else "#101e23")}" '
            'stroke="#b5ccd0" stroke-width="1.5"/>')


def route(path, arrow=False):
    marker = ' marker-end="url(#arrow)"' if arrow else ''
    return f'<path d="{path}" fill="none" stroke="#7d9fa6" stroke-width="1.5"{marker}/>'


def planning():
    parts = []
    for x, y in [(0, 9), (34, 45), (68, 0)]:
        parts += [box(x, y, 27, 37), route(f'M{x+6} {y+12}h15M{x+6} {y+22}h11')]
    parts += [route('M105 41H138', True), box(168, 0, 64, 28, True),
              route('M200 28V55M167 78V55H239V78'), box(145, 78, 44, 24), box(217, 78, 44, 24)]
    return ''.join(parts)


def experience():
    parts = []
    for x in [0, 99, 198]:
        parts += [box(x, 5, 73, 88), route(f'M{x} 22h73M{x+10} 38h44M{x+10} 49h34'), box(x+10, 65, 44, 16, True)]
        if x < 198:
            parts += [route(f'M{x+78} 49h16', True)]
    return ''.join(parts)


def collaboration():
    parts = []
    for y, text in [(13, 'Users'), (49, 'Business'), (85, 'Engineering')]:
        parts += [f'<text x="0" y="{y}" font-size="17">{text}</text>', route(f'M116 {y-5}H130L164 46', True)]
    parts += [box(184, 19, 83, 55, True), '<text x="225" y="43" font-size="15" text-anchor="middle">Shared</text>',
              '<text x="225" y="62" font-size="15" text-anchor="middle">plan</text>']
    return ''.join(parts)


def frontend():
    return ''.join([box(0, 5, 106, 87), route('M0 23H106M27 23V92'), box(39, 36, 51, 18, True),
                    route('M39 67H86M39 79H71'), route('M116 48H147', True), box(163, 5, 42, 28), box(231, 5, 42, 28),
                    route('M184 33V56H252V33M218 56V78'), box(197, 78, 42, 24, True)])


def panels(pixel_text):
    rows = [('structure', 40, 554, 'PLANNING', planning),
            ('journey', 380, 554, 'USER EXPERIENCE', experience),
            ('alignment', 40, 780, 'COLLABORATION', collaboration),
            ('delivery', 380, 780, 'FRONT-END', frontend)]
    return ''.join(f'<g data-stage="{name}">' + pixel_text(x, y, title, 2.5)
                   + f'<g transform="translate({x},{y+55})">' + renderer() + '</g></g>'
                   for name, x, y, title, renderer in rows)
