# Sources and credits

Yaobian ships **36 color-theme families** (72 themes, dark + light). Almost none
of the palettes originate here, so this file names every source it can be traced
to, plus the licence each one carries.

If you are one of the authors below and want your credit changed — or the theme
removed — please open an issue and it will be done.

## What was taken, and what was not

Only **colour values** were taken. For each source palette this project reads a
list of hex colours (23 variables at most) and re-derives a full VS Code theme
from them: 567 workbench colour keys, 68 TextMate rules and 28 semantic-token
rules, all computed by the formulas in [`roles.py`](roles.py)/[`gen.py`](gen.py).

Nothing else from the sources is used: no CSS, no animations, no fonts, no
layout rules, no selectors, no images. A source's "theme" here is its palette,
nothing more.

## 1. The gallery these themes were collected from

| | |
| --- | --- |
| Project | **cherrycss** — <https://cherrycss.com> — <https://github.com/boilcy/cherrycss> |
| Author | Caiyun Liu ([@boilcy](https://github.com/boilcy)) |
| Licence | MIT, © 2025 Caiyun Liu (full text below) |
| Used for | the 36 palette definitions in `lib/themes/**` — parsed by [`cherry.py`](cherry.py) |

cherrycss publishes these as CSS themes for Cherry Studio. Its own README lists
one source for the Chinese-style set (the linux.do thread in §2) and carries no
per-theme provenance, so the individual upstreams below were traced by hand.

## 2. The 25 `chineseStyle` themes

| | |
| --- | --- |
| Source | **linux.do topic 325119** — <https://linux.do/t/topic/325119> — "分享一些中国风 Cherry Studio 主题皮肤" (2025-01-03) |
| Author | linux.do user **imkekeaiai** |
| Licence | none declared |
| Themes | 禅棕 chan-zong, 长安 chang-an, 春梅 chun-mei, 丹霞 dan-xia, 汉白玉 han-bai-yu, 湖光 hu-guang, 金镶玉 jin-xiang-yu, 流云 liu-yun, 琵琶 pi-pa, 青瓷 qing-ci, 青雾 qing-wu, 汝窑蓝 ru-yao-lan, 汝窑绿 ru-yao-lv, 山水 shan-shui, 素宣 su-xuan, 天水 tian-shui, 宣纸 xuan-zhi, 雁灰 yan-hui, 烟雨 yan-yu, 胭脂 yan-zhi, 羊皮纸 yang-pi-zhi, 窑火 yao-huo, 玉石 yu-shi, 紫陶 zi-tao |

「青花」 (qing-hua) is by the same author, posted later in
[reply #129](https://linux.do/t/topic/325119/129) of the same thread.

These were written directly for Cherry Studio — they are not ports of any VS Code
theme. Note that no licence is declared: they are credited here as the source of
the palettes, with the author's name, and can be removed on request.

## 3. The 11 `others` themes

| Theme | Source | Author / project | Licence |
| --- | --- | --- | --- |
| Dracula | <https://github.com/dracula/dracula-theme> | Dracula Theme, created by Zeno Rocha | **MIT**, © 2023 Dracula Theme |
| Vitesse Soft | <https://github.com/antfu/vscode-theme-vitesse> | Anthony Fu ([@antfu](https://github.com/antfu)), built on GitHub's Primer theme | **MIT**, © 2020 Primer, © 2021 Anthony Fu |
| 莫奈 mo-nai | <https://linux.do/t/topic/325119> | linux.do user **imkekeaiai** | none declared |
| 奶茶 nai-cha | <https://linux.do/t/topic/325119> | linux.do user **imkekeaiai** | none declared |
| 歌蕾蒂娅·返航 gladiia | <https://linux.do/t/topic/432753> | linux.do user **404nyaFound**; dark variant contributed by **LostMyHead** | none declared |
| Claude | <https://linux.do/t/topic/472763> | linux.do user **EDWINCHENC** (an earlier, unnamed version was optimised in that post) | none declared |
| Peppa | <https://github.com/boilcy/cherrycss/issues/28> | GitHub user **hailey07** | none declared separately (contributed into cherrycss's MIT repository) |
| 暮山紫 mu-shan-zi | <https://github.com/boilcy/cherrycss/pull/16> | GitHub user **HPUhushicheng** | contributed into cherrycss's MIT repository |
| Pulse (脉动交互) | <https://github.com/boilcy/cherrycss/pull/13> | GitHub user **Lucas04-nhr** | contributed into cherrycss's MIT repository |
| Mint | palette `#519D9E #58C9B9 #9DC8C8 #D1B6E1` — <https://colorhunt.co/palette/519d9e58c9b99dc8c8d1b6e1> | the palette is from Color Hunt; Color Hunt states each palette "is a public property and not owned by a specific creator, nor by Color Hunt" | public property (per Color Hunt) |
| Dopamine | — | not stated in cherrycss; no upstream found | unknown — see below |

Notes on the awkward ones:

- **Dopamine** is the one theme whose provenance could not be established. It
  entered cherrycss as a direct commit with no source given, and searches of the
  cherrycss history, the Cherry Studio community, the VS Code Marketplace and
  Open VSX turned up nothing that matches its colours. It is treated as a
  cherrycss original; if that is wrong, say so and it will be credited or pulled.
- **Peppa** takes its name from the children's show. No artwork or fonts from it
  are used — the palette is the cartoon's red/pink/blue/yellow/green — but the
  name is a trademark of Hasbro/eOne and is used here only descriptively.
- **歌蕾蒂娅·返航** likewise names a character and skin from *Arknights*; only the
  palette is used, and the name identifies which palette it is.
- **starryNight** exists in cherrycss but is deliberately **not** shipped: its
  look depends on a background image injected by a Cherry Studio extension,
  which has no VS Code equivalent.

## 4. Everything else in this repository

Original work, MIT, © 2026 Tombliboo: the pipeline (`cherry.py`, `roles.py`,
`keyexpr.py`, `gen.py`, `build.py`, `palette.py`), the role formulas (measured
against the 青瓷 palette in `build.py`), the 567-key colour tables, the syntax and
semantic-token scope tables, the theme switcher `mode.py` and its self-checks,
and the generated JSON in `themes/`.

The TextMate scopes and semantic-token selectors follow VS Code's own bundled
`dark_vs` and `dark_plus` themes (MIT, © Microsoft Corporation) — the scopes are
copied, the colours are not.

## 5. Required licence texts

### cherrycss

```
MIT License

Copyright (c) 2025 Caiyun Liu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Dracula Theme

```
MIT License

Copyright (c) 2023 Dracula Theme

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Vitesse Theme

```
MIT License

Copyright (c) 2020 Primer
Copyright (c) 2021 Anthony Fu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 中文说明

本扩展的 36 款配色**几乎都不是原创**：色板来自 cherrycss.com（MIT，© 2025 Caiyun Liu）
收录的主题，其中 25 款中国风 + 莫奈 + 奶茶出自 linux.do 主题帖
[t/325119](https://linux.do/t/topic/325119)（作者 imkekeaiai，帖子未声明许可），
另有 Dracula（MIT）、Vitesse Soft（MIT）、Peppa、Claude、歌蕾蒂娅·返航、暮山紫、
脉动交互、Mint 等各自的社区作者。上面逐条点名，能查到的一律给了作者与链接。

本仓库**只取了颜色值**：源主题的 CSS、动画、字体、布局一概没用，VS Code 的 567 个颜色键
是按本仓库的公式算出来的。若你是上述作者，希望改署名或撤下某一款，开个 issue 即可。

同名主题的**名称**（Peppa、歌蕾蒂娅、Claude 等）只用于指认配色来源，不含任何关联或授权含义；
相关商标归各自权利人所有。
