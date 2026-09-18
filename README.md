# Yaobian (窑变)

**36 colour-theme families for VS Code — 72 themes, each in a matched dark and light pair.**

中文说明见 [README.zh-CN.md](README.zh-CN.md) · Sources and credits: [NOTICE.md](NOTICE.md) · Licence: [MIT](LICENSE)

The palettes come from the [cherrycss.com](https://cherrycss.com) theme gallery — a
collection of Chinese-style and community colour schemes — re-expressed as full VS Code
themes. It includes **青瓷 / Celadon**, the palette this project grew out of.

The name 窑变 (*yáobiàn*) is the kiln transmutation of glazes: one recipe, different heat,
and 36 different colours come out of the same firing. That is roughly what the pipeline here
does.

| | |
| --- | --- |
| Theme families | **36** (25 `chineseStyle` + 11 `others`) |
| Themes (dark + light) | **72** |
| Workbench colour keys per theme | 567 |
| TextMate syntax rules per theme | 68 |
| Semantic highlighting rules per theme | 28 |

## Install

Search **窑变** in the Extensions view, or:

```bash
code --install-extension tombliboo.yaobian-theme              # from the Marketplace
code --install-extension yaobian-theme-0.3.0.vsix --force      # from a local .vsix
```

Then pick a theme with `Ctrl+K Ctrl+T` (`Cmd+K Cmd+T` on macOS) or via
`workbench.colorTheme` in your settings.

**Installing needs no window reload** — a running window picks up the new themes immediately.
(Themes are read once when applied, so *editing* a theme file does need a reload; installing
does not.)

⚠ **Uninstalling is the risky direction.** If you uninstall while a window is running and that
extension provides the theme currently in use, VS Code deletes the `workbench.colorTheme`
setting and falls back to a built-in theme. (Reproduced in isolation: with the window closed
the settings file is untouched; with a window open the key disappears within two seconds.)
After a version swap or uninstall, set your theme again.

## Dark mode: follow the system, or pin it manually

VS Code itself has both paths; four settings decide:

| Mode | What picks the theme | Settings |
| --- | --- | --- |
| **Follow system** | OS light/dark → the matching slot | `window.autoDetectColorScheme: true`, `workbench.preferredDarkColorTheme`, `workbench.preferredLightColorTheme` |
| **Manual** | the one you picked | `workbench.colorTheme` (with `autoDetectColorScheme: false`) |

Switching between them preserves what you were looking at:

- While **follow system** is on, `workbench.colorTheme` is ignored but **not cleared** — the
  theme you picked manually keeps sitting in your settings. That value is the memory.
- Switching back to **manual**, VS Code uses that remembered value, so you return to the
  family you pinned earlier, at the light/dark level the system last showed.
- Both directions take effect within about a second — these are settings changes, not theme
  reloads.

**Power-user extras** (in this repository, not in the extension package):

```bash
python mode.py status                 # which mode, which family, is the OS dark?
python mode.py auto [family]          # follow the system (family defaults to the current one)
python mode.py manual                 # back to manual, pinning what is on screen right now
python mode.py dark | light [family]  # pin a family and a light/dark variant
python mode.py list                   # list all 36 families
python mode.py tasks                  # add "窑变: …" entries to the VS Code command palette
```

`mode.py` pairs **both slots of one family** (so system dark → 湖光 dark, system light → 湖光
light), and its `manual` command reads the theme actually being rendered out of VS Code's
`state.vscdb`, rather than the stale setting, so "inherit what I'm looking at" holds even when
you were following the system. `mode.py tasks` writes `Tasks: Run Task` entries into your
user-level `tasks.json`, so you can switch from the command palette without a terminal.

One known quirk: with follow-system on, picking a theme from VS Code's own picker changes
**only the slot for the current light/dark state**, so you can end up with dark = family A and
light = family B. `mode.py status` points that mismatch out.

## The 36 families

Labels in VS Code's picker are Chinese, suffixed `（深）` for dark and `（浅）` for light —
so `青瓷（深）` is "Celadon (Dark)". The table maps every label.

`chineseStyle` (25)

| Picker label | English | id |
| --- | --- | --- |
| 禅棕 | Zen Brown | `chan-zong` |
| 长安 | Chang'an | `chang-an` |
| 春梅 | Spring Plum | `chun-mei` |
| 丹霞 | Danxia | `dan-xia` |
| 汉白玉 | Han White Marble | `han-bai-yu` |
| 湖光 | Lake Light | `hu-guang` |
| 金镶玉 | Gold-in-Jade | `jin-xiang-yu` |
| 流云 | Drifting Clouds | `liu-yun` |
| 琵琶 | Pipa | `pi-pa` |
| 青瓷 | Celadon | `qing-ci` |
| 青花 | Blue-and-White | `qing-hua` |
| 青雾 | Blue Mist | `qing-wu` |
| 汝窑蓝 | Ru Ware Blue | `ru-yao-lan` |
| 汝窑绿 | Ru Ware Green | `ru-yao-lv` |
| 山水 | Landscape | `shan-shui` |
| 素宣 | Plain Xuan Paper | `su-xuan` |
| 天水 | Sky Water | `tian-shui` |
| 宣纸 | Xuan Paper | `xuan-zhi` |
| 雁灰 | Wild-Goose Grey | `yan-hui` |
| 烟雨 | Misty Rain | `yan-yu` |
| 胭脂 | Rouge | `yan-zhi` |
| 羊皮纸 | Parchment | `yang-pi-zhi` |
| 窑火 | Kiln Fire | `yao-huo` |
| 玉石 | Jade | `yu-shi` |
| 紫陶 | Purple Clay | `zi-tao` |

`others` (11)

| Picker label | English | id |
| --- | --- | --- |
| Claude | Claude | `claude` |
| Dopamine | Dopamine | `dopamine` |
| Dracula | Dracula | `dracula` |
| 歌蕾蒂娅·返航 | Gladiia: Homecoming | `gladiia` |
| Mint | Mint | `mint` |
| 莫奈 | Monet | `mo-nai` |
| 暮山紫 | Dusk Mountain Purple | `mu-shan-zi` |
| 奶茶 | Milk Tea | `nai-cha` |
| Peppa | Peppa | `peppa` |
| Pulse | Pulse | `pulse-interactive` |
| Vitesse Soft | Vitesse Soft | `vitesse-soft` |

## How the themes are made

They are computed, not hand-written — one chain, every step runnable and checkable on its own:

```text
36 theme definitions (CSS variables) from cherrycss
      │  cherry.py    parse the variables (a port of cherrycss's v2Compatibility.ts)
      ▼               → one "canonical palette" per mode
   canonical palettes
      │  roles.py     apply the formulas measured from Celadon → 61–67 semantic roles
      ▼               (three text levels, borders, accent ramp, semantic hues, syntax hues…)
   role vectors
      │  gen.py + keyexpr.py   567 role expressions
      ▼                        × 68 syntax rules + 28 semantic rules
   themes/<id>-<dark|light>.json (72 files)
```

- **`build.py`** is the reference: the two hand-tuned Celadon tables (`D` / `L`), the list of
  567 colour keys, and the syntax/semantic scope tables (scopes copied from VS Code's own
  `dark_vs` + `dark_plus`, so no language is left out — only the colours change).
- **`keyexpr.py`** reverse-engineers Celadon's two tables into 567 expressions (`ink`,
  `mix(prim, ink, 0.4)`, cross-mode `inkDk`…). Any other palette just needs its own role
  vector to reuse the same table.
- **Celadon goes through a frozen vector**, not the formulas: `gen.py` byte-compares the
  formula-generated `qing-ci-*.json` against the hand-written `qingci-*.json` and exits if
  they differ.

Run it end to end:

```bash
python cherry.py     # re-extract the canonical palettes (only after changing the parser)
python roles.py      # canonical palettes -> role vectors, with a contrast report
python gen.py        # role vectors -> 72 theme JSONs + package.json + preview.html
python pack.py       # -> dist/yaobian-theme-0.3.0.vsix  (no node needed)
npx @vscode/vsce package   # the same thing via vsce, which is what the Marketplace gets
```

## Self-checks

The classic failure mode of a hand-written theme is a **misspelled key**: VS Code silently
ignores keys it does not know, so "I changed it and nothing happened" can cost an afternoon.
Every step therefore has a gate:

| Script | What it checks | Current result |
| --- | --- | --- |
| `build.py` | all 567 keys cross-checked against three VS Code sources (bundled themes, built-in `contributes.colors`, literals in `out/**/*.js`) | all found; 16 obsolete keys dropped |
| `roles.py` | role completeness; contrast of text and syntax colours on their backgrounds | complete ✓; 29 roles below 3.0 (all in the `prim` family) |
| `gen.py` | identical key sets across dark/light, valid colour values, **Celadon byte-identical** | 72 × 567 keys ✓; Celadon 39748 / 39749 bytes ✓ |
| `check_shape.py` | colour *shape* per key vs Celadon (no 8-digit values where opaque belongs) | 0 differences ✓ |
| `check_pairs.py` | 6230 foreground/background pairs, scored against Celadon | 261 notably softer (mostly `prim`) |
| `test_mode.py` | the switcher touches only those four keys and not one byte more; `[python]`-scoped keys untouched; inheritance; failure injection | 25 checks pass ✓ |
| `falsify_checks.py` | reverts two improvements back to their old, buggy form and requires the suite to **go red** | 4 checks red as expected ✓ |
| `sheet.py` | renders all 72 themes into one contact-sheet PNG for eyeballing | `sheet.png` (1856×1378) |
| `preview.html` | the same, block by block in a browser | generated in the repo root |

## Honest notes

- **Most palettes are not original to this project.** Every source is named in
  [NOTICE.md](NOTICE.md), including the ones whose authors declared no licence. Only colour
  values were used — no CSS, animations, fonts or layout.
- **starryNight is not included.** It ships in cherrycss, but its look depends on a background
  image injected by a Cherry Studio extension, which has no VS Code equivalent.
- **Dracula's light variant is derived by inversion** (the source theme only has a dark mode).
  The light/dark relationship is coherent, but it is not the original's design.
- **Some source palettes are sparse** and are completed by the formulas: Pulse 28 missing
  variables, Gladiia 26/28, Plain Xuan Paper 27, Peppa 15; the rest are missing the same
  handful that cherrycss v1 themes rarely declare. They are filled in by the same formulas,
  not by guesswork.
- **Semantic hues are anchored.** Syntax colours may rotate with the accent, but error /
  warning / information / success keep the four hues measured from Celadon (29.5° / 90.4° /
  223.5° / 172.7°), with lightness shifted and chroma scaled per palette. Without this, Zen
  Brown gets blue errors and purple warnings — we tried.
- **20 accents were brightened for readability** (Bright-vs-background contrast as low as
  1.4:1 in some palettes, and the accent has to work as a focus ring, a badge and a status-bar
  colour). The floor is **2.5:1** — exactly what Celadon's light theme scores, not a new bar.
- **`check_pairs.py`'s remaining 261 pairs** are mostly the `prim` family (button text, badge
  text, cursor over accent), worst case 2.5:1 — the same range as Celadon light's own 2.3–2.4,
  inherited from the reference design rather than introduced here.

## Making changes

- **To recolour one family**: edit `cherry.py`'s `DEFAULT_SOURCES` / theme mapping, or the
  family's `canonical` block in `cherry_palettes.json`, then `python roles.py && python gen.py`.
- **To change the "Celadon feel" of everything** (the text-level falloffs, border strength,
  accent floor…): edit the formulas in `roles.py`.
- **To change Celadon itself**: edit the two tables at the top of `build.py`, then re-snapshot
  the reference, or `gen.py` will stop you:

```bash
python build.py && cp themes/qingci-dark.json _ref_qingci-dark.json \
                && cp themes/qingci-light.json _ref_qingci-light.json
```

To try a change without repackaging, edit the installed JSON directly — this one **does** need
a window reload (`watch: false`: theme files are read once and not watched):

```text
%USERPROFILE%\.vscode\extensions\tombliboo.yaobian-theme-0.3.0\themes\qing-ci-dark.json
```

## Sources and licence

- **This repository's code and the 72 generated themes**: MIT, © 2026 Tombliboo — [LICENSE](LICENSE).
- **Palettes**: named individually in [NOTICE.md](NOTICE.md) — cherrycss (MIT, © 2025 Caiyun Liu),
  the Chinese-style set plus Monet and Milk Tea (linux.do, by imkekeaiai), Dracula (MIT),
  Vitesse Soft (MIT, Anthony Fu), Peppa, Claude, Gladiia, Dusk Mountain Purple, Pulse and Mint,
  each with its author, link and licence status. Where a source declared no licence, NOTICE.md
  says so, and the credit will be changed or the theme removed on request.
- Theme **names** that reference a character or product (Peppa, Gladiia, Claude) are used only
  to identify which palette a theme comes from. No affiliation is implied, and the names remain
  the property of their owners.

## Rollback

```bash
code --uninstall-extension tombliboo.yaobian-theme
```

Then set `workbench.colorTheme` back to whatever you used before (see the uninstall warning
above — VS Code removes that key for you if the extension was providing the current theme).
Installing 0.1.0 also added `window.autoDetectColorScheme`, `workbench.preferredDarkColorTheme`
and `workbench.preferredLightColorTheme`; the extension additionally contributes default values
for the two preferred slots, which disappear with the extension.

`mode.py` leaves a `settings.json.yaobian-bak` copy before each change — safe to delete.
