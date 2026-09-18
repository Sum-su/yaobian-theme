# -*- coding: utf-8 -*-
"""把 72 套主题画成一张联络表（PNG），用来「看」一眼有没有翻车。

数字再漂亮也不如瞄一眼：每格是一小块假编辑器 —— 底色、侧栏、状态栏、
正文/注释/关键字/字符串/函数的语法色、选中块、行号，还有徽章和报错色。
"""
import io
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "themes")

SAMPLE = [("def", "kw"), (" fire", "fn"), ("(self, kiln):", "ty"), ("", None),
          ("    # 开片：天青", "cm"), ('    glaze = "天青"', "st"),
          ("    return", "kw"), (" self._glaze", "ty"), ("  # 注释", "cm")]
CELL_W, CELL_H = 300, 104
PAD = 8


def rule_for(theme, scope):
    if not scope:
        return theme["colors"]["foreground"]
    for r in theme["tokenColors"]:
        sc = r.get("scope")
        scopes = [sc] if isinstance(sc, str) else (sc or [])
        if any(s == scope or s.startswith(scope + ".") for s in scopes):
            return r.get("settings", {}).get("foreground")
    return theme["colors"]["foreground"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ids = [t["id"] for t in json.load(io.open(os.path.join(HERE, "package.json"),
                                              encoding="utf-8"))["contributes"]["themes"]
           if False]
    themes = json.load(io.open(os.path.join(HERE, "cherry_palettes.json"), encoding="utf-8"))
    order = [t["id"] for t in themes if t["id"] != "starry-night"]
    cards = [(i, m) for i in order for m in ("dark", "light")]
    cols = 6
    rows = (len(cards) + cols - 1) // cols
    W, H = cols * (CELL_W + PAD) + PAD, rows * (CELL_H + PAD) + PAD + 26
    img = Image.new("RGB", (W, H), (24, 27, 26))
    dr = ImageDraw.Draw(img)
    dr.text((10, 8), "qingci x cherrycss — 36 themes x2 (%d cells)" % len(cards),
            fill=(200, 210, 205))

    for n, (tid, mode) in enumerate(cards):
        cx = PAD + (n % cols) * (CELL_W + PAD)
        cy = 26 + PAD + (n // cols) * (CELL_H + PAD)
        th = json.load(io.open(os.path.join(OUT, f"{tid}-{mode}.json"), encoding="utf-8"))
        c = th["colors"]
        bg = c["editor.background"]
        dr.rectangle([cx, cy, cx + CELL_W, cy + CELL_H], fill=bg)
        # 侧栏 + 状态栏 + 标题栏
        dr.rectangle([cx, cy, cx + 56, cy + 82], fill=c["sideBar.background"])
        dr.rectangle([cx, cy, cx + CELL_W, cy + 14], fill=c["titleBar.activeBackground"])
        dr.rectangle([cx, cy + 82, cx + CELL_W, cy + CELL_H], fill=c["statusBar.background"])
        dr.text((cx + 4, cy + 2), f"{tid} {mode}", fill=c["titleBar.activeForeground"])
        # 行号 + 语法
        for i in range(6):
            dr.text((cx + 40, cy + 18 + i * 10), str(i + 1), fill=c["editorLineNumber.foreground"])
        x = cx + 62
        y = cy + 18
        for text, scope in SAMPLE[:6]:
            dr.text((x, y), text, fill=rule_for(th, scope))
            y += 10
        # 选中块 + 徽章 + 报错
        dr.rectangle([cx + 58, cy + 18, cx + 130, cy + 27], fill=c["editor.selectionBackground"])
        dr.rectangle([cx + 8, cy + 40, cx + 30, cy + 52], fill=c["badge.background"])
        dr.text((cx + 12, cy + 42), "9", fill=c["badge.foreground"])
        dr.text((cx + 62, cy + 86), "main  x 0  ! 0", fill=c["statusBar.foreground"])
        dr.text((cx + 200, cy + 86), "err", fill=c["editorError.foreground"])
        # 焦点框 + 校验框
        dr.rectangle([cx + 200, cy + 18, cx + 290, cy + 34], outline=c["focusBorder"])
        dr.text((cx + 204, cy + 20), "warn", fill=c["inputValidation.warningForeground"])
        dr.rectangle([cx + 200, cy + 40, cx + 290, cy + 56],
                     fill=c["inputValidation.warningBackground"])
        dr.text((cx + 204, cy + 42), "check", fill=c["inputValidation.warningForeground"])
        dr.rectangle([cx + 200, cy + 56, cx + 290, cy + 72],
                     fill=c["inputValidation.errorBackground"])
        dr.text((cx + 204, cy + 58), "error", fill=c["inputValidation.errorForeground"])

    path = os.path.join(HERE, "sheet.png")
    img.save(path)
    print(f"→ sheet.png（{img.size[0]}x{img.size[1]}，{os.path.getsize(path)//1024} KB）")
    # 再来一张只看样张中段（放大），便于细看
    big = img.resize((int(W * 1.6), int(H * 1.6)), Image.LANCZOS)
    path2 = os.path.join(HERE, "sheet_big.png")
    big.save(path2)
    print(f"→ sheet_big.png（{big.size[0]}x{big.size[1]}）")


if __name__ == "__main__":
    main()
