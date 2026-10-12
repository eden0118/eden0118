"""Original terminal-profile graphics, with a real ASCII character portrait."""
from pathlib import Path
from html import escape
import json
import math
import re
from PIL import Image, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONT = 'ui-monospace,SFMono-Regular,Consolas,Liberation Mono,monospace'
THEMES = {
    'dark': dict(bg='#090f1c', panel='#0e192b', line='#26384f', text='#dde7f5', muted='#8e9eb5', accent='#22d3ee', art='#a99aee', green='#10b981'),
    'light': dict(bg='#f5f7fc', panel='#ffffff', line='#d0dae8', text='#172539', muted='#52647b', accent='#08788c', art='#6750a4', green='#087657'),
}


def text(value, x, y, color, size=14, anchor='start', weight='400', extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'


def start(width, height, title, desc, t):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
            f'<rect width="{width}" height="{height}" rx="16" fill="{t["bg"]}"/>']


def ascii_portrait():
    image = Image.open(ROOT / 'assets/design.png').convert('RGB')
    bounds = ImageChops.difference(image, Image.new('RGB', image.size, 'white')).convert('L').point(lambda v: 255 if v > 35 else 0).getbbox()
    if bounds:
        image = image.crop(bounds)
    # Correct for the non-square cells of a monospace glyph.
    image = ImageOps.pad(image.convert('L'), (360, 380), color='white').resize((120, 76), Image.Resampling.LANCZOS)
    ramp = ' .:-=+*#%@'
    return [''.join(ramp[round((255 - image.getpixel((x, y))) / 255 * (len(ramp) - 1))] for x in range(120)) for y in range(76)]


def banner(data, t):
    p = start(1180, 610, 'Eden Chang · profile.sh --live', 'Terminal profile with an ASCII character drawing at a desk, and information about Eden Chang, Technical Product Manager.', t)
    p += [f'<rect x="14" y="14" width="1152" height="582" rx="14" fill="{t["panel"]}" stroke="{t["line"]}"/>',
          f'<path d="M14 62H1166" stroke="{t["line"]}"/>']
    for x, color in [(38, '#ff5f57'), (59, '#febc2e'), (80, '#28c840')]:
        p.append(f'<circle cx="{x}" cy="38" r="6" fill="{color}"/>')
    p.append(text('profile.sh --live', 590, 43, t['muted'], 13, 'middle'))
    for x, w, heading in [(34, 420, 'VISUAL.MAP'), (474, 672, 'SYSTEM.INFO')]:
        p += [f'<rect x="{x}" y="88" width="{w}" height="474" rx="6" fill="none" stroke="{t["line"]}"/>',
              f'<path d="M{x} 124h{w}" stroke="{t["line"]}"/>', text(heading, x+16, 111, t['accent'], 13, weight='700')]
    p += [text('ASCII / 120x76', 437, 111, t['muted'], 11, 'end'), text('@'+data['handle'], 1128, 111, t['accent'], 13, 'end')]
    p.append(f'<g fill="{t["art"]}" font-family="{FONT}" font-size="5" xml:space="preserve">')
    for i, line in enumerate(ascii_portrait()):
        runs = ''.join(f'<tspan x="{64 + match.start()*3}">{escape(match[0])}</tspan>' for match in re.finditer(r'[^ ]+', line))
        p.append(f'<text y="{151+i*5}">{runs}</text>')
    p += ['</g>', f'<path d="M49 150v-12h12M427 138h12v12M49 521v12h12M427 533h12v-12" fill="none" stroke="{t["accent"]}"/>', text('CHARACTER / ASCII DENSITY MAP', 58, 550, t['muted'], 10)]
    fields = [('Subject',data['subject']), ('Role',data['role']), ('Background.01', data['background'][0]), ('Background.02', data['background'][1]), ('Background.03',data['background'][2]), ('Practice.01',data['practice'][0]), ('Practice.02',data['practice'][1]), ('Practice.03',data['practice'][2]), ('Practice.04',data['practice'][3]), ('Perspective.01','Users'), ('Perspective.02','Business'), ('Perspective.03','Engineering'), ('Grid.GitHub',data['handle']), ('Status','Curious builder')]
    for i, (key, value) in enumerate(fields):
        y = 153+i*24
        p += [text(key, 491, y, t['muted']), f'<path d="M628 {y-4}H{1116-len(value)*8.5}" stroke="{t["line"]}" stroke-dasharray="1 4"/>', text(value, 1128, y, t['text'], anchor='end')]
    p += [f'<path d="M491 524H1128" stroke="{t["line"]}"/>',text('● BUILDING / LEARNING / EXPLORING',491,548,t['green'],11), text('PRODUCT DEVELOPMENT',1128,548,t['muted'],11,'end'), '</svg>']
    return ''.join(p)


def signals(data, t):
    p=start(480, 300, 'Working practice', 'Planning, user experience, collaboration and front-end connect users, business and engineering.', t)
    p.append(text('working practice',24,32,t['accent'],16,weight='600'))
    nodes=[(134,87,'Planning'),(351,87,'User experience'),(351,221,'Front-end'),(134,221,'Collaboration')]
    for x,y,_ in nodes:
        p.append(f'<path d="M240 153L{x} {y}" stroke="{t["line"]}"/>')
    p.append(f'<circle cx="240" cy="153" r="38" fill="{t["panel"]}" stroke="{t["art"]}"/>')
    p.append(text('Product',240,158,t['text'],13,'middle'))
    for x,y,label in nodes:
        p.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{t["art"]}"/>')
        p.append(text(label,x,y-16,t['text'],12,'middle'))
    p += [text('Users / Business / Engineering',240,280,t['muted'],12,'middle'), '</svg>']
    return ''.join(p)


def languages(data,t):
    counts=data['stats']['languages']
    p=start(480,300,'Repository languages','Primary languages across non-fork public repositories: '+', '.join(f'{k}: {v}' for k,v in counts.items()),t)
    p.append(text('repository languages',24,32,t['accent'],16,weight='600'))
    top=sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:3]
    coords=[]
    maxval=max(v for _,v in top)
    for scale in (.25,.5,.75,1):
        vertices=[(240+90*scale*math.cos(-math.pi/2+i*2*math.pi/3),159+90*scale*math.sin(-math.pi/2+i*2*math.pi/3)) for i in range(3)]
        p.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in vertices)+f'" fill="none" stroke="{t["line"]}"/>')
    for i,(label,count) in enumerate(top):
        angle=-math.pi/2+i*2*math.pi/3
        x,y=240+90*math.cos(angle),159+90*math.sin(angle)
        coords.append((240+90*count/maxval*math.cos(angle),159+90*count/maxval*math.sin(angle)))
        p.append(f'<path d="M240 159L{x:.2f} {y:.2f}" stroke="{t["line"]}"/>')
        lx,ly=240+123*math.cos(angle),159+112*math.sin(angle)
        p.append(text(f'{label} ({count})',round(lx),round(ly),t['text'],12,'middle'))
    p.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)+f'" fill="{t["art"]}" fill-opacity=".18" stroke="{t["art"]}" stroke-width="2"/>')
    p += [text('Primary language / non-fork public repos',240,280,t['muted'],11,'middle'), '</svg>']
    return ''.join(p)


def stats(data,t):
    s=data['stats']
    p=start(680,180,'GitHub public statistics',f'As of {s["as_of"]}: {s["public_repos"]} public repositories, {s["stars"]} stars on non-fork public repositories, {s["followers"]} followers, {s["following"]} following.',t)
    p.append(text('github / @'+data['handle'],24,32,t['accent'],15,weight='600'))
    for i,(label,key) in enumerate([('Public repos','public_repos'),('Stars','stars'),('Followers','followers'),('Following','following')]):
        x=26+i*167
        p += [text(s[key],x,92,t['art'],32,weight='600'),text(label,x,118,t['muted'],12)]
    p += [text('Public snapshot / '+s['as_of'],24,158,t['muted'],11),'</svg>']
    return ''.join(p)


def graphics():
    data=json.loads((ROOT/'assets/profile.json').read_text())
    return {f'assets/{name}-{theme}.svg': render(data,t) for theme,t in THEMES.items() for name,render in [('banner',banner),('signals',signals),('languages',languages),('stats',stats)]}


if __name__ == '__main__':
    for name,content in graphics().items():
        (ROOT/name).write_text(content)
    print('Generated terminal banner, practice map, language radar and public statistics')
