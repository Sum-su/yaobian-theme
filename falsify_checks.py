# -*- coding: utf-8 -*-
"""证伪：把 mode.py 的**新写法**回退成旧写法，确认 test_mode.py 里对应的检查真的会红。

「检查能通过」本身说明不了检查有效——一条恒真的断言也是绿的。所以这里做反向验证：
在临时目录里复制一份工程，把两处改进回退成它们修掉的那个 bug，跑 test_mode.py，
要求**恰好那几项**变红。红不了 = 那几条检查是摆设。

    回退 ①  _indent_of：多数派缩进 → 照抄第一个顶层键（插进去的键歪 8 格）
    回退 ②  current()：去掉「此刻真正渲染的是「…」」注记（status 拿设置推断冒充画面）

跑：python falsify_checks.py
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)

# 回退后必须变红的检查名（前缀匹配即可，名字里有全角符号，照抄自 test_mode.py）
EXPECT_RED = ["插进去的键跟着", "_indent_of 挑的是多数派", "照抄第一个的旧写法", "点出真正在渲染的是什么"]


def revert_indent(src):
    """_indent_of：把「取最常见缩进」换回「照抄第一个顶层键」。"""
    anchor = "    return max(counts.items(), key=lambda kv: (kv[1], len(kv[0])))[0]"
    assert anchor in src, "找不到 _indent_of 的返回行（mode.py 改过了？）"
    old = (NL.join([
        "    first = next(iter(sc), None)",
        "    if first is None:",
        '        return "    "',
        "    ln = text.rfind(chr(10), 0, sc[first][0]) + 1",
        "    seg = text[ln:ln + 40]",
        '    return seg[:len(seg) - len(seg.lstrip())] or "    "',
    ]))
    return src.replace(anchor, old)


def revert_note(src):
    """current()：删掉那行诚实注记（按形状认行，不写中文字面量）。"""
    lines = src.split(NL)
    hit = [i for i, l in enumerate(lines)
           if l.lstrip().startswith("note = ") and l.rstrip().endswith("% lab")]
    assert len(hit) == 1, "找不到注记行：%s" % hit
    del lines[hit[0]]
    return NL.join(lines)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    good = subprocess.run([sys.executable, os.path.join(HERE, "test_mode.py")],
                          capture_output=True, cwd=HERE)
    if good.returncode != 0:
        print("现行代码本身就没过，先修好再来证伪。")
        return 1

    tmp = tempfile.mkdtemp(prefix="yaobian-falsify-")
    try:
        for f in ("mode.py", "test_mode.py", "package.json"):
            shutil.copy2(os.path.join(HERE, f), os.path.join(tmp, f))
        p = os.path.join(tmp, "mode.py")
        src = io.open(p, encoding="utf-8").read()
        io.open(p, "w", encoding="utf-8", newline=NL).write(
            revert_note(revert_indent(src)))

        bad = subprocess.run([sys.executable, os.path.join(tmp, "test_mode.py")],
                             capture_output=True, cwd=tmp)
        out = bad.stdout.decode("utf-8", "replace") + bad.stderr.decode("utf-8", "replace")
        red = [l.split("✗ ", 1)[1].strip() for l in out.splitlines() if "✗ " in l]
        print("回退后变红的检查：")
        for r in red:
            print("    ✗ " + r)
        miss = [e for e in EXPECT_RED if not any(e in r for r in red)]
        if miss:
            print()
            print("有检查没红（说明它验不到那个 bug，等于没写）：%s" % miss)
            return 1
        print()
        print("✓ %d 项按预期变红，恰好覆盖两处回退（退出码 %d）" % (len(red), bad.returncode))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
