# Profile artwork

The README follows the terminal-banner, introduction, stack, signals and stats
layout of [emmi-lili](https://github.com/emmi-lili). Graphics are original and use
Eden's existing character and profile information.

The banner has a real ASCII portrait generated from `assets/design.png` using
120 columns and 76 rows of density characters. `scripts/terminal_art.py` renders
the ASCII lettering into an SVG terminal alongside profile details. Both light
and dark assets are local and self-contained. GitHub selects the theme through
`picture` elements. Stack icons and the GitHub badge use external image services.

## Update profile data

Edit `assets/profile.json` to change the banner fields and chart data. Edit the
prose in `README.md` separately. `preview.html` is a static local preview of the
README; keep it in sync when changing the profile text or image references.

GitHub statistics and language counts are a public-data snapshot as of the date
in `profile.json`; they are not automatically refreshed. `source` and
`repos_source` record the public API endpoints used. Language values count each
non-fork public repository's primary language, rather than bytes or proficiency.
The practice map describes working relationships without invented skill scores.

## Regenerate and validate

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py
/tmp/eden-profile-venv/bin/python scripts/check_art.py
```

Generation is deterministic and works offline from the stored profile data.
`profile_art.py` generates the eight visible terminal assets along with the six
previous graphic experiments. The earlier assets remain available but are not
referenced by the README. The validation workflow checks local references,
size budgets, SVG descriptions, unique identifiers and absence of external embeds
or scripts. It also checks the ASCII portrait dimensions and character set.
