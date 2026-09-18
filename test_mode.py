# -*- coding: utf-8 -*-
"""mode.py 的自检：拿一份**仿造的** settings.json 跑，逐字节验证它只动该动的键。

为什么要仿造而不是直接拿真的 settings.json 试：真的那份里有别的东西，复制到工程目录
等于多留一份。仿造件故意做得比真的更刁钻——

  · 顶层有一个同名键藏在 `"[python]"` 语言作用域块里（层级识别错了就会改错那一个）
  · 值里有转义引号、嵌套对象、数组
  · CRLF 行尾、末尾带注释式的自定义键（模拟别人的配置）
  · 一个「绝不能被动到」的键值块（真的那份里放的是密钥，这里放占位串）

失败注入：改掉仿造件里一个**别的**键，确认「其余逐字节不动」这条检查会红。
检查不会红，等于没检查。
"""
import io
import json
import os
import subprocess
import sys

import mode  # 同目录；用来直接验 _indent_of / current 这类内部件

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "_test_settings.json")

FIXTURE = (
    '{\r\n'
    '    "editor.fontSize": 14,\r\n'
    '    "workbench.iconTheme": "material-icon-theme",\r\n'
    '    "someone.secretBlock": [\r\n'
    '        { "name": "占位", "value": "sk-PLACEHOLDER-not-a-real-key", "n": 3 }\r\n'
    '    ],\r\n'
    '    "[python]": {\r\n'
    '        "workbench.colorTheme": "SHOULD-NOT-BE-TOUCHED",\r\n'
    '        "editor.tabSize": 4\r\n'
    '    },\r\n'
    '    "escape.test": "带\\"引号\\"和\\\\反斜杠",\r\n'
    '    "workbench.colorTheme": "青瓷（深）",\r\n'
    '    "window.autoDetectColorScheme": false,\r\n'
    '    "workbench.preferredDarkColorTheme": "青瓷（深）",\r\n'
    '    "workbench.preferredLightColorTheme": "青瓷（浅）"\r\n'
    '}\r\n'
)


def run(*argv):
    p = subprocess.run([sys.executable, os.path.join(HERE, "mode.py"), *argv,
                        "--settings", FIX], capture_output=True)
    out = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
    return p.returncode, out


def only_these_keys_changed(before, after, touched):
    """把 before 里的这 touched 个键也换成 after 的值，两边应当逐字节相同。

    这是「只动了这几个键」的**充分证明**：其余部分一字节都没挪。
    """
    for k in touched:
        before, _ = mode.set_key(before, k, mode.scan_top(after)[k][3])
    return before == after


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    io.open(FIX, "w", encoding="utf-8", newline="").write(FIXTURE)
    fails = []

    def check(name, ok, extra=""):
        print(("  ✓ " if ok else "  ✗ ") + name + (("  " + extra) if extra and not ok else ""))
        if not ok:
            fails.append(name)

    print("① 只读命令不动文件")
    before = io.open(FIX, encoding="utf-8", newline="").read()
    rc, out = run("status")
    check("status 退出码 0", rc == 0, out)
    check("status 不动文件", io.open(FIX, encoding="utf-8", newline="").read() == before)
    rc, out = run("list")
    check("list 列出 36 个家族", rc == 0 and "共 36 个家族" in out, out[-200:])

    print("② auto：三个键一起改，其余逐字节不动")
    rc, out = run("auto", "湖光")
    after = io.open(FIX, encoding="utf-8", newline="").read()
    check("auto 退出码 0", rc == 0, out)
    check("auto 只动了预期的三个键",
          only_these_keys_changed(before, after,
                                  ["workbench.preferredDarkColorTheme",
                                   "workbench.preferredLightColorTheme",
                                   "window.autoDetectColorScheme"]), out)
    d = json.loads(after)
    check("preferredDark = 湖光（深）", d["workbench.preferredDarkColorTheme"] == "湖光（深）")
    check("preferredLight = 湖光（浅）", d["workbench.preferredLightColorTheme"] == "湖光（浅）")
    check("autoDetect 开了", d["window.autoDetectColorScheme"] is True)
    check("手动的 colorTheme 原样留着（这就是「记住上次」）",
          d["workbench.colorTheme"] == "青瓷（深）")
    print("③ 层级识别 + 特殊字符不被碰")
    check("[python] 块里的同名键没被动", d["[python]"]["workbench.colorTheme"] == "SHOULD-NOT-BE-TOUCHED")
    check("转义引号/反斜杠原样", d["escape.test"] == '带"引号"和\\反斜杠')
    check("别人的嵌套块原样",
          d["someone.secretBlock"] == [{"name": "占位", "value": "sk-PLACEHOLDER-not-a-real-key", "n": 3}])
    check("CRLF 行尾保住", after.count("\r\n") == FIXTURE.count("\r\n"))

    print("④ manual：继承此刻显示的深浅（此刻显示的由 --settings 那份的 colorTheme 决定）")
    rc, out = run("manual")
    d = json.loads(io.open(FIX, encoding="utf-8", newline="").read())
    check("manual 退出码 0", rc == 0, out)
    check("autoDetect 关了", d["window.autoDetectColorScheme"] is False)
    check("钉住的是青瓷（深）", d["workbench.colorTheme"] == "青瓷（深）", str(d["workbench.colorTheme"]))

    print("⑤ dark/light 指定家族")
    rc, out = run("light", "peppa")
    d = json.loads(io.open(FIX, encoding="utf-8", newline="").read())
    check("light peppa → Peppa（浅）", d["workbench.colorTheme"] == "Peppa（浅）", str(d["workbench.colorTheme"]))
    rc, out = run("dark", "claude")
    d = json.loads(io.open(FIX, encoding="utf-8", newline="").read())
    check("dark claude → Claude（深）", d["workbench.colorTheme"] == "Claude（深）", str(d["workbench.colorTheme"]))
    rc, out = run("dark", "不存在的家族")
    check("乱给家族要报错", rc != 0 and "没有这个家族" in out, out)

    print("⑥ 键缺失时插得进去，且 JSON 仍合法")
    io.open(FIX, "w", encoding="utf-8", newline="").write(
        '{\r\n    "editor.fontSize": 14\r\n}\r\n')
    rc, out = run("auto", "青瓷")
    d = json.loads(io.open(FIX, encoding="utf-8", newline="").read())
    check("三个键都插进去了",
          d["window.autoDetectColorScheme"] is True
          and d["workbench.preferredDarkColorTheme"] == "青瓷（深）"
          and d["workbench.preferredLightColorTheme"] == "青瓷（浅）", out)
    check("原有键还在", d["editor.fontSize"] == 14)

    print("⑥b 插入的键跟**大多数**顶层键对齐，不是跟第一个")
    # 真的 settings.json 就是这样：第一个顶层键缩进 8 格，其余 4 格。
    # 老写法照抄第一个 → 插进去的键歪 8 格（2026-09-18 真机上歪过一次）。
    skewed = ('{\r\n'
              '        "workbench.experimental.modernUI": "on",\r\n'
              '    "editor.fontSize": 14,\r\n'
              '    "workbench.iconTheme": "material-icon-theme"\r\n'
              '}\r\n')
    io.open(FIX, "w", encoding="utf-8", newline="").write(skewed)
    rc, out = run("auto", "青瓷")
    after = io.open(FIX, encoding="utf-8", newline="").read()
    json.loads(after)                                   # 合法性（坏了会抛）
    inserted = [l for l in after.split("\r\n")
                if l.lstrip().startswith('"window.autoDetectColorScheme"')]
    check("插进去的键跟着 4 格缩进（跟多数派）",
          len(inserted) == 1 and inserted[0].startswith('    "') and
          not inserted[0].startswith('        "'), repr(inserted))
    check("_indent_of 挑的是多数派，不是第一个",
          mode._indent_of(skewed) == "    ", repr(mode._indent_of(skewed)))
    check("（证伪）照抄第一个的旧写法在这份上会挑到 8 格",
          skewed.split("\r\n")[1][:8] == " " * 8 and mode._indent_of(skewed) != " " * 8)

    print("⑦ 失败注入：确认「其余逐字节不动」这条检查真的会红")
    b = io.open(FIX, encoding="utf-8", newline="").read()
    a = b.replace('"editor.fontSize": 14', '"editor.fontSize": 15')
    check("改掉别的键时检查变红", not only_these_keys_changed(
        b, a, ["window.autoDetectColorScheme"]))
    check("（反向）没改时检查是绿的", only_these_keys_changed(
        b, b, ["window.autoDetectColorScheme"]))

    print("⑧ 备份文件")
    check("留下了 settings.json 备份", os.path.exists(FIX + ".yaobian-bak"))

    print("⑨ 活库不是窑变时，别把设置推断冒充「此刻显示」")
    # 这一幕真发生过：提供当前主题的扩展被卸载 → VS Code 删掉 workbench.colorTheme →
    # 屏幕回落到内置主题，而设置里的槽位还是青瓷，于是 status 报「此刻显示：青瓷（浅）」。
    saved = mode.live_label
    try:
        st = {"workbench.colorTheme": "青瓷（浅）",
              "window.autoDetectColorScheme": False,
              "workbench.preferredDarkColorTheme": "青瓷（深）",
              "workbench.preferredLightColorTheme": "青瓷（浅）"}
        mode.live_label = lambda: "2026 深色"
        _, _, src = mode.current(mode.families(), st)
        check("点出真正在渲染的是什么", "此刻真正渲染的是「2026 深色」" in src, src)
        mode.live_label = lambda: "青瓷（深）"
        fam, m, src = mode.current(mode.families(), st)
        check("（反向）活库是窑变时不啰嗦", src == "正在渲染", src)
        mode.live_label = lambda: None
        _, _, src = mode.current(mode.families(), st)
        check("（反向）活库读不到时也不啰嗦", src == "设置里的手动值", src)
    finally:
        mode.live_label = saved

    print()
    print("失败 %d 项" % len(fails) + ("" if not fails else "：" + str(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
