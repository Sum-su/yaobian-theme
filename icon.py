# -*- coding: utf-8 -*-
"""画扩展图标 icon.png（128×128）：釉色「窑」字压在墨色底上，底纹是冰裂纹。

窑变 = 一窑出万色：底色用墨 `#2C3635`、字用釉 `#7BA898`（和青瓷、Zotero/Cherry 那套同源），
裂纹是随机折线，所以每跑一次都不一样——要复现就固定 seed。

    python icon.py            # 生成 icon.png
    python icon.py --seed 7   # 换一张裂纹
"""
import argparse
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
INK = (0x2C, 0x36, 0x35)          # 墨
GLAZE = (0x7B, 0xA8, 0x98)        # 釉
FONT = r"C:\Windows\Fonts\LXGWWenKai-Medium.ttf"
S = 1024                          # 先画大的再缩，边缘干净


def crackle(d, seed):
    """冰裂纹：从边缘往里的随机折线，压得很淡，只当底纹。"""
    rnd = random.Random(seed)
    for _ in range(26):
        x, y = rnd.choice([(rnd.uniform(0, S), 0), (0, rnd.uniform(0, S)),
                           (rnd.uniform(0, S), S), (S, rnd.uniform(0, S))])
        ang = rnd.uniform(0, 6.283)
        pts = [(x, y)]
        for _ in range(rnd.randint(4, 9)):
            ang += rnd.uniform(-0.9, 0.9)
            step = rnd.uniform(S * 0.05, S * 0.16)
            x, y = x + step * math.cos(ang), y + step * math.sin(ang)
            pts.append((x, y))
        d.line(pts, fill=GLAZE + (26,), width=rnd.randint(2, 5), joint="curve")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260918)
    a = ap.parse_args()

    img = Image.new("RGB", (S, S), INK)
    overlay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    crackle(ImageDraw.Draw(overlay), a.seed)
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # 字：居中。字体本身有行高，用 bbox 做视觉居中。
    font = ImageFont.truetype(FONT, int(S * 0.62))
    d = ImageDraw.Draw(img)
    box = d.textbbox((0, 0), "窑", font=font)
    d.text(((S - (box[2] - box[0])) / 2 - box[0],
            (S - (box[3] - box[1])) / 2 - box[1]), "窑", font=font, fill=GLAZE)

    img.convert("RGB").resize((128, 128), Image.LANCZOS).save(os.path.join(HERE, "icon.png"))
    print("icon.png 128x128（seed=%d）" % a.seed)


if __name__ == "__main__":
    main()
