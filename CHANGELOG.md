# Changelog

## 0.3.0

First public release. The extension was previously installed locally as
`tombliboo.qingci-theme`; it is renamed to **窑变** (`tombliboo.yaobian-theme`) and published
here.

- 36 theme families × dark/light = **72 colour themes** (567 workbench keys, 68 TextMate rules,
  28 semantic rules each).
- Palette pipeline: `cherry.py` → `roles.py` → `gen.py` + `keyexpr.py`, with Celadon kept
  byte-identical to its hand-tuned reference.
- Follow-system / manual dark-mode switching, with the manual choice preserved while the
  system is in charge.
- `mode.py` switcher, its 25-check test suite and the falsification script.
- English and Chinese documentation; full source credits in `NOTICE.md`.

### 0.1.0

Celadon only (dark + light), hand-tuned. Never published.
