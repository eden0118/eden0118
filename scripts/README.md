# Profile artwork

The profile contains a four-scene ASCII carousel and four animated diagrams.
Both light and dark versions are generated locally. The cover embeds a small
pre-rendered animation instead of thousands of live SVG text elements.

## Generate

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py
/tmp/eden-profile-venv/bin/python scripts/check_art.py
```

The source order is `design.png`, `need-sleep.png`, `working.png`, `drink.png`.
Each scene types at 20 fps for 3.6 seconds and holds for 3.4 seconds. The full
28-second loop repeats continuously. The lower caption in `working.png` is
cropped during conversion. Source images are kept intact.

`scripts/design-cover-template.svg` controls the cover typography and layout.
`scripts/practice_art.py` generates the four explanatory diagrams. Assets are
regenerated when source images or scripts are pushed, or by running the
**Update profile art** workflow manually. No daily job or contribution-data
request is needed.

The cover and diagrams adapt to the viewer's color scheme. Reduced-motion
preferences show the first completed illustration and static diagrams.
`preview.html` is a local approximation of GitHub's README rendering.

Only assets used by the README are kept. The earlier standalone portraits,
contribution cards, summary diagram, and unused source illustration have been
removed. Edit `README.md` for copy changes and update `preview.html` to match.

The cover uses a four-tone animated GIF embedded in a small SVG, keeping the
heading text sharp without live text animation. The asset checks enforce a
download and element budget, verify the four-scene loop, and catch a return to
the previous slow typing cadence.
