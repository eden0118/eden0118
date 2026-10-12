# Profile artwork

The profile contains a four-scene ASCII carousel and one connected four-stage diagram.
Light and dark versions use native SVG animation without GIFs or JavaScript.
Each character illustration is stored once as ASCII text. A 0.6-second crossfade
connects the scenes without character noise or scanning masks. The four working
practices share one canvas, with headings highlighted in sequence. The drawings
stay visible throughout, without traveling dots or sliding shapes.

## Generate

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py
/tmp/eden-profile-venv/bin/python scripts/check_art.py
```

The order is `design.png`, `need-sleep.png`, `working.png`, `drink.png`, with a
seven-second slot for each scene and a continuous 28-second loop.
`working.png` is cropped during conversion to remove its lower caption.
Source images are kept intact.

`scripts/design-cover-template.svg` controls the cover typography and layout.
`scripts/practice_art.py` combines the four explanatory drawings into one workflow. Assets are
generated locally with the commands above and committed together with source
changes. The **Check profile art** workflow validates committed assets, runs the
generator in its temporary runner, and checks the result on pushes, pull
requests, or manual runs. It has read-only repository permissions and never
commits or pushes generated files. No daily job or contribution request is needed.

The artwork adapts to the viewer's color scheme. Reduced-motion preferences
show the first complete illustration and a static workflow. Static SVG renderers
also show the first illustration. `preview.html` approximates GitHub rendering.

Only assets used by the README are kept. The checks enforce size and element
budgets, continuous interpolation, correct carousel timing, a shared workflow timeline, and valid image
references. The previous many-frame SVG and GIF approaches have been removed.
