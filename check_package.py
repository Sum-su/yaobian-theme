# -*- coding: utf-8 -*-
"""发布前的守门检查：**包里的东西**和**清单声明的东西**必须严格对上。

为什么要有这个：`contributes.themes` 声明 72 套，而 `themes/` 目录里躺着 74 个 json
（多出来的是 build.py 手写的基准 `qingci-*.json`），vsce 照着目录打包、从不看清单——
于是那个 484 KB 的 vsix 里一直多带两个没人读的 40 KB 文件，谁都没发现。
「目录里有」不等于「该进包」，这个脚本就是拿来问这句话的。

查这些（任何一条不过就退出码 1）：
    1. 包里 themes/*.json 的集合 == contributes.themes 声明的集合（多一个少一个都报）
    2. 每个声明的 path 在包里真实存在，且是合法 JSON、带 name/colors
    3. `%...%` 占位符都能在 package.nls.json 里找到（商城页面上不能出现裸的 %description%）
    4. 名字/发布者/版本/协议，以及 vsixmanifest 里展开后的 Description
    5. LICENSE 是**裸 MIT 全文**（追加说明段会让 GitHub 认不出协议）

    python check_package.py                     # 查 dist/ 里最新的 vsix
    python check_package.py --vsix dist/x.vsix  # 查指定的
"""
import argparse
import glob
import io
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")

FAILS = []


def check(cond, ok_msg, bad_msg):
    if cond:
        print("  ✓ " + ok_msg)
    else:
        print("  ✗ " + bad_msg)
        FAILS.append(bad_msg)
    return cond


def norm(path):
    """清单里的 path 形如 './themes/x.json'，统一成 'themes/x.json'。"""
    p = path.replace(os.sep, "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def newest_vsix():
    got = glob.glob(os.path.join(DIST, "*.vsix"))
    if not got:
        return None
    return max(got, key=os.path.getmtime)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--vsix", help="要检查的 vsix（默认 dist/ 里最新的那个）")
    a = ap.parse_args()

    vsix = a.vsix or newest_vsix()
    if not vsix or not os.path.isfile(vsix):
        raise SystemExit("找不到 vsix：%s" % (vsix or DIST))
    pkg = json.load(io.open(os.path.join(HERE, "package.json"), encoding="utf-8"))
    nls = json.load(io.open(os.path.join(HERE, "package.nls.json"), encoding="utf-8"))

    print("包：%s（%.1f KB）" % (os.path.basename(vsix), os.path.getsize(vsix) / 1024.0))
    z = zipfile.ZipFile(vsix)
    names = z.namelist()

    def read(name):
        return z.read(name).decode("utf-8")

    print("\n1) 包里的主题 ↔ 清单声明的主题")
    declared = set(norm(t["path"]) for t in pkg["contributes"]["themes"])
    inside = set(n[len("extension/"):] for n in names
                 if n.startswith("extension/themes/") and n.endswith(".json"))
    for p in sorted(inside - declared):
        check(False, "", "包里有清单没声明的主题：%s（装上去没人读的孤儿文件）" % p)
    for p in sorted(declared - inside):
        check(False, "", "清单声明了但包里没有：%s ← 用户会在选择器里看不到它" % p)
    if declared == inside:
        check(True, "%d 套主题，两边完全一致（没有孤儿、没有缺漏）" % len(declared), "")

    print("\n2) 每套主题能解析、字段齐")
    bad = []
    for p in sorted(declared & inside):
        try:
            t = json.loads(read("extension/" + p))
        except ValueError as e:
            bad.append("%s 不是合法 JSON：%s" % (p, e))
            continue
        if not t.get("name") or not isinstance(t.get("colors"), dict) or not t["colors"]:
            bad.append("%s 缺 name 或缺 colors" % p)
    check(not bad, "%d 个 json 全部可解析、name/colors 齐全" % len(declared & inside),
          "；".join(bad))

    print("\n3) package.json 里的 %%占位符%% 都能解析")
    leftover = []
    txt = read("extension/package.json")
    for k in re.findall(r"%([A-Za-z0-9_.-]+)%", txt):
        if k not in nls:
            leftover.append("%" + k + "%")
    check(not leftover, "只用到 %description%（本地由 package.nls.json 解析）",
          "package.nls.json 里没有这些键：%s" % "、".join(sorted(set(leftover))))

    print("\n4) 身份信息")
    check(pkg["displayName"] == "窑变", "显示名是「窑变」（两个字，无后缀）",
          "displayName 是 %r，应为「窑变」" % pkg["displayName"])
    check(pkg["license"] == "MIT", "package.json 的 license 是 MIT",
          "license 字段是 %r" % pkg.get("license"))
    ident = "%s.%s@%s" % (pkg["publisher"], pkg["name"], pkg["version"])
    check(True, "扩展 id %s（%d 套主题）" % (ident, len(declared)), "")
    check("extension/icon.png" in names, "带图标 icon.png", "包里没有 icon.png")

    print("\n5) vsixmanifest（商城页面读的是这里，不是 package.json）")
    if "extension.vsixmanifest" in names:
        m = read("extension.vsixmanifest")
        dm = re.search(r"<Description[^>]*>(.*?)</Description>", m, re.S)
        desc = (dm.group(1) if dm else "").strip()
        check(bool(desc) and "%" not in desc,
              "Description 已展开成正文（商城不会显示裸的 %%description%%）：%s…" % desc[:48],
              "vsixmanifest 里的 Description 没展开：%r" % desc)
    else:
        check(False, "", "包里没有 extension.vsixmanifest（pack.py 手搓的包会有——"
                         "商城必须用 npx @vscode/vsce package）")

    print("\n6) LICENSE 是裸 MIT 全文")
    # 只认文件名前缀，不认后缀：vsce 写 LICENSE.txt、pack.py 手搓的写 LICENSE，两个都对
    # （清单里各自指着各自的路径）。这里查的是**内容**，名字不一样不该算不过。
    lics = [n for n in names
            if os.path.basename(n).lower().startswith("license") and not n.endswith("/")]
    if lics:
        lic = read(lics[0])
        check(lic.startswith("MIT License"), "以 'MIT License' 开头（文件是 %s）"
              % os.path.basename(lics[0]),
              "LICENSE 不是以 MIT License 开头")
        check(lic.rstrip().endswith("SOFTWARE."),
              "以免责声明结尾（**后面没追加任何说明段**，否则 GitHub 认不出 MIT）",
              "LICENSE 结尾不是免责声明——多半又追加了说明段，GitHub 会判成 license: null")
    else:
        check(False, "", "包里没有 LICENSE 文件")

    print("\n%s" % ("全部通过 ✓" if not FAILS else "%d 项不过：" % len(FAILS)))
    for f in FAILS:
        print("  - " + f)
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
