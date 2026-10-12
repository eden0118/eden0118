# Profile artwork

The README is a single retro electronic dossier: pixel lettering, a cyan
ordered-dither character portrait, and four static diagrams on a shared grid.
The card keeps the same dark palette in both GitHub color schemes. The existing
`design.png` supplies the character; no generated portrait or external font is needed.

## Generate

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py
python3 scripts/check_art.py
```

`scripts/design-cover-template.svg` defines the card frame and one-shot startup
pulse. `scripts/profile_art.py` contains the embedded 5×7 pixel alphabet and the
ordered-dither portrait converter. `scripts/practice_art.py` draws the four
working practices. Generation is deterministic and writes `assets/profile-card.svg`.
Source images remain intact.

The startup overlay fades out within 0.8 seconds and never repeats. Reduced-motion
preferences hide it entirely. Static renderers show the complete card. There is
no JavaScript, raster image embed, network request, or external font dependency.
The image's alt text and SVG title/description provide a text equivalent.

`preview.html` approximates GitHub's image display on desktop and mobile. The
**Check profile art** workflow validates the SVG and its references, regenerates
it, and validates the output. Checks enforce an asset size budget, four practices,
unique identifiers, a single finite animation, and no unused artwork.
