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
    for y in [0, 36, 72]:
        parts += [box(0, y, 95, 25), route(f'M105 {y+12}H125L163 48', True)]
    parts += [box(184, 21, 83, 55, True), route('M197 38H254M197 49H241M197 60H250')]
    return ''.join(parts)


def frontend():
    return ''.join([box(0, 5, 106, 87), route('M0 23H106M27 23V92'), box(39, 36, 51, 18, True),
                    route('M39 67H86M39 79H71'), route('M116 48H147', True), box(163, 5, 42, 28), box(231, 5, 42, 28),
                    route('M184 33V56H252V33M218 56V78'), box(197, 78, 42, 24, True)])


def diagrams():
    renderers = {'planning': planning, 'experience': experience, 'collaboration': collaboration, 'frontend': frontend}
    output = {}
    for name, renderer in renderers.items():
        output[f'assets/practice-{name}.svg'] = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="336" height="160" viewBox="0 0 336 160" role="img">'
            f'<title>{name.capitalize()} diagram</title>'
            '<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">'
            '<path d="M0 0L6 3L0 6" fill="#7d9fa6"/></marker></defs>'
            '<rect width="336" height="160" fill="#101e23"/>'
            '<path d="M4 14V4H14M322 4H332V14M4 146V156H14M322 156H332V146" fill="none" stroke="#617f86"/>'
            '<g transform="translate(32,29)">' + renderer() + '</g></svg>')
    return output
