# Profile artwork

The profile contains a four-scene ASCII carousel and four animated diagrams.
Light and dark versions use native SVG animation without GIFs or JavaScript.
Each illustration is stored once as final text and once as a faint character
variation. Eight small masks reveal different columns continuously, avoiding
both top-to-bottom scanning and discrete full-image frame changes.

## Generate

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py
/tmp/eden-profile-venv/bin/python scripts/check_art.py
```

The order is `design.png`, `need-sleep.png`, `working.png`, `drink.png`, with a
seven-second slot for each scene and a continuous 28-second loop. Each reveal
finishes within 3.6 seconds, leaving time to view the complete image.
`working.png` is cropped during conversion to remove its lower caption.
Source images are kept intact.

`scripts/design-cover-template.svg` controls the cover typography and layout.
`scripts/practice_art.py` generates the four explanatory diagrams. Assets are
regenerated when source images or scripts are pushed, or by running the
**Update profile art** workflow manually. No daily job or contribution request
is needed.

The artwork adapts to the viewer's color scheme. Reduced-motion preferences
show the first complete illustration and static diagrams. Static SVG renderers
also show the first illustration. `preview.html` approximates GitHub rendering.

Only assets used by the README are kept. The checks enforce size and element
budgets, continuous interpolation, correct carousel timing, and valid image
references. The previous many-frame SVG and GIF approaches have been removed.
