#!/usr/bin/env python3
"""Generate GitHub profile SVGs from public contributions and a local portrait."""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import random
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, ACCENT = "#18181b", "#46515f", "#2563eb"
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.tooltips = {}, {}
        self.tooltip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and attrs.get("data-date"):
            self.cells[attrs["id"]] = dict(date=attrs["data-date"], level=int(attrs.get("data-level", 0)))
        if tag == "tool-tip":
            self.tooltip = attrs.get("for")
            if self.tooltip:
                self.tooltips[self.tooltip] = ""

    def handle_data(self, data):
        if self.tooltip:
            self.tooltips[self.tooltip] += data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.tooltip = None

    def days(self):
        days = []
        for key, cell in self.cells.items():
            label = self.tooltips.get(key, "").strip()
            match = re.match(r"([\d,]+) contributions?\b", label, re.I)
            if not match and not label.lower().startswith("no contributions"):
                raise ValueError(f"Cannot read contribution count: {cell['date']}: {label!r}")
            days.append({**cell, "count": int(match[1].replace(",", "")) if match else 0})
        days.sort(key=lambda day: day["date"])
        if len(days) < 350:
            raise ValueError("Incomplete contribution calendar; keeping existing assets")
        for left, right in zip(days, days[1:]):
            if dt.date.fromisoformat(right["date"]) - dt.date.fromisoformat(left["date"]) != dt.timedelta(days=1):
                raise ValueError("Contribution calendar has gaps")
        return days


def summarize(days):
    active = sum(day["count"] > 0 for day in days)
    total = sum(day["count"] for day in days)
    longest = run = 0
    monthly = {}
    for day in days:
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)
        month = day["date"][:7]
        monthly[month] = monthly.get(month, 0) + day["count"]
    index = len(days) - 1
    # Allow today to finish, but do not forgive a past inactive day.
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    if days[index]["date"] == today and not days[index]["count"]:
        index -= 1
    current = 0
    while index >= 0 and days[index]["count"]:
        current += 1
        index -= 1
    return dict(total=total, active=active, longest=longest, current=current,
                best=max(day["count"] for day in days),
                average=round(total / active, 1) if active else 0, monthly=monthly)


def text(x, y, content, size=16, fill=INK, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{html.escape(str(content))}</text>'


def frame(width, height, title, description):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}" role="img">',
            f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>',
            '<style>.reveal{animation:reveal .6s ease-out both}@keyframes reveal{from{opacity:0}to{opacity:1}}'
            '@media(prefers-reduced-motion:reduce){.reveal{animation:none}.portrait-row{clip-path:none}}</style>',
            f'<rect width="{width}" height="{height}" fill="#fafafa"/>',
            text(24, 30, title, 18, INK)]


def heatmap(days, stats):
    start = dt.date.fromisoformat(days[0]["date"])
    offset = (start.weekday() + 1) % 7
    cols = (len(days) + offset + 6) // 7
    width = max(860, 60 + cols * 15)
    parts = frame(width, 228, "Activity / last year", "Daily contributions over the last year")
    palette = ["#e8ecf0", "#bcd0fa", "#7ea4ef", "#487adb", "#2563eb"]
    seen = set()
    for i, day in enumerate(days):
        col, row = divmod(i + offset, 7)
        date = dt.date.fromisoformat(day["date"])
        if day["date"][:7] not in seen:
            seen.add(day["date"][:7])
            parts.append(text(49 + col * 15, 60, date.strftime("%b"), 10, MUTED))
        parts.append(f'<rect class="reveal" x="{49+col*15}" y="{73+row*15}" width="11" height="11" rx="2" fill="{palette[day["level"]]}" style="animation-delay:{col*.024+row*.035:.3f}s"><title>{day["date"]}: {day["count"]} contributions</title></rect>')
    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        parts.append(text(14, 82 + row * 15, label, 10, MUTED))
    parts.append(text(24, 207, f"{stats['total']:,} contributions in the last year", 14, ACCENT))
    parts.append(text(width - 24, 207, f"{days[0]['date']} / {days[-1]['date']}", 11, MUTED, 'text-anchor="end"'))
    return "".join(parts) + "</svg>"


def stats_card(days, stats):
    parts = frame(860, 430, "Activity / in numbers", "Contribution statistics and monthly totals")
    metrics = [("Current streak", f"{stats['current']} days"),
               ("Longest streak", f"{stats['longest']} days"),
               ("Contributions", f"{stats['total']:,}"),
               ("Active days", f"{stats['active']} / {len(days)}"),
               ("Best day", f"{stats['best']:,}"),
               ("Average per active day", stats["average"])]
    for i, (label, value) in enumerate(metrics):
        x, y = 24 + (i % 3) * 280, 72 + (i // 3) * 90
        parts.extend([text(x, y, label, 16, MUTED), text(x, y + 38, value, 32, INK)])
    parts.append('<path d="M24 228H836" stroke="#dce0e5"/>')
    parts.append(text(24, 260, "Monthly contributions", 16, MUTED))
    monthly = list(stats["monthly"].items())
    peak = max(value for _, value in monthly) or 1
    slot = 812 / len(monthly)
    for i, (month, value) in enumerate(monthly):
        x, height = 24 + i * slot + 8, 90 * value / peak
        parts.append(f'<rect x="{x:.1f}" y="{365-height:.1f}" width="{slot-16:.1f}" height="{height:.1f}" fill="{ACCENT}"/>')
        parts.append(text(x + (slot - 16) / 2, 387, dt.date.fromisoformat(month + "-01").strftime("%b"), 13, MUTED, 'text-anchor="middle"'))
    parts.append(text(24, 415, "Source: public GitHub contribution calendar", 13, MUTED))
    return "".join(parts) + "</svg>"


def ascii_lines(source, cols=100, rows=96):
    from PIL import Image, ImageChops, ImageEnhance, ImageOps
    image = Image.open(source).convert("RGB")
    if source.name == "working.png":
        # The bottom caption sits below the illustration in this source image.
        image = image.crop((0, 0, image.width, round(image.height * .84)))
    difference = ImageChops.difference(image, Image.new("RGB", image.size, "white"))
    bounds = difference.convert("L").point(lambda value: 255 if value > 35 else 0).getbbox()
    if bounds:
        x0, y0, x1, y1 = bounds
        margin = round(max(x1 - x0, y1 - y0) * .035)
        image = image.crop((max(0, x0 - margin), max(0, y0 - margin),
                            min(image.width, x1 + margin), min(image.height, y1 + margin)))
    # Pad rather than crop so each illustration keeps its full composition.
    image = ImageOps.pad(image.convert("L"), (cols, rows), color="white")
    image = ImageEnhance.Contrast(image).enhance(1.2)
    ramp = " .:-=+*#"
    return ["".join(ramp[round((255 - image.getpixel((col, row))) / 255 * (len(ramp) - 1))]
                    for col in range(cols)) for row in range(rows)]


def portrait(sources, dark=False):
    cols, rows = 100, 96
    ramp = " .:-=+*#"
    frames, interval, hold = 24, .15, 3.4
    typing = frames * interval
    slide_duration = typing + hold
    cycle = len(sources) * slide_duration
    background, ink = ("#0d1117", "#b7cdc8") if dark else ("#fafafa", "#30383b")
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="840" height="800" viewBox="0 0 840 800" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" role="img">',
             '<title>Eden / ASCII illustration carousel</title>',
             '<desc>Designing, needing sleep, working, and drinking bubble tea, rotating with a character typing effect.</desc>',
             '<style>@media(prefers-reduced-motion:reduce){.carousel-frame{display:none!important}.portrait-fallback{display:inline!important;opacity:1!important}}</style>',
             f'<rect width="840" height="800" fill="{background}"/>']
    step = 736 / rows

    def render_lines(lines):
        return "".join(text(24, round(32 + row * step, 2), line, 10.2, ink,
                            'xml:space="preserve" textLength="792" lengthAdjust="spacingAndGlyphs"')
                       for row, line in enumerate(lines))

    def active_window(start, end):
        # All groups share one repeating clock, avoiding drift after each loop.
        if start == 0:
            values, times = "1;0;0", f"0;{end / cycle:.8f};1"
        elif end == cycle:
            values, times = "0;1;1", f"0;{start / cycle:.8f};1"
        else:
            values, times = "0;1;0;0", f"0;{start / cycle:.8f};{end / cycle:.8f};1"
        return f'<animate attributeName="opacity" values="{values}" keyTimes="{times}" calcMode="discrete" dur="{cycle:.2f}s" repeatCount="indefinite"/>'

    for slide, source in enumerate(sources):
        lines = ascii_lines(source, cols, rows)
        rng = random.Random(18 + slide)
        timing = [[(rng.uniform(0, .38), rng.uniform(.42, .98)) for _ in range(cols)]
                  for _ in range(rows)]
        offset = slide * slide_duration
        fallback = slide == 0
        classes = "carousel-frame portrait-fallback" if fallback else "carousel-frame"
        parts.append(f'<g class="{classes}" opacity="{1 if fallback else 0}" data-scene="{html.escape(source.stem)}" data-phase="hold">')
        parts.append(active_window(offset + typing, (slide + 1) * slide_duration))
        parts.append(render_lines(lines))
        parts.append('</g>')
        for frame in range(frames):
            progress = (frame + 1) / frames
            frame_lines = []
            for row, line in enumerate(lines):
                chars = []
                for col, target in enumerate(line):
                    arrival, settled = timing[row][col]
                    if target == " " or progress < arrival:
                        chars.append(" ")
                    elif progress >= settled:
                        chars.append(target)
                    else:
                        index = ramp.index(target)
                        variants = ramp[max(1, index - 2):min(len(ramp), index + 3)]
                        chars.append(rng.choice(variants))
                frame_lines.append("".join(chars))
            parts.append(f'<g class="carousel-frame" opacity="0" data-scene="{html.escape(source.stem)}" data-phase="typing" data-frame="{frame}">')
            parts.append(active_window(offset + frame * interval, offset + (frame + 1) * interval))
            parts.append(render_lines(frame_lines))
            parts.append('</g>')
    return "".join(parts) + "</svg>"


def dark_variant(svg):
    """Recolor the shared artwork without changing layout or animation timing."""
    palette = {
        "#fafafa": "#0d1117", "#18181b": "#e6edf3",
        "#46515f": "#a6b2c0", "#2563eb": "#8db1ff",
        "#dce0e5": "#30363d", "#929ba8": "#8b98a8",
        "#edf2ff": "#17263d", "#f0f2f5": "#161b22",
        "#e8ecf0": "#161b22", "#bcd0fa": "#23395e",
        "#7ea4ef": "#315486", "#487adb": "#547fc0",
    }
    return re.sub(r"#[0-9a-fA-F]{6}", lambda match: palette.get(match[0].lower(), match[0]), svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="eden0118")
    parser.add_argument("--html", type=Path, help="Use a saved GitHub calendar instead of fetching")
    parser.add_argument("--portrait", type=Path, nargs="+", help="Illustrations to rotate in the ASCII carousel, in order")
    args = parser.parse_args()
    if args.html:
        calendar_html = args.html.read_text()
    else:
        request = urllib.request.Request(f"https://github.com/users/{args.username}/contributions", headers={"User-Agent": "eden-profile-art"})
        with urllib.request.urlopen(request, timeout=30) as response:
            calendar_html = response.read().decode()
    calendar = CalendarParser()
    calendar.feed(calendar_html)
    days = calendar.days()
    stats = summarize(days)
    outputs = {"assets/contributions.svg": heatmap(days, stats), "assets/stats.svg": stats_card(days, stats),
               "data/contributions.json": json.dumps(dict(username=args.username, days=days, stats=stats), indent=2) + "\n"}
    if args.portrait:
        character = portrait(args.portrait)
        outputs["assets/portrait.svg"] = character
        template = (ROOT / "scripts/design-cover-template.svg").read_text()
        # The outer SVG supplies the scaled viewport; keep the portrait's content.
        content = character[character.index(">") + 1:character.rindex("</svg>")]
        outputs["assets/design-cover.svg"] = template.replace("{PORTRAIT}", content)
        colored = portrait(args.portrait, dark=True)
        outputs["assets/portrait-dark.svg"] = colored
        content = colored[colored.index(">") + 1:colored.rindex("</svg>")]
        outputs["assets/design-cover-dark.svg"] = dark_variant(template).replace("{PORTRAIT}", content)
    for name in ("design-practice", "contributions", "stats"):
        light_path = f"assets/{name}.svg"
        light_svg = outputs.get(light_path)
        if light_svg is None:
            light_svg = (ROOT / light_path).read_text()
        outputs[f"assets/{name}-dark.svg"] = dark_variant(light_svg)
    for path, content in outputs.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    print(f"Generated profile art: {len(days)} days, {stats['total']:,} contributions")


if __name__ == "__main__":
    main()
