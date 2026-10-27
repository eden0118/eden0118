"""GitHub-compatible profile panels with phone, intermediate and desktop layouts."""
from html import escape
import textwrap
import re
from pathlib import Path
import xml.etree.ElementTree as ET

SANS = 'Arial,Helvetica,sans-serif'
MONO = 'ui-monospace,SFMono-Regular,Consolas,monospace'
ICON_SURFACE = '#293347'  # Backing for the original white monochrome brand marks.

PALETTES = {
    'dark': dict(bg='#0d1117', panel='#161c26', line='#303b4c', text='#ecf1fa',
                 muted='#adb9cc', accent='#81d8d0', art='#c2b4ff', green='#81d8d0'),
    'light': dict(bg='#f8f9fd', panel='#eef1f8', line='#d4dbe8', text='#202b40',
                  muted='#52627b', accent='#146b68', art='#6750a4', green='#146b68'),
}


def label(value, x, y, color, size=16, weight=400, mono=False, anchor='start'):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="{MONO if mono else SANS}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')


def paragraph(value, x, y, width, t, size=18, leading=27):
    lines = textwrap.wrap(value, width, break_long_words=False)
    return ''.join(label(line, x, y + i * leading, t['muted'], size) for i, line in enumerate(lines))


def canvas(w, h, title, desc, t):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
            f'<rect width="{w}" height="{h}" rx="12" fill="{t["bg"]}"/>']


def hero(data, t, rows, typewriter, mobile=False, tablet=False):
    w, h = (600 if tablet else 360, 640) if mobile else (980, 460)
    p = canvas(w, h, data['subject'], ' '.join(data['intro']), t)
    if mobile:
        p += [label(data['subject'], 24, 32, t['text'], 18, 600),
              label(data['role'], 24, 55, t['muted'], 14),
              label('From everyday friction', 24, 103, t['text'], 28, 600),
              label('to something useful.', 24, 138, t['text'], 28, 600)]
        p.append(f'<rect x="20" y="166" width="{w-40}" height="230" rx="6" fill="{t["panel"]}"/>')
        scale = .8 if tablet else .7
        offset_x, offset_y = w/2-244*scale, 190-216*scale
        p.append(f'<g transform="translate({offset_x},{offset_y}) scale({scale})">'+typewriter(rows,t)+'</g>')
        y = 440
        for value in data['intro'][1:]:
            measure, size, leading = (42,24,32) if tablet else (29,20,28)
            lines = textwrap.wrap(value, measure)
            p.append(paragraph(value, 24, y, measure, t, size, leading))
            y += len(lines) * leading + 16
    else:
        p.append(f'<rect x="24" y="24" width="392" height="412" rx="8" fill="{t["panel"]}"/>')
        p += [label('eden / profile', 48, 58, t['muted'], 12, mono=True),
              '<g transform="translate(-24,-68)">'+typewriter(rows,t)+'</g>',
              label(data['subject'], 460, 63, t['text'], 20, 600),
              label(data['role'], 460, 90, t['muted'], 16),
              label('From everyday friction', 460, 170, t['text'], 38, 600),
              label('to something useful.', 460, 216, t['text'], 38, 600)]
        y = 280
        for value in data['intro'][1:]:
            lines = textwrap.wrap(value, 47)
            p.append(paragraph(value, 460, y, 47, t, 19, 28))
            y += len(lines) * 28 + 16
    p.append('</svg>')
    return ''.join(p)


def sketch(kind, x, y, t, scale=1):
    p = [f'<g transform="translate({x},{y}) scale({scale})" fill="none" stroke="{t["art"]}" stroke-width="2" stroke-linejoin="round">']
    if kind == 0:
        p.append('<path d="M0 18h26v22H0zM70 0h28v22H70zM130 43h26v22h-26zM22 68h30v22H22zM26 29 70 11M84 22l46 32M52 79l78-25"/>')
        p.append(f'<circle cx="84" cy="11" r="29" stroke="{t["accent"]}"/><path d="m105 32 23 23" stroke="{t["accent"]}"/>')
    elif kind == 1:
        p.append('<path d="M0 34h36v26H0zM72 0h42v26H72zM72 68h42v26H72zM36 47h18V13h18M54 47v34h18M114 13h36v68h-36"/>')
        p.append(f'<path d="M8 47h20M80 13h26M80 81h26" stroke="{t["accent"]}"/>')
    else:
        p.append('<rect x="0" y="0" width="126" height="84" rx="4"/><path d="M0 20h126M9 10h4m6 0h4m6 0h4M14 34h40v36H14zM66 36h43M66 48h34M66 60h24"/>')
        p.append(f'<path d="m104 64 4 30 9-9 14-1zM147 14V0h-14M147 0c26 22 25 60-2 83" stroke="{t["accent"]}"/>')
    return ''.join(p) + '</g>'


def approach(data, t, mobile=False, tablet=False):
    items = data['experience']
    desc = ' '.join(item['name']+': '+item['description'] for item in items)
    measure, size, leading = (42,24,34) if tablet else (28,20,30)
    row_heights = [len(textwrap.wrap(item['description'],measure))*leading+100 for item in items]
    w, h = (600 if tablet else 360, 100+sum(row_heights)) if mobile else (980, 460)
    p = canvas(w, h, 'How an idea takes shape', desc, t)
    p.append(label('How an idea takes shape', 24 if mobile else 32, 42, t['text'], 24, 600))
    if not mobile:
        p.append(f'<path d="M48 92H932" stroke="{t["line"]}"/>')
    for i, item in enumerate(items):
        x, y = (24, 100+sum(row_heights[:i])) if mobile else (32+i*316, 92)
        if mobile:
            p.append(f'<path d="M24 {y-22}H{w-24}" stroke="{t["line"]}"/>')
            p.append(sketch(i, w-76, y-12, t, .28))
            p.append(label(item['name'], x, y+20, t['text'], 21, 600))
            p.append(paragraph(item['description'], x, y+58, measure, t, size, leading))
        else:
            p.append(f'<circle cx="{x+8}" cy="{y}" r="5" fill="{t["accent"]}"/>')
            p.append(sketch(i, x+24, y+38, t, .72))
            p.append(label(item['name'], x, y+154, t['text'], 23, 600))
            p.append(paragraph(item['description'], x, y+187, 27, t, 20, 29))
    p.append('</svg>')
    return ''.join(p)


def perspective(data, t, mobile=False, tablet=False):
    desc = 'Planning connects user needs, business priorities and technical feasibility. Design background: '+', '.join(data['background'])+'.'
    w = (600 if tablet else 360) if mobile else 980
    p = canvas(w, 568 if mobile else 290, 'A design perspective', desc, t)
    # Two related diagrams share one canvas instead of competing full-width cards.
    if mobile:
        centers, origins = [(w/2, 152), (w/2, 416)], [(24, 36), (24, 310)]
        p.append(f'<path d="M24 278H{w-24}" stroke="{t["line"]}"/>')
    else:
        centers, origins = [(242, 152), (734, 152)], [(32, 36), (524, 36)]
        p.append(f'<path d="M490 32V258" stroke="{t["line"]}"/>')
    x, y = origins[0]
    p.append(label('A shared plan', x, y, t['text'], 22, 600))
    cx, cy = centers[0]
    points = [(cx,cy-55,'People','Needs'),(cx-104,cy+53,'Purpose','Priorities'),(cx+104,cy+53,'Practice','Feasibility')]
    p.append(f'<path d="M{cx} {cy-55} {cx-104} {cy+53}H{cx+104}Z" stroke="{t["line"]}" fill="none"/>')
    for i,(nx,ny,word,caption) in enumerate(points):
        p.append(f'<path d="M{cx} {cy+8}L{nx} {ny}" stroke="{t["art"]}"/>')
        p.append(f'<circle cx="{nx}" cy="{ny}" r="4" fill="{t["accent"]}"/>')
        # Keep captions outside the triangle so its edges do not cross text.
        title_y, caption_y = (ny-36,ny-15) if i == 0 else (ny+25,ny+45)
        p += [label(word,nx,title_y,t['text'],18 if mobile else 16,600,anchor='middle'),label(caption,nx,caption_y,t['muted'],16 if mobile else 14,anchor='middle')]
    p.append(f'<rect x="{cx-45}" y="{cy-7}" width="90" height="29" rx="4" fill="{t["panel"]}"/>')
    p.append(label('Decisions',cx,cy+13,t['text'],14,anchor='middle'))
    x,y = origins[1]
    p.append(label('Where I started', x, y, t['text'], 22, 600))
    cx,cy = centers[1]
    p.append(f'<path d="M{cx-104} {cy}H{cx+104}" stroke="{t["line"]}"/>')
    for j,(title,words) in enumerate([('Form',['Industrial','design']),('Material',['Metalwork']),('Space',['Exhibition','planning'])]):
        nx = cx-104+j*104
        p.append(label(title,nx,cy-45,t['muted'],14,anchor='middle'))
        p.append(f'<circle cx="{nx}" cy="{cy}" r="24" fill="{t["panel"]}" stroke="{t["art"]}"/>')
        shape = ['M-11-6 0-12 11-6v13L0 13-11 7zM-11-6 0 0 11-6M0 0v13',
                 'M-12-11h24v8h-24zM-3-3h6v18h-6z',
                 'M-14-10-5-14v25l-9 4zM-2-14h8v25h-8zM9-14l8 4v25l-8-4z'][j]
        p.append(f'<path transform="translate({nx},{cy})" d="{shape}" fill="none" stroke="{t["art"]}" stroke-width="1.5"/>')
        for k,word in enumerate(words):
            p.append(label(word,nx,cy+46+k*19,t['text'],14,anchor='middle'))
    p.append('</svg>')
    return ''.join(p)


def profile_graphics(data, rows, typewriter):
    output = {}
    for theme, t in PALETTES.items():
        for variant in ('', '-mobile', '-tablet'):
            mobile, tablet = bool(variant), variant == '-tablet'
            suffix = variant+'-'+theme+'.svg'
            output['assets/banner'+suffix] = hero(data,t,rows,typewriter,mobile,tablet)
            output['assets/banner-static'+suffix] = hero(data,t,rows,static_portrait,mobile,tablet)
            output['assets/experience'+suffix] = approach(data,t,mobile,tablet)
            output['assets/perspective'+suffix] = perspective(data,t,mobile,tablet)
            output['assets/toolkit'+suffix] = toolkit(data,t,mobile,tablet)
    return output


def toolkit(data, t, mobile=False, tablet=False):
    w = (600 if tablet else 360) if mobile else 980
    tools = data['tools']
    cols = 2 if mobile else 3
    row_count = (len(tools)+cols-1)//cols
    description = ', '.join(tool.get('accessible_name',tool['name']) for tool in tools)+'.'
    p = canvas(w, 64+row_count*52, 'Tools I work with', description,t)
    p.append(label('Tools I work with',24 if mobile else 32,34,t['muted'],18))
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('',ns)
    cell_w = (w-48)/cols if mobile else (w-64)/cols
    start_x = 24 if mobile else 32
    assets = Path(__file__).resolve().parents[1]/'assets'
    for i,tool in enumerate(tools):
        name,title = tool['key'],tool['name']
        x, y = start_x+(i%cols)*cell_w, 72+(i//cols)*52
        p.append(f'<rect x="{x}" y="{y-4}" width="32" height="32" rx="5" fill="{t["panel"] if name == "aws" else ICON_SURFACE}"/>')
        if (assets/f'icons/{name}.svg').exists():
            icon = ET.parse(assets/f'icons/{name}.svg').getroot()
            if name == 'aws':
                p.append(f'<rect x="{x+2}" y="{y-2}" width="28" height="28" rx="3" fill="#fff"/>')
        else:
            badge = ET.parse(assets/f'badge-{name}.svg').getroot()
            icon = badge.find('.//{'+ns+'}svg')
        if icon is None:
            raise ValueError(f'Missing icon for {name}')
        icon.attrib.update(x=str(x+3),y=str(y-1),width='26',height='26')
        p.append(ET.tostring(icon,encoding='unicode'))
        lines = textwrap.wrap(title,12 if mobile else 26,break_long_words=False)
        for j,line in enumerate(lines):
            p.append(label(line,x+42,y+(8 if len(lines)>1 else 17)+j*21,t['text'],18,600))
    p.append('</svg>')
    return ''.join(p)


def static_portrait(rows, t):
    """A complete frame selected by the parent picture for reduced motion."""
    p = [f'<g fill="{t["art"]}" font-family="{MONO}" font-size="5" xml:space="preserve">']
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        runs = ''.join(f'<tspan x="{64+m.start()*3}">{escape(m[0])}</tspan>' for m in re.finditer(r'[^ ]+',line))
        p.append(f'<text y="{151+i*5}">{runs}</text>')
    return ''.join(p)+'</g>'
