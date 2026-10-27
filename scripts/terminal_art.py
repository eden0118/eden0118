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
    # A separate static group avoids dependence on animated clip geometry when
    # embedded-image renderers evaluate reduced-motion preferences.
    css.append('.ascii-static{display:none}@media(prefers-reduced-motion:reduce){.ascii-static{display:inline}.ascii-animated{display:none}}')
    p = ['<style>' + ''.join(css) + '</style><defs>' + ''.join(clips) + '</defs>',
         f'<g class="ascii-animated" fill="{t["art"]}" font-family="{FONT}" font-size="5" xml:space="preserve">']
    for i, line in visible:
        runs = ''.join(f'<tspan x="{64 + match.start()*3}">{escape(match[0])}</tspan>' for match in re.finditer(r'[^ ]+', line))
        p.append(f'<text y="{151+i*5}" clip-path="url(#row-{i})">{runs}</text>')
    p += ['</g>', f'<g class="ascii-static" fill="{t["art"]}" font-family="{FONT}" font-size="5" xml:space="preserve">']
    for i, line in visible:
        runs = ''.join(f'<tspan x="{64 + match.start()*3}">{escape(match[0])}</tspan>' for match in re.finditer(r'[^ ]+', line))
        p.append(f'<text y="{151+i*5}">{runs}</text>')
    p += ['</g>', f'<rect class="typing-cursor" x="64" y="146" width="2" height="6" fill="{t["accent"]}" opacity="0" aria-hidden="true"/>']
    return ''.join(p)


def signals(data, t):
    p=start(480, 300, 'Where planning connects', 'User needs, business priorities and technical feasibility inform shared planning decisions.', t)
    p.append(text('where planning connects',24,32,t['accent'],16,weight='600'))
    nodes=[(240,88,'People','Needs & context'),(104,220,'Purpose','Priorities & scope'),(376,220,'Practice','Feasibility')]
    p.append(f'<path d="M240 88 104 220H376Z" fill="{t["art"]}" fill-opacity=".04" stroke="{t["line"]}"/>')
    for x,y,label,caption in nodes:
        p.append(f'<path d="M240 158L{x} {y}" stroke="{t["accent"]}" stroke-dasharray="3 5"/>')
        p.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{t["art"]}"/>')
        p += [text(label,x,y-14,t['text'],14,'middle',weight='600'),text(caption,x,y+23,t['muted'],11,'middle')]
    p.append(f'<rect x="185" y="139" width="110" height="36" rx="4" fill="{t["panel"]}" stroke="{t["art"]}"/>')
    p += [text('Decisions',240,162,t['text'],13,'middle'),text('Users / Business / Engineering',240,280,t['muted'],12,'middle'), '</svg>']
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


def graphics():
    data=json.loads((ROOT/'assets/profile.json').read_text())
    from profile_layout import profile_graphics
    output = {f'assets/{name}-{theme}.svg': render(data,t) for theme,t in THEMES.items() for name,render in [('signals',signals),('roots',roots),('stats',stats)]}
    output.update(profile_graphics(data, ascii_portrait(), typewriter))
    return output


if __name__ == '__main__':
    for name,content in graphics().items():
        (ROOT/name).write_text(content)
    print('Generated terminal banner, practice map, design roots and public statistics')
