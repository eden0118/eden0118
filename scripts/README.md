# Profile art

The profile follows a design portfolio layout: a typographic cover, design studies,
an introduction, and optional GitHub activity. The palette uses white, charcoal,
and drafting blue. The cover includes a character-scramble typing animation
from `design.png`, `need-sleep.png`, `working.png`, and `drink.png`, without terminal chrome.

`scripts/design-cover-template.svg` controls the cover layout; its portrait marker
is filled by the generator. `assets/design-practice.svg` is an editable vector asset.
GitHub activity lives in a collapsed details section and refreshes from the public
calendar without a personal access token or external stats service. Pillow is used
only to convert the character image into ASCII.

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py --portrait design.png need-sleep.png working.png drink.png
```

The workflow refreshes the cover, portrait, and activity SVGs daily at 06:17 UTC (14:17 Taipei time),
on relevant pushes to master or main, or through Actions → Update profile art →
Run workflow. GitHub may delay scheduled jobs. Generated assets are committed
so the README also works when a refresh fails.

Statistics cover GitHub's calendar (approximately the last year). The current
streak allows today to have no contributions yet, using UTC dates. Longest
streak is limited to this calendar, rather than the account's lifetime.
The parser stops if daily counts cannot be read, preserving previous images.

Edit the root README to change your introduction. Replace one of the four source PNGs to change a scene, then regenerate. Open preview.html for a local approximation of
GitHub rendering. The portrait cycles continuously; the activity calendar reveals once on load.
Reduced-motion preferences show the completed portrait immediately.

Every SVG has a matching `-dark.svg` variant. README picture sources select the
artwork through `prefers-color-scheme`; the dark background matches GitHub's
default dark theme (#0d1117). Both themes form the same ASCII character through changing symbols. Dark mode uses a soft
mint gray instead of bright white, with a shorter character-density ramp to keep
the illustration gentle. Each illustration is padded to preserve the entire composition. Reduced
motion shows the complete character. Edit light assets or the cover template, then regenerate.

The standalone character study is also available as assets/portrait.svg.

The carousel order is design → need-sleep → working → drink. Each scene types
for 3.6 seconds (24 frames), then holds for 3.4 seconds. The 28-second cycle
repeats continuously, with all frames sharing one clock to avoid timing drift.
Each character has an independent arrival and settling time across the whole
image. SMIL runs without JavaScript. Reduced motion and static renderers show
the complete first illustration. Fixed random seeds avoid daily random churn.
To change the order, edit the --portrait list in the workflow and regenerate.

The lower caption in working.png is cropped out during ASCII conversion.
The source image is preserved.

The four capability sections each have a small animated explanation generated
by scripts/practice_art.py: requirements become a structure, user actions move
between interface states, different needs meet in a discussion, and design
becomes explicit states and implementation components. Motion runs briefly
within a nine-second cycle, leaving a quiet interval for reading. Reduced motion
hides all moving overlays while retaining the complete diagrams. Each animation
has light and dark versions and runs as an embedded SVG without JavaScript.
