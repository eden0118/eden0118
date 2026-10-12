#!/usr/bin/env python3
"""Generate GitHub profile SVGs from public contributions and a local portrait."""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, ACCENT = "#e6edf3", "#919da9", "#99e1d9"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


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
            f'<rect width="{width}" height="{height}" rx="12" fill="#0d1117"/>',
            f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="#30363d"/>',
            f'<path d="M0 38H{width}" stroke="#30363d"/>',
            '<circle cx="22" cy="19" r="5" fill="#ff5f56"/><circle cx="39" cy="19" r="5" fill="#ffbd2e"/><circle cx="56" cy="19" r="5" fill="#27c93f"/>',
            text(width / 2, 24, title, 12, MUTED, 'text-anchor="middle"')]


def heatmap(days, stats):
    start = dt.date.fromisoformat(days[0]["date"])
    offset = (start.weekday() + 1) % 7
    cols = (len(days) + offset + 6) // 7
    width = max(860, 60 + cols * 15)
    parts = frame(width, 228, "eden@github: ~$ ./contributions.sh", "Daily contributions over the last year")
    palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
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
    parts = frame(840, 880, "eden@github: ~$ ./stats.sh", "Contribution statistics and monthly totals")
    tiles = [("current streak", f"{stats['current']} days"), ("longest streak", f"{stats['longest']} days"),
             ("contributions", f"{stats['total']:,}"), ("active days", f"{stats['active']} / {len(days)}"),
             ("best day", f"{stats['best']:,}"), ("avg / active day", stats["average"])]
    for i, (label, value) in enumerate(tiles):
        x, y = 24 + i % 2 * 404, 66 + i // 2 * 166
        parts.append(f'<g class="reveal" style="animation-delay:{i*.12}s"><rect x="{x}" y="{y}" width="388" height="148" rx="8" fill="#161b22"/>')
        parts.extend([text(x + 22, y + 38, "$ " + label, 20, MUTED), text(x + 22, y + 101, value, 43, ACCENT if i == 0 else INK), "</g>"])
    parts.extend([text(24, 610, "$ contributions / month", 22, MUTED), text(24, 842, "Last year · public GitHub contribution calendar", 16, MUTED)])
    monthly = list(stats["monthly"].items())
    peak = max(value for _, value in monthly) or 1
    slot = 792 / len(monthly)
    for i, (month, value) in enumerate(monthly):
        x, height = 24 + i * slot + 8, 156 * value / peak
        parts.append(f'<g class="reveal" style="animation-delay:{.7+i*.05}s"><rect x="{x:.1f}" y="{782-height:.1f}" width="{slot-16:.1f}" height="{height:.1f}" rx="3" fill="{ACCENT}"/>')
        parts.extend([text(x + (slot - 16) / 2, 806, dt.date.fromisoformat(month + "-01").strftime("%b"), 13, MUTED, 'text-anchor="middle"'), "</g>"])
    return "".join(parts) + "</svg>"


def portrait(source):
    from PIL import Image, ImageEnhance, ImageOps
    image = Image.open(source).convert("RGBA")
    background = Image.new("RGBA", image.size, "white")
    background.alpha_composite(image)
    image = ImageOps.fit(background.convert("L"), (120, 100))
    image = ImageEnhance.Contrast(image).enhance(1.15)
    ramp = " .:-=+*#%@"
    parts = frame(840, 880, "eden@github: ~$ ./portrait.sh", "A bubble tea character revealed line by line as ASCII art")
    for row in range(100):
        line = "".join(ramp[min(9, round((255 - image.getpixel((col, row))) / 255 * 9))] for col in range(120))
        y, delay = 72 + row * 7.35, row * .045
        parts.append(f'<clipPath id="r{row}"><rect x="24" y="{y-7:.2f}" width="792" height="9"><animate attributeName="width" from="0" to="792" dur=".045s" begin="{delay:.3f}s" fill="freeze"/></rect></clipPath>')
        parts.append(f'<g class="portrait-row" clip-path="url(#r{row})">' + text(24, round(y, 2), line, 9, INK, 'xml:space="preserve" textLength="792" lengthAdjust="spacingAndGlyphs"') + "</g>")
    parts.append('<path d="M0 824H840" stroke="#30363d"/>')
    parts.append(text(24, 854, "eden@github:~$ whoami   EdenChang", 17, ACCENT))
    return "".join(parts) + "</svg>"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="eden0118")
    parser.add_argument("--html", type=Path, help="Use a saved GitHub calendar instead of fetching")
    parser.add_argument("--portrait", type=Path, help="Also regenerate the ASCII portrait")
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
        outputs["assets/portrait.svg"] = portrait(args.portrait)
    for path, content in outputs.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    print(f"Generated profile art: {len(days)} days, {stats['total']:,} contributions")


if __name__ == "__main__":
    main()
