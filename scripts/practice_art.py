"""Small animated SVG studies that explain the profile's working methods."""

from html import escape

INK, MUTED, BLUE = '#18181b', '#46515f', '#2563eb'


def label(x, y, value, size=17, color=MUTED, anchor='middle'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}">{escape(value)}</text>'


def arrow(path):
    return f'<path d="{path}" fill="none" stroke="#929ba8" stroke-width="1.5" marker-end="url(#arrow)"/>'


def traveler(path, delay=0):
    return (f'<circle class="motion" r="4" fill="{BLUE}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.02;.28;.32;1" dur="9s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animateMotion path="{path}" keyPoints="0;1;1" keyTimes="0;.3;1" calcMode="linear" dur="9s" begin="{delay}s" repeatCount="indefinite"/></circle>')


def sheet(title, description, content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="190" viewBox="0 0 860 190" role="img" font-family="Helvetica Neue, Helvetica, Arial, sans-serif">'
            f'<title>{escape(title)}</title><desc>{escape(description)}</desc>'
            '<style>@media(prefers-reduced-motion:reduce){.motion{display:none!important}}</style>'
            '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7" fill="#929ba8"/></marker></defs>'
            '<rect width="860" height="190" fill="#fafafa"/>' + content + '</svg>')


def structure():
    parts = []
    for x, y in [(58, 39), (119, 69), (180, 27)]:
        parts.append(f'<g fill="#fafafa" stroke="{INK}" stroke-width="1.5"><rect x="{x}" y="{y}" width="48" height="51" rx="2"/><path d="M{x+9} {y+16}h30M{x+9} {y+25}h23M{x+9} {y+34}h27" stroke="#929ba8"/></g>')
    parts.extend([arrow('M257 88H330'), arrow('M522 88H595'),
                  '<g fill="none" stroke="#18181b" stroke-width="1.5"><rect x="390" y="31" width="72" height="36" rx="2"/><path d="M426 67V87M366 105V87H486V105"/><rect x="336" y="105" width="60" height="28" rx="2"/><rect x="456" y="105" width="60" height="28" rx="2"/></g>',
                  '<g fill="none" stroke="#18181b" stroke-width="1.5"><rect x="627" y="32" width="174" height="101" rx="3"/><path d="M627 51H801M672 51V133"/><path d="M687 68H785M687 83H760M687 98H780" stroke="#929ba8"/></g>'])
    # Moving notes converge on the structure rather than bouncing decoratively.
    for i, (x, y, dx, dy) in enumerate([(58, 39, 338, -4), (119, 69, 223, 36), (180, 27, 282, 78)]):
        parts.append(f'<g class="motion" opacity="0"><g fill="#edf2ff" stroke="{BLUE}" stroke-width="1.5"><rect x="{x}" y="{y}" width="48" height="28" rx="2"/><path d="M{x+8} {y+10}h29M{x+8} {y+18}h20"/></g>'
                     f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.04;.27;.34;1" dur="9s" begin="{i*.3}s" repeatCount="indefinite"/>'
                     f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};{dx} {dy}" keyTimes="0;.3;1" dur="9s" begin="{i*.3}s" repeatCount="indefinite"/></g>')
    parts.extend([label(146, 169, 'Initial requirements'), label(426, 169, 'Information architecture'), label(714, 169, 'Product plan')])
    return sheet('Organizing requirements into a product structure', 'Loose requirements converge into an information hierarchy and a concrete product plan.', ''.join(parts))


def journey():
    parts = []
    for i, x in enumerate([40, 330, 620]):
        parts.append(f'<g fill="none" stroke="{INK}" stroke-width="1.5"><rect x="{x}" y="25" width="190" height="113" rx="3"/><path d="M{x} 45h190"/></g>')
        parts.append(f'<path d="M{x+16} 61h70M{x+16} 73h109" stroke="#929ba8" stroke-width="2"/>')
        parts.append(f'<rect x="{x+16}" y="91" width="110" height="28" rx="3" fill="#edf2ff" stroke="{BLUE}"/>')
        parts.append(f'<rect class="motion" x="{x+16}" y="91" width="110" height="28" rx="3" fill="{BLUE}" opacity="0"><animate attributeName="opacity" values="0;.22;.22;0;0" keyTimes="0;.02;.2;.25;1" dur="9s" begin="{i*.9}s" repeatCount="indefinite"/></rect>')
    parts.extend([arrow('M246 82H312'), arrow('M536 82H602'), traveler('M166 105L280 105L280 82L425 82L425 105L571 105L571 82L715 82L715 105'),
                  label(135, 169, 'Entry point'), label(425, 169, 'User action'), label(715, 169, 'Next state')])
    return sheet('Following the user through interface states', 'A highlighted action moves the user through successive interface states, showing where information and interactions connect.', ''.join(parts))


def alignment():
    parts = []
    for y, word in [(25, 'User needs'), (73, 'Business goals'), (121, 'Technical constraints')]:
        parts.append(f'<rect x="40" y="{y}" width="182" height="30" rx="4" fill="none" stroke="{INK}" stroke-width="1.5"/>')
        parts.append(label(131, y+21, word, 16, INK))
        parts.append(arrow(f'M238 {y+15}H284L354 88'))
        parts.append(traveler(f'M238 {y+15}H284L391 88', (y-25)/160))
    parts.extend(['<circle cx="426" cy="88" r="36" fill="#edf2ff" stroke="#2563eb" stroke-width="1.5"/>', label(426, 94, 'Align', 18, INK),
                  arrow('M478 88H601'), traveler('M478 88H601', 2),
                  '<rect x="620" y="30" width="192" height="112" rx="3" fill="none" stroke="#18181b" stroke-width="1.5"/>',
                  '<path d="M639 54h117M639 71h152M639 88h98M639 105h131" stroke="#929ba8" stroke-width="2"/>',
                  label(426, 169, 'Shared priorities'), label(716, 169, 'A workable plan')])
    return sheet('Aligning different needs into a workable plan', 'User needs, business goals, and technical limits meet in a shared discussion before becoming a workable plan.', ''.join(parts))


def delivery():
    parts = ['<g fill="none" stroke="#18181b" stroke-width="1.5"><rect x="40" y="25" width="190" height="113" rx="3"/><path d="M40 45H230M86 45V138"/><rect x="102" y="61" width="109" height="28" fill="#edf2ff" stroke="#2563eb"/><path d="M102 106h80M102 118h101" stroke="#929ba8"/></g>',
             arrow('M246 82H317'),
             '<rect x="345" y="25" width="158" height="113" rx="3" fill="none" stroke="#18181b" stroke-width="1.5"/>',
             '<path d="M363 49h96M363 66h121M363 83h78M363 100h111M363 117h99" stroke="#929ba8" stroke-width="2"/>',
             arrow('M520 82H601'),
             '<g fill="none" stroke="#18181b" stroke-width="1.5"><rect x="622" y="31" width="68" height="37" rx="2"/><rect x="742" y="31" width="68" height="37" rx="2"/><rect x="682" y="105" width="68" height="30" rx="2" fill="#edf2ff" stroke="#2563eb"/><path d="M656 68V85H776V68M716 85V105"/></g>',
             traveler('M246 82H345', .2), traveler('M520 82H622L656 82L656 85H716V120', 1.4),
             label(135, 169, 'Interface design'), label(424, 169, 'States & constraints'), label(716, 169, 'Implementation')]
    return sheet('Keeping design intent through implementation', 'An interface design becomes explicit states and constraints, then connected components for implementation.', ''.join(parts))


def diagrams():
    return {f'assets/practice-{name}.svg': renderer() for name, renderer in [
        ('structure', structure), ('journey', journey), ('alignment', alignment), ('delivery', delivery)]}
