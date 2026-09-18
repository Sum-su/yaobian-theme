# -*- coding: utf-8 -*-
"""成对自检：VS Code 里有些键**要配着读**——`X.background` 上的 `X.foreground`。

拿 editor.background 当标尺是不够的：徽章字压在徽章底色上、校验框的字压在校验框
底色上、选中行的字压在选中底色上。这些对儿里只要糊一个，界面上就是一块看不见的字。

标尺还是青瓷：某对儿在青瓷里是多少，别的主题不该明显更低。
（prim 系的对儿青瓷自己就只做到 2.3–2.4，所以按「相对青瓷」判，不套绝对阈值。）
"""
import io
import json
import os
import sys
from collections import defaultdict

import palette as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "themes")

# 状态修饰词：`titleBar.activeForeground` 的底色可以是 titleBar.activeBackground，
# 也可以退回 titleBar.background
def parent_surface(colors, key):
    """某个键实际压在谁身上 —— 半透明底色要先压到它上面才算得对对比度。"""
    ns = key.split(".")[0]
    chain = {
        "statusBar": ["statusBar.background"],
        "statusBarItem": ["statusBar.background"],
        "activityBar": ["activityBar.background"],
        "activityBarBadge": ["activityBar.background"],
        "modernActivityBar": ["activityBar.background"],
        "titleBar": ["titleBar.activeBackground"],
        "list": ["editorWidget.background", "sideBar.background"],
        "menu": ["menu.background", "editorWidget.background"],
        "menubar": ["editorWidget.background", "sideBar.background"],
        "quickInput": ["quickInput.background", "editorWidget.background"],
        "quickInputList": ["quickInput.background", "editorWidget.background"],
        "editorSuggestWidget": ["editorSuggestWidget.background", "editorWidget.background"],
        "peekView": ["peekViewEditor.background", "editorWidget.background"],
        "peekViewResult": ["peekViewResult.background", "editorWidget.background"],
        "input": ["input.background", "editorWidget.background"],
        "inputOption": ["input.background", "editorWidget.background"],
        "dropdown": ["dropdown.background", "editorWidget.background"],
        "gauge": ["editorWidget.background", "editor.background"],
        "notifications": ["notifications.background", "editorWidget.background"],
        "panel": ["panel.background", "editor.background"],
        "sideBar": ["sideBar.background", "editor.background"],
        "editorWidget": ["editorWidget.background", "editor.background"],
        "editorHoverWidget": ["editorHoverWidget.background", "editorWidget.background"],
        "terminal": ["terminal.background", "editor.background"],
        "chat": ["editorWidget.background", "editor.background"],
        "debugView": ["sideBar.background", "editor.background"],
        "breadcrumb": ["editor.background"],
    }.get(ns, ["editor.background"])
    for c in chain:
        if c in colors:
            return colors[c]
    return colors.get("editor.background", "#000000")


def over(colors, key):
    """把某个键的色值压到它该在的底色上，返回实色。"""
    v = colors[key]
    bg = parent_surface(colors, key)
    if bg == v:
        bg = colors.get("editor.background", "#000000")
    return P.mix(bg, v, P.parse(v)[3]) if P.parse(v)[3] < 0.999 else v


def partner(colors, key):
    if not (key.endswith("Foreground") or key.endswith(".foreground")):
        return None
    stem = key[:-len("Foreground")] if key.endswith("Foreground") else key[:-len(".foreground")]
    for cand in (stem + "Background",           # list.activeSelectionForeground
                 stem + ".background",          # editorWidget.foreground
                 stem.rsplit(".", 1)[0] + ".background",   # titleBar.activeForeground
                 stem.rsplit(".", 1)[0] + "Background"):
        if cand in colors and cand != key:
            return cand
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted(f for f in os.listdir(OUT) if f.endswith(".json") and not f.startswith("_"))
    ref = {m: json.load(io.open(os.path.join(OUT, f"qingci-{m}.json"), encoding="utf-8"))["colors"]
           for m in ("dark", "light")}

    # 青瓷基准
    base = {}
    for m in ("dark", "light"):
        c = ref[m]
        for k in c:
            p = partner(c, k)
            if p:
                base[(m, k)] = round(P.contrast(over(c, k), over(c, p)), 2)

    bad = []
    pair_n = 0
    for f in files:
        if f.startswith("qingci") or f.startswith("qing-ci"):
            continue
        m = "dark" if f.endswith("-dark.json") else "light"
        c = json.load(io.open(os.path.join(OUT, f), encoding="utf-8"))["colors"]
        for k, v in c.items():
            p = partner(c, k)
            if not p:
                continue
            pair_n += 1
            got = P.contrast(over(c, k), over(c, p))
            want = base.get((m, k), 4.5)
            # 低于青瓷同键的 70%，且绝对值也低（3.0）时才算问题
            if got < 3.0 and got < want * 0.7:
                bad.append((f, k, p, round(got, 2), want, over(c, k), over(c, p)))
    print(f"成对检查：{pair_n} 对；比青瓷明显更糊的：{len(bad)}")
    seen = defaultdict(list)
    for f, k, p, got, want, v, pv in bad:
        seen[k].append((f, got, want, v, pv))
    for k, items in sorted(seen.items(), key=lambda x: -len(x[1])):
        f, got, want, v, pv = items[0]
        print(f"  {k:<44}{len(items):>3} 套  最差 {got}（青瓷 {want}）  例 {f[:-5]} {v} on {pv}")


if __name__ == "__main__":
    main()
