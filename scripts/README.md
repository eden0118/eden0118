# Profile art

Original SVG generators inspired by AVIVASHISHTA29's terminal layout.
The portrait source is `drink.png`. Contributions come from GitHub's public calendar;
no personal access token or external stats service is needed.

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py --portrait drink.png
```

The workflow refreshes all three SVGs daily at 06:17 UTC (14:17 Taipei time),
on relevant pushes to master or main, or through Actions → Update profile art →
Run workflow. GitHub may delay scheduled jobs. Generated assets are committed
so the README also works when a refresh fails.

Statistics cover GitHub's calendar (approximately the last year). The current
streak allows today to have no contributions yet, using UTC dates. Longest
streak is limited to this calendar, rather than the account's lifetime.
The parser stops if daily counts cannot be read, preserving previous images.

Edit the root README to change your introduction. Replace drink.png to change
the portrait. CSS and SMIL provide animation without JavaScript.
Reduced-motion preferences show the complete portrait and disable CSS reveals.
