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


def typewriter(rows, t):
    """Reveal each nonempty ASCII row from left to right, then hold the portrait."""
    visible = [(i, line) for i, line in enumerate(rows) if line.strip()]
    duration, delay, typing = 10, .5, 3.5
    interval = typing / len(visible)
    css, clips, cursor = [], [], ['0%,4.99%{opacity:0;transform:translate(0,0)}']
    for n, (i, _) in enumerate(visible):
        begin = (delay + n * interval) / duration * 100
        end = (delay + (n + 1) * interval) / duration * 100
        css.append(f'@keyframes row-{i}{{0%,{begin:.4f}%{{width:0}}{end:.4f}%,99.99%{{width:360px}}100%{{width:0}}}}')
        clips.append(f'<clipPath id="row-{i}"><rect class="type-mask" x="64" y="{145+i*5}" width="360" height="7" style="animation-name:row-{i}"/></clipPath>')
        cursor += [f'{begin:.4f}%{{opacity:1;transform:translate(0,{i*5}px)}}',
                   f'{end-.0001:.4f}%{{opacity:1;transform:translate(360px,{i*5}px)}}']
    cursor.append('40%,100%{opacity:0;transform:translate(0,0)}')
    css += [f'.type-mask{{animation-duration:{duration}s;animation-timing-function:steps(120,end);animation-iteration-count:infinite}}',
            '@keyframes typing-cursor{' + ''.join(cursor) + '}',
            f'.typing-cursor{{animation:typing-cursor {duration}s steps(120,end) infinite}}',
            '@media(prefers-reduced-motion:reduce){.type-mask{animation:none;width:360px}.typing-cursor{display:none}}']
    p = ['<style>' + ''.join(css) + '</style><defs>' + ''.join(clips) + '</defs>',
         f'<g fill="{t["art"]}" font-family="{FONT}" font-size="5" xml:space="preserve">']
    for i, line in visible:
        runs = ''.join(f'<tspan x="{64 + match.start()*3}">{escape(match[0])}</tspan>' for match in re.finditer(r'[^ ]+', line))
        p.append(f'<text y="{151+i*5}" clip-path="url(#row-{i})">{runs}</text>')
    p += ['</g>', f'<rect class="typing-cursor" x="64" y="146" width="2" height="6" fill="{t["accent"]}" opacity="0" aria-hidden="true"/>']
    return ''.join(p)


def banner(data, t):
    description = ' '.join(data['intro']) + ' How I work: ' + ' '.join(f'{item["name"]}: {item["description"]}' for item in data['strengths'])
    p = start(1180, 610, 'Eden Chang · profile.sh --live', description, t)
    p += [f'<rect x="14" y="14" width="1152" height="582" rx="14" fill="{t["panel"]}" stroke="{t["line"]}"/>',
          f'<path d="M14 62H1166" stroke="{t["line"]}"/>']
    for x, color in [(38, '#ff5f57'), (59, '#febc2e'), (80, '#28c840')]:
        p.append(f'<circle cx="{x}" cy="38" r="6" fill="{color}"/>')
    p.append(text('profile.sh --live', 590, 43, t['muted'], 13, 'middle'))
    for x, w, heading in [(34, 420, 'VISUAL.MAP'), (474, 672, 'SYSTEM.INFO')]:
        p += [f'<rect x="{x}" y="88" width="{w}" height="474" rx="6" fill="none" stroke="{t["line"]}"/>',
              f'<path d="M{x} 124h{w}" stroke="{t["line"]}"/>', text(heading, x+16, 111, t['accent'], 13, weight='700')]
    p += [text('ASCII / 120x76', 437, 111, t['muted'], 11, 'end'), text('@'+data['handle'], 1128, 111, t['accent'], 13, 'end')]
    p.append(typewriter(ascii_portrait(), t))
    p += [f'<path d="M49 150v-12h12M427 138h12v12M49 521v12h12M427 533h12v-12" fill="none" stroke="{t["accent"]}"/>', text('CHARACTER / ASCII DENSITY MAP', 58, 550, t['muted'], 10)]
    fields = [('Subject', data['subject']), ('Role', data['role'])]
    for i, (key, value) in enumerate(fields):
        y = 153+i*24
        p += [text(key, 491, y, t['muted']), f'<path d="M628 {y-4}H{1116-len(value)*8.5}" stroke="{t["line"]}" stroke-dasharray="1 4"/>', text(value, 1128, y, t['text'], anchor='end')]
    for i, line in enumerate(data['intro']):
        p.append(text(line, 491, 209+i*20, t['muted'], 13))
    p.append(f'<path d="M491 269H1128" stroke="{t["line"]}"/>')
    p.append(text('HOW I WORK', 491, 291, t['accent'], 12, weight='600'))
    for i, item in enumerate(data['strengths']):
        y = 320+i*49
        p.append(text(item['name'], 491, y, t['text'], 14, weight='600'))
        p.append(text(item['description'], 491, y+19, t['muted'], 13))
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


def roots(data, t):
    p = start(480, 300, 'Design roots', 'Eden’s background in industrial design, metalwork and exhibition planning: form, material and space.', t)
    p.append(text('design roots', 24, 32, t['accent'], 16, weight='600'))
    p.append(f'<path d="M80 150H400" stroke="{t["line"]}"/>')
    for x, label in [(80, 'Form'), (240, 'Material'), (400, 'Space')]:
        p.append(text(label, x, 88, t['muted'], 12, 'middle'))
        p.append(f'<circle cx="{x}" cy="150" r="34" fill="{t["panel"]}" stroke="{t["art"]}"/>')
    # A drafted object, a hammer, and exhibition panels describe physical practice.
    p.append(f'<g fill="none" stroke="{t["art"]}" stroke-width="1.5" stroke-linejoin="round">'
             '<path d="M62 140l18-10 18 10v20l-18 10-18-10zM62 140l18 10 18-10M80 150v20"/>'
             '<path d="M224 134h30v10h-30zM235 144h8v25h-8z"/>'
             '<path d="M380 138l12-5v32l-12 5zM395 133h12v32h-12zM410 133l12 5v32l-12-5z"/>'
             '</g>')
    for x, words in [(80, ['Industrial', 'design']), (240, ['Metalwork']), (400, ['Exhibition', 'planning'])]:
        for i, word in enumerate(words):
            p.append(text(word, x, 213+i*18, t['text'], 13, 'middle'))
    p += [text('From physical objects to digital products', 240, 280, t['muted'], 11, 'middle'), '</svg>']
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


def experience(data, t):
    items = data['experience']
    description = ' '.join(f'{item["name"]}: {item["description"]}' for item in items)
    p = start(980, 98 + len(items) * 128, 'How an idea takes shape', description, t)
    p += [text('How an idea takes shape', 32, 43, t['text'], 24, weight='600'),
          text('observe / map / explore', 32, 68, t['muted'], 12)]
    for j in range(18):
        x = 724 + j * 12
        y = 29 + (j % 3) * 10
        p.append(f'<rect x="{x}" y="{y}" width="{8 if j % 4 else 20}" height="6" fill="{t["accent"] if j % 3 else t["art"]}" opacity="{.35 + (j % 4) * .2}"/>')
    for i, item in enumerate(items):
        y = 98 + i * 128
        p.append(f'<path d="M32 {y-8}H948" stroke="{t["line"]}"/>')
        p.append(text(f'0{i+1}', 34, y + 22, t['accent'], 12))
        p.append(f'<g transform="translate(76,{y+8})" fill="none" stroke="{t["art"]}" stroke-width="1.5">')
        if i == 0:
            p.append('<path d="M0 8h24v20H0zM64 0h28v20H64zM112 36h24v20h-24zM20 56h30v20H20zM24 18l40-8M78 20l34 26M50 66l62-20"/>')
            p.append(f'<circle cx="77" cy="10" r="27" stroke="{t["accent"]}"/><path d="m96 30 18 18" stroke="{t["accent"]}"/>')
        elif i == 1:
            p.append('<path d="M0 32h32v24H0zM62 0h40v24H62zM62 64h40v24H62zM32 44h16V12h14M48 44v32h14M102 12h32v64h-32"/>')
            p.append(f'<path d="M7 44h18M70 12h24M70 76h24" stroke="{t["accent"]}"/>')
        else:
            p.append('<rect x="0" y="5" width="116" height="74" rx="4"/><path d="M0 22h116M9 13h4m5 0h4m5 0h4M12 35h42v32H12zM65 37h36M65 47h29M65 57h20"/>')
            p.append(f'<path d="m94 60 4 28 8-9 13-1zM134 20v-13h-16M134 7c24 20 22 57-4 72" fill="{t["panel"]}" stroke="{t["accent"]}"/>')
        p.append('</g>')
        p.append(text(item['name'], 264, y + 28, t['text'], 21, weight='600'))
        p.append(text(item['description'], 264, y + 55, t['muted'], 14))
        p.append(text(' / '.join(item['labels']), 264, y + 83, t['accent'], 12))
    p.append('</svg>')
    return ''.join(p)


def graphics():
    data=json.loads((ROOT/'assets/profile.json').read_text())
    return {f'assets/{name}-{theme}.svg': render(data,t) for theme,t in THEMES.items() for name,render in [('banner',banner),('signals',signals),('roots',roots),('stats',stats),('experience',experience)]}


if __name__ == '__main__':
    for name,content in graphics().items():
        (ROOT/name).write_text(content)
    print('Generated terminal banner, practice map, design roots and public statistics')
