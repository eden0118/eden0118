# Profile visual direction

This GitHub README introduces a product manager through a design background and
a way of approaching problems. It does not rank engineering skills or list
individual projects. The ASCII character is the identifying visual.

## Composition

```text
ASCII portrait      Name / role / short positioning / background
Observe             Plan                  Explore
Design perspective                       Design origins
```

The README uses one 980-unit desktop composition at every viewport width.
Only theme and reduced-motion preferences select alternate sources; there are
no phone or intermediate breakpoints. Content narrows proportionally with its
container. Tool icons are an optional desktop panel, currently omitted from README.

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
- A short personal design perspective and an origins diagram share one panel.
- The toolkit uses a fixed grid of equal-size icons with readable names, without capability pills or
  purpose captions. White brand marks use neutral backing; the AWS mark uses a
  light inset for its original dark lettering. Keep original symbol geometry.
- No project list, invented metrics, oversized H1 name or repeated section tags.

## Implementation and verification

`scripts/profile_layout.py` owns the current panels and theme tokens.
`assets/profile.json` supplies wording; README supplies matching image text
alternatives. Preview content is generated from README, without special layout
that would only work outside GitHub.

Verify desktop light/dark compositions, text bounds and reduced-motion source
selection. Different viewport widths must keep the same desktop source.
The local preview approximates the README content area, not all GitHub chrome.
