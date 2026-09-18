# -*- coding: utf-8 -*-
"""把 cherrycss 画廊的主题铺成 VS Code 配色主题。

一条链：
    cherry.py   36 个 .ts 的 CSS  ->  每个模式一套「规范色板」（v2Compatibility 的移植）
    roles.py    规范色板          ->  67 个语义角色（青瓷量出来的公式）
    gen.py      角色向量 + 567 条角色表达式表（keyexpr.py） -> themes/*.json

青瓷走的不是公式，是**冻结向量**（build.py 里那套手调值）——本脚本最后会逐字节
比对刚生成的青瓷两套与 themes/ 里现有的文件，对不上就报错退出。
"""
import io
import json
import os
import re
import sys

import build as B
import cherry as Ch
import keyexpr as K
import palette as P
import roles as R

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "themes")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")

# 官网画廊列表里没有 starryNight（仓库里有，但要靠扩展注入的背景图，VS Code 里没有对应物）
SKIP = {"starry-night"}

# 主题 id -> (显示名, 深/浅后缀)。id 来自 cherrycss 的 theme.id
LABELS = {
    "qing-ci": "青瓷", "chang-an": "长安", "chan-zong": "禅棕", "chun-mei": "春梅",
    "dan-xia": "丹霞", "han-bai-yu": "汉白玉", "hu-guang": "湖光", "jin-xiang-yu": "金镶玉",
    "liu-yun": "流云", "pi-pa": "琵琶", "qing-hua": "青花", "qing-wu": "青雾",
    "ru-yao-lan": "汝窑蓝", "ru-yao-lv": "汝窑绿", "shan-shui": "山水", "su-xuan": "素宣",
    "tian-shui": "天水", "xuan-zhi": "宣纸", "yang-pi-zhi": "羊皮纸", "yan-hui": "雁灰",
    "yan-yu": "烟雨", "yan-zhi": "胭脂", "yao-huo": "窑火", "yu-shi": "玉石",
    "zi-tao": "紫陶", "claude": "Claude", "dopamine": "Dopamine", "dracula": "Dracula",
    "gladiia": "歌蕾蒂娅·返航", "mint": "Mint", "mo-nai": "莫奈", "mu-shan-zi": "暮山紫",
    "nai-cha": "奶茶", "peppa": "Peppa", "pulse-interactive": "Pulse",
    "vitesse-soft": "Vitesse Soft",
}


def vector_for(t, mode, cherry_roles, qc):
    """青瓷用冻结向量；别的主题用公式算，外加三个 Dk 角色 = 另一模式的同名基础角色。"""
    if t["id"] == "qing-ci":
        return qc[mode]
    v = dict(cherry_roles[t["id"]][mode])
    other = cherry_roles[t["id"]]["light" if mode == "dark" else "dark"]
    v["inkDk"], v["ink2Dk"], v["nuDk"], v["tyDk"] = (other["ink"], other["ink2"],
                                                     other["nu"], other["ty"])
    return v


def build_theme(t, mode, vec, stats):
    idx = 0 if mode == "dark" else 1
    colors = {}
    for key in B.COLORS:                       # 按 build.py 的原始顺序，保证青瓷能逐字节复原
        expr = stats["table"][key][idx]
        val = K.eval_expr(expr, vec)
        if val is None:            # 表达式就是 NONE —— 那是「关掉这条描边」，写透明
            val = "#00000000"
        if not HEX.match(val):
            raise ValueError(f"{t['id']}/{mode} {key} 非法色值 {val!r}（表达式 {expr}）")
        colors[key] = val
    label = LABELS.get(t["id"], t["id"])
    return {
        "$schema": "vscode://schemas/color-theme",
        "name": f"{label}（{'深' if mode == 'dark' else '浅'}）",
        "type": mode,
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": B.tokens(vec),
        "semanticTokenColors": B.semantic(vec),
    }


def dump(theme, path):
    io.open(path, "w", encoding="utf-8", newline="\n").write(
        json.dumps(theme, ensure_ascii=False, indent=2) + "\n")


# 清单顺序 = 官网画廊的顺序（chineseStyle 25 款在前，others 11 款在后），
# 只把青瓷提到最前 —— 它是这个扩展的本名，也是现在正在用的那套。
ORDER = [
    "qing-ci",
    "chang-an", "chan-zong", "chun-mei", "dan-xia", "han-bai-yu", "hu-guang", "jin-xiang-yu",
    "liu-yun", "pi-pa", "qing-hua", "qing-wu", "ru-yao-lan", "ru-yao-lv",
    "shan-shui", "su-xuan", "tian-shui", "xuan-zhi", "yang-pi-zhi", "yan-hui", "yan-yu",
    "yan-zhi", "yao-huo", "yu-shi", "zi-tao",
    "claude", "dopamine", "dracula", "gladiia", "mo-nai", "nai-cha", "mint",
    "vitesse-soft", "mu-shan-zi", "pulse-interactive", "peppa",
]


def write_package(themes):
    """package.json 的 contributes.themes 由主题清单直接生成（青瓷排最前，保持现用标签不变）。"""
    pkg_path = os.path.join(HERE, "package.json")
    pkg = json.load(io.open(pkg_path, encoding="utf-8"))
    ids = [t["id"] for t in themes]
    assert set(ids) == set(ORDER), set(ids) ^ set(ORDER)
    contrib = []
    for tid in ORDER:
        label = LABELS[tid]
        for mode, ui in (("dark", "vs-dark"), ("light", "vs")):
            contrib.append({
                "label": f"{label}（{'深' if mode == 'dark' else '浅'}）",
                "uiTheme": ui,
                "path": f"./themes/{tid}-{mode}.json",
            })
    pkg["contributes"]["themes"] = contrib
    pkg["version"] = "0.3.0"
    pkg["name"] = "yaobian-theme"
    # 名字就叫「窑变」，不加后缀（用户 2026-09-18 定）；英文说明走 package.nls.json，
    # 中文走 package.nls.zh-cn.json —— 商城和英文 locale 的 VS Code 读默认那份。
    pkg["displayName"] = "窑变"
    pkg["description"] = "%description%"
    pkg["keywords"] = ["theme", "color theme", "dark theme", "light theme",
                       "chinese style", "celadon", "yaobian", "qingci", "cherrycss",
                       "syntax highlighting", "semantic highlighting", "gallery",
                       "窑变", "青瓷"]
    # 跟随系统那两个槽位的**默认值**：新装的人没显式设过时，系统深色就用青瓷（深）、
    # 浅色用青瓷（浅），而不是落到 VS Code 自带的 Dark Modern。用户已显式设过的值优先。
    # （配置默认值不影响任何人现有设置，删掉扩展也会跟着消失。）
    pkg["contributes"]["configurationDefaults"] = {
        "workbench.preferredDarkColorTheme": "青瓷（深）",
        "workbench.preferredLightColorTheme": "青瓷（浅）",
    }
    io.open(pkg_path, "w", encoding="utf-8", newline="\n").write(
        json.dumps(pkg, ensure_ascii=False, indent=2) + "\n")
    n_d = sum(1 for c in contrib if c["uiTheme"] == "vs-dark")
    print(f"package.json: {len(contrib)} 套主题（深 {n_d} / 浅 {len(contrib) - n_d}），版本 0.3.0")


SAMPLE = [
    ("# 注释：青瓷开片，窑变无常", "comment"),
    ("import", "keyword"), ("  math", "variable"), ("", None),
    ("class", "keyword"), (" Celadon", "support.class"), ("(object):", None),
    ("", None),
    ('    glaze = "天青色等烟雨"', "string"),
    ("    temp = 1280", "constant.numeric"),
    ("    ratio = 0.62", "constant.numeric"),
    ("", None),
    ("    def", "keyword"), (" fire", "entity.name.function"), ("(self, kiln):", None),
    ("        return", "keyword"), (" self._glaze", "variable"),
    ("", None),
]


def write_preview(themes):
    """一个 HTML：72 套主题各来一小块「编辑器」，眼看一下配色有没有翻车。"""
    from html import escape

    def rule_for(theme, scope):
        for r in theme["tokenColors"]:
            sc = r.get("scope")
            scopes = [sc] if isinstance(sc, str) else (sc or [])
            if any(s == scope or s.startswith(scope + ".") for s in scopes):
                return r.get("settings", {}).get("foreground")
        return None

    cards = []
    for t in themes:
        for mode in ("dark", "light"):
            th = json.load(io.open(os.path.join(OUT, f"{t['id']}-{mode}.json"), encoding="utf-8"))
            c = th["colors"]
            lines = []
            for text, scope in SAMPLE:
                col = rule_for(th, scope) if scope else c["foreground"]
                lines.append(f'<div style="color:{col or c["foreground"]}">{escape(text) or "&nbsp;"}</div>')
            chips = "".join(
                f'<span class="chip" style="background:{c[k]}" title="{k} {c[k]}"></span>'
                for k in ("editor.background", "sideBar.background", "foreground",
                          "focusBorder", "editorLineNumber.foreground",
                          "editor.selectionBackground", "editorWidget.background",
                          "editorError.foreground"))
            cards.append(f'''<div class="card">
  <div class="hd">{escape(th["name"])}<span>{t["id"]}</span></div>
  <div class="win" style="background:{c["sideBar.background"]}">
    <div class="bar" style="background:{c["titleBar.activeBackground"]};color:{c["titleBar.activeForeground"]};border-color:{c["titleBar.border"]}">青瓷.py — {escape(t["id"])}</div>
    <div class="body">
      <div class="gutter" style="background:{c["editorGutter.background"]};color:{c["editorLineNumber.foreground"]}">1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10</div>
      <pre style="background:{c["editor.background"]};color:{c["foreground"]}">{''.join(lines)}</pre>
    </div>
    <div class="status" style="background:{c["statusBar.background"]};color:{c["statusBar.foreground"]}">main  ✓ 0  ⚠ 0    UTF-8   Python</div>
  </div>
  <div class="chips">{chips}</div>
</div>''')

    html = f'''<!doctype html><html lang="zh"><meta charset="utf-8">
<title>青瓷与 Cherry 主题集 — 预览</title>
<style>
 body{{background:#1b1f1e;color:#dfe7e4;font:14px/1.5 -apple-system,"Segoe UI",sans-serif;margin:0;padding:24px}}
 h1{{font-size:20px;font-weight:600;margin:0 0 4px}} p.sub{{color:#8fa39d;margin:0 0 20px}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:18px}}
 .card{{background:#232827;border:1px solid #313836;border-radius:10px;overflow:hidden}}
 .hd{{display:flex;justify-content:space-between;padding:9px 12px;font-weight:600}}
 .hd span{{color:#7f948e;font-weight:400;font-size:12px}}
 .win{{padding:0;font:12px/1.45 ui-monospace,Consolas,monospace}}
 .bar{{padding:5px 10px;border-bottom:1px solid}}
 .body{{display:flex}}
 .gutter{{padding:8px 6px 8px 10px;text-align:right;opacity:.75}}
 pre{{margin:0;padding:8px 10px;flex:1;overflow:hidden}}
 .status{{padding:4px 10px}}
 .chips{{display:flex;gap:0}}
 .chip{{flex:1;height:16px}}
</style>
<h1>青瓷与 Cherry 主题集</h1>
<p class="sub">{len(themes)} 款主题 × 深浅两套，共 {len(themes) * 2} 套；色块依次是 底色 / 侧栏 / 正文 / 主色 / 行号 / 选中 / 浮层 / 错误</p>
<div class="grid">{''.join(cards)}</div>
</html>
'''
    path = os.path.join(HERE, "preview.html")
    io.open(path, "w", encoding="utf-8", newline="\n").write(html)
    print(f"→ preview.html（{os.path.getsize(path) // 1024} KB，浏览器里看）")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT, exist_ok=True)

    # 1) 表达式表 + 青瓷冻结向量
    D, L, table, new_roles = K.build()
    bad = K.verify(D, L, table)
    if bad:
        print(f"!! 青瓷复原校验失败 {len(bad)} 条：{bad[:3]}")
        sys.exit(1)
    qc = {"dark": K.role_vector(D, L, new_roles, "D"),
          "light": K.role_vector(D, L, new_roles, "L")}
    print(f"表达式表 {len(table)} 键；青瓷冻结向量逐字节复原 ✓")

    # 2) 36 个主题的规范色板 + 角色向量
    themes = [t for t in json.load(open(os.path.join(HERE, "cherry_palettes.json"),
                                        encoding="utf-8")) if t["id"] not in SKIP]
    cherry_roles = {}
    for t in themes:
        both = {m: R.roles_for(t["modes"][m]["canonical"], m) for m in ("dark", "light")}
        cherry_roles[t["id"]] = {
            m: {k: v for k, v in both[m].items() if not k.startswith("_")}
            for m in ("dark", "light")}
    print(f"主题 {len(themes)} 个（跳过 {sorted(SKIP)}）")

    # 3) 生成
    stats = {"table": table}
    made = []
    worst = []
    for t in themes:
        for mode in ("dark", "light"):
            vec = vector_for(t, mode, cherry_roles, qc)
            theme = build_theme(t, mode, vec, stats)
            path = os.path.join(OUT, f"{t['id']}-{mode}.json")
            dump(theme, path)
            made.append((t["id"], mode, path))
            bg, ink = theme["colors"]["editor.background"], theme["colors"]["foreground"]
            c = P.contrast(ink, bg)
            if c < 4.5:
                worst.append((t["id"], mode, round(c, 2)))

    # 4) 自检：键集合一致 + 青瓷逐字节复原
    keys = set(B.COLORS)
    for tid, mode in {(a, b) for a, b, _ in made}:
        d = json.load(io.open(os.path.join(OUT, f"{tid}-{mode}.json"), encoding="utf-8"))
        assert set(d["colors"]) == keys, f"{tid}-{mode} 键集合不对"
        assert d["name"].endswith("（深）" if mode == "dark" else "（浅）"), d["name"]
    print(f"写出 {len(made)} 套；键集合 {len(keys)} 条，全部一致 ✓")
    print(f"正文对底色 < 4.5:1 的：{worst if worst else '无 ✓'}")

    # 青瓷：公式流水线生成的 qing-ci-* 必须和 build.py 手写的那两套逐字节一致。
    # （qing-ci 的 id 是 `qing-ci`，build.py 写的是 `qingci-*`，两条线各写各的文件，
    #   这里把两个文件对起来 —— 早先拿 _ref_ 快照跟 themes/qingci-* 比，比的是同一个
    #   文件、等于没比，两条线其实有 2 个键不一样。）
    for mode in ("dark", "light"):
        gen_p = os.path.join(OUT, f"qing-ci-{mode}.json")
        hand_p = os.path.join(OUT, f"qingci-{mode}.json")
        snap_p = os.path.join(HERE, f"_ref_qingci-{mode}.json")
        gen = io.open(gen_p, encoding="utf-8").read()
        hand = io.open(hand_p, encoding="utf-8").read()
        assert hand == io.open(snap_p, encoding="utf-8").read(), \
            f"build.py 输出与 _ref_ 快照不一致（手调基准被改过？）"
        assert gen == hand, f"青瓷 {mode}：流水线与手写版不一致！"
        print(f"  qing-ci-{mode}.json {len(gen)} 字节 = 手写版 {len(hand)} 字节 ✓（基准快照未变）")
    # 5) 清单 + 预览
    write_package(themes)
    write_preview(themes)
    return made


if __name__ == "__main__":
    main()
