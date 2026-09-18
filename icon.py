# -*- coding: utf-8 -*-
"""生成扩展图标 icon.png（128×128）——青瓷冰裂纹碗。

源图是仓库外的照片，**故意不放进版本库**：仓库是公开的，没必要把 1.8 MB 的
原作也发出去，而图标本身已经随 vsix 分发了。所以这里用绝对路径，跟
gen.py 读 refs/ 的做法一个道理——本地可复现，克隆者不需要它也能打包。

    python icon.py                       # 用默认源图
    python icon.py --src D:\\path\\x.png  # 换一张

源图 1212×1233，不是正方形。**先居中裁成方的再缩**，否则碗会被压扁 1.7%。
缩完补一道轻 unsharp：冰裂纹是发丝级线条，1212 → 128 直接 LANCZOS 会糊成一片。
"""
import argparse
import os

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = r"D:\tombliboo\Pictures\Saved Pictures\窑变.png"
SIZE = 128


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC, help="源图路径")
    ap.add_argument("--size", type=int, default=SIZE)
    a = ap.parse_args()

    if not os.path.exists(a.src):
        raise SystemExit("找不到源图：%s\n用 --src 指定。" % a.src)

    im = Image.open(a.src).convert("RGB")
    w, h = im.size
    side = min(w, h)
    im = im.crop(((w - side) // 2, (h - side) // 2,
                  (w + side) // 2, (h + side) // 2))

    out = im.resize((a.size, a.size), Image.LANCZOS)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    dest = os.path.join(HERE, "icon.png")
    out.save(dest, "PNG", optimize=True)
    # 源图路径含中文，而 Windows 上 stdout 被管道接走时是 GBK（见 CLAUDE.md 的
    # 输出编码陷阱）。转义成 \uXXXX 再印，路径照样可读，字节流是纯 ASCII。
    label = a.src.encode("ascii", "backslashreplace").decode("ascii")
    print("icon.png %dx%d (%d bytes)  <-  %s (%dx%d)"
          % (a.size, a.size, os.path.getsize(dest), label, w, h))


if __name__ == "__main__":
    main()
