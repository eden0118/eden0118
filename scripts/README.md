# Profile art

The profile follows a design portfolio layout: a typographic cover, design studies,
an introduction, and optional GitHub activity. The palette uses white, charcoal,
and drafting blue. The cover includes a line-by-line character animation
from `drink.png`, without terminal chrome.

`scripts/design-cover-template.svg` controls the cover layout; its portrait marker
is filled by the generator. `assets/design-practice.svg` is an editable vector asset.
GitHub activity lives in a collapsed details section and refreshes from the public
calendar without a personal access token or external stats service. Pillow is used
only to convert the character image into ASCII.

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py --portrait drink.png
```

The workflow refreshes the cover, portrait, and activity SVGs daily at 06:17 UTC (14:17 Taipei time),
on relevant pushes to master or main, or through Actions → Update profile art →
Run workflow. GitHub may delay scheduled jobs. Generated assets are committed
so the README also works when a refresh fails.

Statistics cover GitHub's calendar (approximately the last year). The current
streak allows today to have no contributions yet, using UTC dates. Longest
streak is limited to this calendar, rather than the account's lifetime.
The parser stops if daily counts cannot be read, preserving previous images.

Edit the root README to change your introduction. Replace drink.png to change
the character, then regenerate. Open preview.html for a local approximation of
GitHub rendering. The cover portrait and activity calendar reveal once on load.
Reduced-motion preferences show the completed portrait immediately.

Every SVG has a matching `-dark.svg` variant. README picture sources select the
artwork through `prefers-color-scheme`; the dark background matches GitHub's
default dark theme (#0d1117). Both characters reveal row by row: the light theme
uses ASCII, while the dark theme preserves the original color illustration on a
soft mint backdrop so the expression stays friendly. The illustration is embedded
inside the SVG and does not need an external image request. Reduced motion shows
the complete character. Edit light assets or the cover template, then regenerate.

The standalone character study is also available as assets/portrait.svg.
