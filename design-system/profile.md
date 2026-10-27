# Profile visual direction

This GitHub README introduces a product manager through a design background and
a way of approaching problems. It does not rank engineering skills or list
individual projects. The ASCII character is the identifying visual.

## Composition

```text
Desktop
  ASCII portrait      Name / role / short positioning / background
  Observe             Plan                  Explore
  Shared decisions                         Design origins
                  Skills and tools

Mobile
  Identity and positioning
  ASCII portrait
  Background
  Observe / Plan / Explore, stacked
  Shared decisions / Design origins, stacked
  Wrapping badges
```

All panels use the same 980-unit desktop or 360-unit mobile width. Wide panels
switch to the mobile source at 600px. Use a clear hierarchy and bounded text
lengths rather than enlarging small standalone charts to fill the page.

## Tokens

| Role | Dark | Light |
| --- | --- | --- |
| Canvas | `#0d1117` | `#f8f9fd` |
| Raised surface | `#161c26` | `#eef1f8` |
| Primary text | `#ecf1fa` | `#202b40` |
| Secondary text | `#adb9cc` | `#52627b` |
| Teal accent | `#81d8d0` | `#146b68` |
| Violet drawing | `#c2b4ff` | `#6750a4` |

Use Arial/Helvetica for reading and headings. Reserve monospace for the ASCII
and its small profile caption. The palette extends the existing blue/violet
identity; the design intelligence search's generic monochrome/blue suggestion
was adapted to retain that identity. External fonts and JavaScript are not
required.

## Restraint

- One moving element: the ASCII portrait. Reduced motion selects a complete,
  static source at the parent `picture`, alongside the SVG's own media fallback.
- Three process columns share a track rather than individual card borders.
- Two conceptual diagrams share one panel. They do not express measured scores.
- Badges use a common neutral backing; retain their original symbol geometry.
- No project list, invented metrics, oversized H1 name or repeated section tags.

## Implementation and verification

`scripts/profile_layout.py` owns the current panels and theme tokens.
`assets/profile.json` supplies wording; README supplies matching image text
alternatives. Preview content is generated from README, without special layout
that would only work outside GitHub.

Browser review covers dark/light at 375, 390, 768 and 1100px, correct mobile
sources, text bounds, reduced motion and the normal animation's completed frame.
The local preview approximates the README content area, not all GitHub chrome.
