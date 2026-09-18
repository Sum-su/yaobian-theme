# -*- coding: utf-8 -*-
"""形状自检：每套主题每个键的「色值形状」和青瓷同键同模式比。

青瓷是手调定稿的基准：某个键在青瓷里是不透明的 6 位，那别的主题也不该
冒出 8 位（半透明）——除了设计上就该透的那几类（选中、半透明边框、
NONE 关掉的描边）。这个脚本就是拿它当标尺扫一遍 72 套。
"""
import io
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "themes")

# 半透明在 VS Code 里的合法用途：选中/高亮/描边/光标，以及 NONE
ALLOW_ALPHA = ("selection", "Selection", "highlight", "Highlight", "border", "Border",
               "outline", "Outline", "shadow", "Shadow", "dropBackground", "hover",
               "Hover", "Cursor", "cursor", "findMatch", "wordHighlight", "bracketMatch",
               "rangeHighlight", "inactiveSelection", "sash", "focusBorder", "Sash",
               "scrollbarSlider", "inputValidation", "widget.shadow", "minimap.",
               "editorOverviewRuler.border", "editorBracketHighlight",
               "editorUnnecessaryCode", "editorError.foreground",
               "editorWarning.foreground", "editorInfo.foreground",
               "editorHint.foreground", "problemsErrorIcon", "problemsWarningIcon",
               "problemsInfoIcon", "notebook.", "terminal.selectionBackground",
               "terminalCursor", "gitDecoration", "diffEditor.", "merge",
               "editorGutter", "breadcrumb", "editorIndentGuide", "editorWhitespace",
               "editorLineNumber", "activityBarBadge", "statusBarItem", "panelTitle",
               "textLink", "button", "list.", "menu.selection", "menubar.selection",
               "quickInputList", "tab.", "titleBar", "toolbar", "badge", "notification",
               "extensionButton", "inputOption", "peekView", "symbolIcon", "testing.",
               "charts.", "debugConsole", "debugToolBar", "editorHoverWidget",
               "editorSuggestWidget", "editorMarkerNavigation", "editorLink",
               "editor.stackFrameHighlight", "editor.focusedStackFrameHighlight",
               "editorGroupHeader", "editor.lineHighlight", "sideBarSectionHeader",
               "statusBar", "activityBar", "editorWidget", "editorGroup",
               "editorPane", "editorBackground", "sideBar", "progressBar",
               "editor.selectionHighlight", "editor.rangeHighlight",
               "sash.hoverBorder", "widget.border", "input.placeholder",
               "listFilterWidget", "settings.", "keybindingLabel",
               "editor.linkedEditing", "editorBracketMatch", "editor.foldPlaceholder",
               "editor.snippetTabstopHighlight", "editor.snippetFinalTabstopHighlight",
               "editor.symbolHighlight", "editor.findMatch", "editor.findRange",
               "terminal.ansi", "terminal.border", "terminal.background",
               "terminal.foreground", "editorOverviewRuler", "editorRuler",
               "editorCodeLens", "editorCommentsWidget", "editorLightBulb",
               "editorOverviewRulerBorder")


def shape(v):
    if not isinstance(v, str) or not v.startswith("#"):
        return v
    body = v[1:]
    if len(body) == 8 and body[6:].lower() == "00":
        return "NONE"
    if len(body) == 8 and body[6:].lower() != "ff":
        return "8位(半透明)"
    return "6位"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    themes = sorted(f for f in os.listdir(OUT) if f.endswith(".json") and not f.startswith("_"))
    ref = {}
    for mode in ("dark", "light"):
        d = json.load(io.open(os.path.join(OUT, f"qingci-{mode}.json"), encoding="utf-8"))
        ref[mode] = d["colors"]

    diff = []
    per_theme = {}
    for f in themes:
        tid, _, mode = f[:-5].rpartition("-")
        d = json.load(io.open(os.path.join(OUT, f), encoding="utf-8"))
        if tid == "qingci":
            continue
        n = 0
        for k, v in d["colors"].items():
            s, rs = shape(v), shape(ref[mode][k])
            if s != rs and not (s == "8位(半透明)" and rs == "6位"
                                and any(a in k for a in ALLOW_ALPHA)):
                diff.append((f, k, v, ref[mode][k]))
                n += 1
        # 每套用到的不同色值数（看有没有「整片同色」）
        per_theme[f] = len({v for v in d["colors"].values()})
    print(f"色值形状与青瓷不同的：{len(diff)} 处"
          + ("" if not diff else ""))
    by_key = defaultdict(list)
    for f, k, v, rv in diff:
        by_key[k].append((f, v))
    for k, items in sorted(by_key.items(), key=lambda x: -len(x[1]))[:12]:
        print(f"  {k:<42}{len(items):>3} 套   例 {items[0][0][:-5]} {items[0][1]}（青瓷 {shape(ref['dark'].get(k, ref['light'].get(k)))}）")
    c = Counter(per_theme.values())
    print(f"每套主题用到的不重复色值数分布: {dict(sorted(c.items()))}")
    # 底色/正文是不是实心——这个最关键
    for f in themes:
        d = json.load(io.open(os.path.join(OUT, f), encoding="utf-8"))["colors"]
        for k in ("editor.background", "sideBar.background", "foreground",
                  "activityBar.background", "titleBar.activeBackground",
                  "statusBar.background", "editorWidget.background"):
            if shape(d[k]) == "8位(半透明)":
                print(f"  !! {f} {k} 半透明 {d[k]}")
    print("半透明渗进实色键的：无 ✓" if not any(
        shape(json.load(io.open(os.path.join(OUT, f), encoding="utf-8"))["colors"][k]) == "8位(半透明)"
        for f in themes for k in ("editor.background", "sideBar.background", "foreground",
                                  "activityBar.background", "titleBar.activeBackground",
                                  "statusBar.background", "editorWidget.background")) else "")


if __name__ == "__main__":
    main()
