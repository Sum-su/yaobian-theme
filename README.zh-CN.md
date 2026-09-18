# 窑变

> English: [README.md](README.md)

一个 VS Code 扩展（`tombliboo26.yaobian-theme`），把 [cherrycss.com](https://cherrycss.com)
主题画廊的配色铺成 VS Code 配色主题，含本机一直在用的**青瓷**（它就是画廊里的一款）。

名字取「窑变」——一窑烧出万色，同一套釉料配方在不同火候下变成 36 种颜色，正好像这条流水线。

**配色几乎都不是原创的**，来源逐条点名在 [NOTICE.md](NOTICE.md)（含各上游作者、链接与许可）。
本仓库的代码与生成的 72 套主题以 MIT 发布。

| | 数量 |
| --- | --- |
| 主题 | **36 款**（画廊 `chineseStyle` 25 + `others` 11） |
| × 深浅两套 | **72 套颜色主题** |
| 每套工作台颜色键 | 567 |
| 每套 TextMate 语法规则 | 68 |
| 每套语义高亮规则 | 28 |

版本 `0.3.0`。**改名过一次**：0.2.0 及以前叫 `tombliboo.qingci-theme`（青瓷与 Cherry 主题集），
改名后旧 id 已卸载——两个都装着会让选择器里出现两份同名主题。

## 装

在 VS Code 里搜 **窑变**（扩展 id `tombliboo26.yaobian-theme`），或者：

```bash
code --install-extension tombliboo26.yaobian-theme      # 从商城装
code --install-extension dist/yaobian-theme-0.3.0.vsix --force   # 装本地打的包
```

装扩展本身**不用重载窗口**：正在运行的那个窗口会当场认出新装的主题
（2026-09-18 用一个隔离窗口实测：装完立刻切到「青瓷（深）」，工作台 567 个颜色键全部解析，
全程没重载）。之前这里写着「要重载」，是错的。

⚠ **卸载才是要当心的那一步**。如果卸掉的正是**当前在用的那套主题**的提供者，
VS Code 会在你眼皮底下把 `workbench.colorTheme` 这个键**删掉**（屏幕回落到内置主题）。
隔离实测过两边：窗口关着时卸载 → 设置文件一个字节没动；窗口开着时卸载 → 2 秒内那个键就没了
（对应内置的 `reloadCurrentColorTheme`，它会把已失效的当前主题再应用一次、写回一个空 id）。
所以**换版本/换 id 之后，卸完要再设一次**：

```bash
python mode.py dark 青瓷      # 或你想要的家族
```

之后切换：`Ctrl+K Ctrl+T`，或改设置里的 `workbench.colorTheme`。

## 深浅模式：跟随系统 / 手动，两条路随时换

VS Code 原生就有这两条路，四个设置键说了算：

| 模式 | 谁决定显示哪套 | 键 |
| --- | --- | --- |
| **跟随系统** | 系统亮暗 → 对应槽位 | `window.autoDetectColorScheme: true`、`workbench.preferredDarkColorTheme`、`workbench.preferredLightColorTheme` |
| **手动** | 你选的那套 | `workbench.colorTheme`（`autoDetectColorScheme: false`） |

窑变的切换器（`mode.py`）做两件事：把 **36 个家族 × 深浅**都成对喂进那两个槽位；
切换时以**此刻正在显示的那一套**为起点。

```bash
cd C:\temp\yaobian-vscode
python mode.py status                # 现在什么模式、哪一家、系统是深是浅
python mode.py auto [家族]           # 跟随系统（家族缺省 = 当前这套的家族）
python mode.py manual                # 切回手动，钉住此刻显示的那套 ← 这就是「继承」
python mode.py dark | light [家族]   # 手动钉死深浅
python mode.py list                  # 36 个家族
python mode.py tasks                 # 把入口写进 VS Code 命令面板（见下）
```

家族参数 **id 和标签都认**：`hu-guang` = `湖光` = `湖光（深）`。

**「继承切换前的深浅」是怎么做的**（都是实测过的）：

- 跟随系统开着时，`workbench.colorTheme` 被 VS Code 忽略，但**不会被清掉**——
  手动选过的那套一直躺在设置里，这就是记忆本身。
- 切回手动时读的不是那个旧值，而是 `state.vscdb` 里**此刻正在渲染**的那套：
  实测在「跟随系统 · 显示湖光（浅）」时跑 `manual`，钉住的是**湖光（浅）**，
  不是设置里躺着的旧值青瓷（深）。家族和深浅都跟着现在的画面走。
- 反向（手动 → 跟随系统）：家族沿用当前这套，亮暗交给系统。系统切深浅时是**热切**，
  不重载窗口。
- 改完设置约 **1 秒内**生效（改的是设置不是主题文件，所以没有重载那回事）。

**在 VS Code 里点**：`Ctrl+Shift+P` → `Tasks: Run Task` → 「窑变：…」共 7 条
（跟随系统·当前家族 / 跟随系统·选家族 / 切回手动 / 手动·深 / 手动·浅 / 状态 / 列出家族）。
写在**用户级** `tasks.json` 里，纯声明式、不需要扩展带代码，`python mode.py tasks` 可重新生成
（里面有不是窑变的任务时会拒绝覆盖，除非 `--force`）。

一个已知的小坑：跟随系统时从主题选择器里手点一套，VS Code 只改**当前亮暗对应的那一个槽位**，
于是可能配成「深色用湖光、浅色用青瓷」。`mode.py status` 会把这种错配点出来，
`python mode.py auto <家族>` 一键配对。

## 36 款主题

官网画廊自己的分组与顺序，括号里是 id。选择器里的顺序是**青瓷提到最前**，其余照此序。

`chineseStyle`（25）

| | | | | |
| --- | --- | --- | --- | --- |
| 禅棕（`chan-zong`） | 长安（`chang-an`） | 春梅（`chun-mei`） | 丹霞（`dan-xia`） | 汉白玉（`han-bai-yu`） |
| 湖光（`hu-guang`） | 金镶玉（`jin-xiang-yu`） | 流云（`liu-yun`） | 琵琶（`pi-pa`） | 青瓷（`qing-ci`） |
| 青花（`qing-hua`） | 青雾（`qing-wu`） | 汝窑蓝（`ru-yao-lan`） | 汝窑绿（`ru-yao-lv`） | 山水（`shan-shui`） |
| 素宣（`su-xuan`） | 天水（`tian-shui`） | 宣纸（`xuan-zhi`） | 雁灰（`yan-hui`） | 烟雨（`yan-yu`） |
| 胭脂（`yan-zhi`） | 羊皮纸（`yang-pi-zhi`） | 窑火（`yao-huo`） | 玉石（`yu-shi`） | 紫陶（`zi-tao`） |

`others`（11）

| | | | | |
| --- | --- | --- | --- | --- |
| Claude（`claude`） | Dopamine（`dopamine`） | Dracula（`dracula`） | 歌蕾蒂娅·返航（`gladiia`） | Mint（`mint`） |
| 莫奈（`mo-nai`） | 暮山紫（`mu-shan-zi`） | 奶茶（`nai-cha`） | Peppa（`peppa`） | Pulse（`pulse-interactive`） |
| Vitesse Soft（`vitesse-soft`） | | | | |

## 流水线

主题不是一套套手写的，是**算出来的**——一条链，中间每一步都能单独跑、单独验：

```text
cherrycss 仓库的 36 个主题 .ts
      │  cherry.py    解析 CSS 变量（v2Compatibility.ts 的 Python 移植）
      ▼               → 每个模式一套「规范色板」canonical
   canonical
      │  roles.py     按青瓷量出来的公式，算成 61–67 个语义角色
      ▼               （正文三档、描边、强调色族、语义色族、语法色族…）
  角色向量
      │  gen.py + keyexpr.py   567 条「角色表达式」表
      ▼                        × 68 条语法规则 + 28 条语义规则
   themes/<id>-<深/浅>.json（72 套）
```

- **`build.py`** 是基准：青瓷手调定稿的两张色表（`D` / `L`）、567 个颜色键的清单、
  以及语法/语义高亮的 scope 表（scope 照抄 VS Code 自带 `dark_vs`+`dark_plus`，只换色，所以不缺语言）。
- **`keyexpr.py`** 把青瓷那两张表反推成 567 条表达式（`ink`、`mix(prim, ink, 0.4)`、
  跨模式的 `inkDk`…），别的主题只要算出自己的角色向量，就能套同一张表。
- **青瓷走的是冻结向量**，不走公式：`gen.py` 最后会把公式生成的两套 `qing-ci-*.json`
  与 `build.py` 手写的 `qingci-*.json` **逐字节**比对，不一致就报错退出。

跑一遍：

```bash
python cherry.py     # 重抽规范色板（改了 .ts 解析逻辑才需要）
python roles.py      # 规范色板 -> 角色向量，附对比度报告
python gen.py        # 角色向量 -> 72 套主题 JSON + package.json + preview.html
python pack.py       # 打成 dist/yaobian-theme-0.3.0.vsix
code --install-extension dist/yaobian-theme-0.3.0.vsix --force
```

## 自检

手写主题最大的坑是**键名写错**——VS Code 对不认识的键**不报错、直接忽略**，
于是「改了没反应」能查很久。所以每一步都带一道闸：

| 脚本 | 查什么 | 现在的结果 |
| --- | --- | --- |
| `build.py` | 567 个键拿去 VS Code 自身三个来源核（自带主题、内置扩展 `contributes.colors`、`out/**/*.js` 里的字面量） | 全部命中；另废掉 16 个这版已没有的键 |
| `roles.py` | 角色齐备、正文/语法色对底色的对比度 | 角色齐备 ✓；< 3.0 的角色 29 处（都是 prim 族，见下） |
| `gen.py` | 键集合深浅两套一致、色值合法、**青瓷逐字节复原** | 72 套 × 567 键一致 ✓；青瓷 39748 / 39749 字节一致 ✓ |
| `check_shape.py` | 每个键的「色值形状」和青瓷同键同模式比（该不透明的别冒 8 位） | 0 处不同；半透明渗进实色键：无 ✓ |
| `check_pairs.py` | 6230 对「前景 + 它实际压着的底色」的对比度，标尺是青瓷 | 261 对明显更糊（主力是 prim 族，见下） |
| `test_mode.py` | 切换器只动那四个键、其余字节不动；[python] 块里的同名键不被误改；继承；插入的键跟**多数派**缩进对齐；屏幕不是窑变时 `status` 要如实说；**失败注入** | 25 项全过 ✓ |
| `falsify_checks.py` | 把上面两处改进**回退成旧写法**，跑一遍看那几条检查会不会红 | 4 项如期变红 ✓ |
| `sheet.py` | 把 72 套画成一张联络表 PNG，**用眼睛**过一遍 | `sheet.png`（1856×1378） |
| `preview.html` | 同理，浏览器里逐块看 | 生成在根目录 |

`test_mode.py` 里那条「其余逐字节不动」是**充分证明**式的：把原文件里那四个键也换成新值之后，
两边必须完全相同——差一个字节就红。并且带失败注入（改掉一个别的键，确认检查会红），
免得写出一条永远绿的检查。新加的两条也各自证伪过，而且**做成了脚本**：`python falsify_checks.py`
会在临时目录里复制一份工程，把 `_indent_of` 换回「照抄第一个顶层键」、把 `current()` 的诚实注记删掉，
跑 `test_mode.py`，要求那 4 项**变红**；红不了就说明检查是摆设，脚本自己报失败。

## 诚实的部分

- **starryNight 没收**。仓库里有这个主题，但官网画廊的 `others` 列表里没有它，而且它的观感
  靠扩展往界面注入一张背景图——VS Code 主题没有对应物，硬做只会是个四不像。
- **Dracula 的浅色是反相推出来的**（源主题只有深色一种模式），亮暗关系对，但不是原作。
- **几套主题的源色板本身就稀疏**，缺的变量由公式补：Pulse 28 个、歌蕾蒂娅 26/28 个、
  素宣 27 个、Peppa 15 个；其余主题只缺固定的那几个（`foreground-tertiary`、`error`、`link`、
  代码块、引用条），这几项 cherrycss 的 v1 主题基本都不声明。补法是按同一套公式算，不是拍脑袋。
- **语义色是锚定的**：语法色可以随强调色转，但错误/警告/信息/成功四族的**色相**固定用青瓷量出来的
  那四个角度（29.5° / 90.4° / 223.5° / 172.7°），只按各主题的底色平移明度、按强调色比例缩放彩度。
  不做这一步的话，禅棕会得到蓝色的错误提示、紫色的警告——试过。
- **20 处强调色因为可读性被提亮了**（`roles.py` 会点名）：禅棕、长安这些的强调色和底色只差 1.4:1，
  而 VS Code 里它要当焦点框、徽章底色、状态栏底色用。提亮的下限是 **2.5:1**——
  这恰好是**青瓷浅色自己**的水平，不是新标准。
- **选中块里的语法色**：半透明选中块压在语法色上，块内对比度天然会掉。青瓷深色自己最差 2.19、
  浅色 1.94；这 72 套里最差的是 dopamine 深色 1.50。这是青瓷选中块的设计（`#7BA89852`）自带的性质，
  成套继承，没有单独为某几套改选中透明度。
- **`check_pairs.py` 剩下的 261 对**：主力是 prim 系（按钮字、徽章字、光标压强调色），
  最差 2.5:1，和青瓷浅色自己的 2.3–2.4 同档，属于「照抄基准的设计取舍」而不是新引入的糊。
- **Peppa 的描边**：它的源色板把 `--color-border` 直接写成正文色（深色 `#ECECEC`、浅色 `#000000`），
  于是「描边」角色等于正文色，而它有几处是当**底色**用的（`button.secondaryBackground`），
  正文色压上去正好 1:1，字直接消失。现在描边有一条上限：对底色的对比度不超过正文的 28%
  （青瓷自己是 12%），越界的往底色里混、保色相。只有 Peppa 触发。

## 改色

- **想让某一套换颜色**：改 `cherry.py` 的 `DEFAULT_SOURCES` / 主题 .ts 映射，或直接在
  `cherry_palettes.json` 里改那个主题的 `canonical`，然后 `python roles.py && python gen.py`。
- **想改所有主题的「青瓷感」**（正文三档的退让比例、描边强度、强调色下限…）：改 `roles.py` 里的公式。
- **想改青瓷自己**：改 `build.py` 顶部两张表。这时要**重拍基准快照**，否则 `gen.py` 会拦你：

```bash
python build.py && cp themes/qingci-dark.json _ref_qingci-dark.json \
                && cp themes/qingci-light.json _ref_qingci-light.json
```

（`_ref_qingci-*.json` 就是「上一次确认过的手调基准」，`gen.py` 拿它防手滑改坏基准。）

不想重新打包的话，也能直接改装好的 JSON：

```text
%USERPROFILE%\.vscode\extensions\tombliboo26.yaobian-theme-0.3.0\themes\qing-ci-dark.json
```

这一种**要**重载窗口：主题文件只在该主题被加载时读一次，之后没有文件监听
（主题缓存里的 `watch` 字段是 `false`）。

## 覆盖不到的

- **图标主题**：没动，仍是你现在的 `material-icon-theme` / `macos-modern` 产品图标
- **字体**：没动（`Source Code Pro, 霞鹜文楷` 那套设置照旧）
- **Windows 系统本身**：切换器只管 VS Code。系统深色要不要切、跟不跟时间表，不归它管
- **扩展自己写死颜色的地方**：GitLens、Jupyter 输出里的 HTML、LaTeX 预览的 CSS——
  它们不吃主题变量时只能各自改配置
- 终端里程序自己输出的 24bit 真彩色，不受 16 色 ANSI 影响

## 回滚

```bash
code --uninstall-extension tombliboo26.yaobian-theme
```

卸的时候如果 VS Code 正开着、而且正用着窑变的主题，`workbench.colorTheme` 这个键会被
VS Code 自己删掉（见上面「装」那节的实测），所以卸完要**再把 `workbench.colorTheme` 写回去**：
装窑变之前这台机器是 `MacOS Modern Dark - Ventura Xcode Civic`；还想留在窑变某一套就
`python mode.py dark 青瓷`。

装 0.1.0 时新加过 `window.autoDetectColorScheme` / `preferredDark/LightColorTheme` 三项，
以及这次新增的 `configurationDefaults`（扩展自带的默认值，只是给没设过的人当兜底，卸载即消失）。

`dist/qingci-theme-0.1.0.vsix` 还留着（只有青瓷两套的旧版）。要装它的话**先卸掉 0.3.0**，
两边的主题标签同名，同时装着会在选择器里出现两份「青瓷（深）」。

`mode.py` 每次改设置前会留一份 `settings.json.yaobian-bak`，不想要可以随手删。

## 许可与来源

- **本仓库的代码与生成的 72 套主题**：MIT，© 2026 Tombliboo（[LICENSE](LICENSE)）。
- **配色来源**：逐条点名在 [NOTICE.md](NOTICE.md)——cherrycss（MIT，© 2025 Caiyun Liu）、
  25 款中国风 + 莫奈 + 奶茶（linux.do 主题帖，作者 imkekeaiai）、Dracula（MIT）、
  Vitesse Soft（MIT，Anthony Fu）、Peppa、Claude、歌蕾蒂娅·返航、暮山紫、脉动交互、
  Mint（Color Hunt 公共调色板）等，各自标了作者、链接与许可证状况。
- 取用的**只有颜色值**：源主题的 CSS、动画、字体、布局一概没用；VS Code 的 567 个颜色键
  是按本仓库的公式从色板算出来的。某一款若查不到上游许可，NOTICE 里会写明「未声明许可，
  仅作来源说明」——作者本人若希望改署名或撤下，开 issue 即办。
