# Profile artwork

All visible profile text lives in `README.md`: the name, role, background,
working-practice headings, collaboration perspectives, and closing line. Edit
those directly without regenerating any images. Native Markdown headings,
blockquote, tables, bold text, and italics provide the layout.

Only the character and four diagrams are SVG images. They keep the cyan pixel
style while GitHub supplies the text font, table borders, and theme colors.
`assets/design.png` supplies the character. Other source images remain intact.

## Generate graphics

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py
python3 scripts/check_art.py
```

`scripts/profile_art.py` generates the ordered-dither character.
`scripts/practice_art.py` generates the four graphic-only diagrams.
Generation is deterministic and does not modify README text. The SVGs have no
visible text, animation, JavaScript, raster embeds, or external font dependencies.

`preview.html` is a static preview of the current Markdown using approximate
GitHub styles; it does not automatically update when README text is edited.
Use your editor's Markdown preview or GitHub's preview for subsequent text edits.
The **Check profile art** workflow validates referenced assets and regenerated
output, including size budgets, unique identifiers, and absence of visible SVG text.
