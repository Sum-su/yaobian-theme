# -*- coding: utf-8 -*-
"""发布到 VS Code 商城 / Open VSX —— token 只从文件或环境变量读，**不进命令行**。

为什么要单独写这个脚本，而不是直接敲 `vsce publish --pat <token>`：
`--pat` 会出现在进程列表里，也可能被 vsce 打进日志。这里改成把 token 放进**子进程的环境变量**
（vsce 认 `VSCE_PAT`，ovsx 认 `OVSX_PAT`），argv 里只有包路径，输出里也从不回显 token。

token 放哪（按顺序找，第一个存在的就用）：
    环境变量 VSCE_PAT / OVSX_PAT
    <本目录>\\vsce-pat.txt / ovsx-pat.txt
    C:\\temp\\vsce-pat.txt / ovsx-pat.txt
    %USERPROFILE%\\.vsce-pat / .ovsx-pat
（这些文件名都写进 .gitignore 了；文件里只放 token 一行，别加引号。）

    python publish.py --check              # 只看准备好没有，不发布
    python publish.py                      # 两个都发
    python publish.py --marketplace        # 只发 VS Code 商城
    python publish.py --openvsx            # 只发 Open VSX
    python publish.py --vsix dist/xxx.vsix # 指定要发的包（默认取 dist/<name>-<version>.vsix）
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "package.json")
DIST = os.path.join(HERE, "dist")

TOKEN_FILES = {
    "marketplace": ["vsce-pat.txt", os.path.join(os.environ.get("TEMP", "C:\\temp"), "vsce-pat.txt"),
                    os.path.join(os.path.expanduser("~"), ".vsce-pat")],
    "openvsx": ["ovsx-pat.txt", os.path.join(os.environ.get("TEMP", "C:\\temp"), "ovsx-pat.txt"),
                os.path.join(os.path.expanduser("~"), ".ovsx-pat")],
}
TOKEN_ENV = {"marketplace": "VSCE_PAT", "openvsx": "OVSX_PAT"}


def find_token(kind):
    """返回 (token, 来源说明)。找不到就 (None, 说明)。"""
    env = os.environ.get(TOKEN_ENV[kind], "").strip()
    if env:
        return env, "环境变量 %s" % TOKEN_ENV[kind]
    for p in TOKEN_FILES[kind]:
        if os.path.isfile(p):
            t = io.open(p, encoding="utf-8-sig").read().strip().strip('"').strip("'")
            if t:
                return t, p
    return None, "、".join(TOKEN_FILES[kind])


def run(cmd, token, kind):
    """跑 vsce/ovsx：token 只走环境变量，绝不进 argv 或日志。"""
    env = dict(os.environ)
    env[TOKEN_ENV[kind]] = token
    print("    $ " + " ".join(cmd) + "   （token 走 %s，不在命令行里）" % TOKEN_ENV[kind])
    p = subprocess.run(cmd, cwd=HERE, env=env)
    return p.returncode


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--marketplace", action="store_true", help="只发 VS Code 商城")
    ap.add_argument("--openvsx", action="store_true", help="只发 Open VSX")
    ap.add_argument("--check", action="store_true", help="只检查 token 和包，不发布")
    ap.add_argument("--vsix", help="要发布的 .vsix（默认 dist/<name>-<version>.vsix）")
    a = ap.parse_args()

    pkg = json.load(io.open(PKG, encoding="utf-8"))
    vsix = a.vsix or os.path.join(DIST, "%s-%s.vsix" % (pkg["name"], pkg["version"]))
    targets = [k for k in ("marketplace", "openvsx")
               if (not a.marketplace and not a.openvsx)
               or (a.marketplace and k == "marketplace")
               or (a.openvsx and k == "openvsx")]

    print("包        ：%s%s" % (vsix, "" if os.path.isfile(vsix) else "  ← 不存在，先 `npx @vscode/vsce package`"))
    print("发布者    ：%s（扩展 id %s.%s）" % (pkg["publisher"], pkg["publisher"], pkg["name"]))
    ok = True
    for kind in targets:
        tok, src = find_token(kind)
        print("%-10s：%s" % (kind, ("已找到 token（%s，%d 字符）" % (src, len(tok))) if tok
                             else "没有 token —— 放到 %s" % src))
        ok = ok and bool(tok)
    if a.check:
        return 0 if ok else 1
    if not os.path.isfile(vsix):
        raise SystemExit("找不到要发布的包：%s" % vsix)
    if not ok:
        raise SystemExit("有目标缺 token，先按上面的路径放好（见 PUBLISHING.md）")

    for kind in targets:
        tok, _ = find_token(kind)
        if kind == "marketplace":
            rc = run(["npx", "--yes", "@vscode/vsce", "publish",
                      "--packagePath", vsix, "--no-dependencies"], tok, kind)
        else:
            rc = run(["npx", "--yes", "ovsx", "publish", vsix], tok, kind)
        print("    → %s 退出码 %d" % (kind, rc))
        if rc != 0:
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
