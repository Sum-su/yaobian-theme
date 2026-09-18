# Changelog

## 0.3.2

Metadata only — no theme file changed, so nothing looks different once installed.

- `package.json` now has a `contributors` field naming **DeepSeek**, which wrote the palette
  pipeline and the check scripts under the author's direction. The Marketplace renders this
  field on the extension page, so the credit needed a version of its own to become visible.
- New `CONTRIBUTORS.md` says who did what, and repeats the third-party provenance pointer.

## 0.3.1

Icon only — no theme file changed, so nothing looks different once installed.

- New `icon.png`: a celadon crackle-glaze bowl, replacing the drawn 「窑」 glyph. It is now
  derived from a photograph by `icon.py` (centre-crop to square first, then a light unsharp,
  because the crackle lines are hairline detail that plain LANCZOS would smear at 128 px).
  The source photo is deliberately kept out of the repo; `icon.py --src` takes a path.

## 0.3.0

First public release. The extension was previously installed locally as
`tombliboo.qingci-theme`; it is renamed to **窑变** (`tombliboo0226.yaobian-theme`) and published
here.

- 36 theme families × dark/light = **72 colour themes** (567 workbench keys, 68 TextMate rules,
  28 semantic rules each).
- Palette pipeline: `cherry.py` → `roles.py` → `gen.py` + `keyexpr.py`, with Celadon kept
  byte-identical to its hand-tuned reference.
- Follow-system / manual dark-mode switching, with the manual choice preserved while the
  system is in charge.
- `mode.py` switcher, its 25-check test suite and the falsification script.
- English and Chinese documentation; full source credits in `NOTICE.md`.
- `check_package.py`, which compares the packaged `.vsix` against `contributes.themes`. It
  caught two files the first build was shipping that no manifest entry declared (the
  hand-tuned Celadon baselines); they now live in `refs/`, and the package contains exactly
  the 72 themes it advertises.

### 0.1.0

Celadon only (dark + light), hand-tuned. Never published.
