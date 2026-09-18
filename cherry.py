# -*- coding: utf-8 -*-
"""从 cherrycss 仓库的 36 个主题 .ts 里抽出「每个模式一套的规范色板」。

这是 lib/themes/v2Compatibility.ts 的 Python 移植（readPaletteRoots / DEFAULT_SOURCES /
THEME_V2_PROFILES / compileMode），差别只有一个：那边产出 var() 引用，我这边直接产出
解析好的色值 —— 我要拿它去算角色向量，不需要中间那层引用。

解析用「括号配深」的扫描器，而不是 `([^{}]+)\{([^{}]*)\}` 这种正则：
vitesseSoft 在 body[theme-mode=dark] 里嵌了 `.ant-* { … }`，正则会被内层大括号噎死。
"""
import json
import os
import re
import sys

import palette as P

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\temp\cherrycss\lib\themes"

# canonical 名 -> 候选源变量（与 DEFAULT_SOURCES 一一对应）
DEFAULT_SOURCES = {
    "background": ["--color-background", "--chat-background"],
    "foreground": ["--color-text", "--color-text-1"],
    "card": ["--chat-background-assistant", "--color-background-soft", "--color-background"],
    "primary": ["--color-primary"],
    "secondary": ["--color-background-soft"],
    "muted": ["--color-background-mute", "--color-background-soft"],
    "muted-foreground": ["--color-text-2", "--color-text", "--color-text-1"],
    "accent": ["--color-hover", "--color-background-soft"],
    "border": ["--color-border"],
    "input": ["--color-border"],
    "sidebar": ["--navbar-background"],
    "sidebar-accent": ["--color-active", "--color-hover"],
    "background-subtle": ["--color-background-mute", "--color-background-soft"],
    "foreground-tertiary": ["--color-text-3", "--color-text-2"],
    "border-subtle": ["--color-border-soft", "--color-border"],
    "border-strong": ["--color-border"],
    "error": ["--color-error"],
    "link": ["--color-link"],
    "code-block": ["--color-code-background"],
    "reference": ["--color-reference"],
    "reference-foreground": ["--color-reference-text"],
    "reference-subtle": ["--color-reference-background"],
    "chat-user": ["--chat-background-user"],
}

SURFACE_PAIRS = [
    ("card", "card-foreground"),
    ("secondary", "secondary-foreground"),
    ("muted", "muted-foreground"),
    ("accent", "accent-foreground"),
    ("sidebar", "sidebar-foreground"),
    ("sidebar-accent", "sidebar-accent-foreground"),
]

# 只搬「源变量重定向」和 primaryForeground 这两类；rules 是 Cherry Studio 专属的 DOM 补丁，
# VS Code 里没有对应物，忽略。
PROFILES = {
    "su-xuan": {},
    "chun-mei": {}, "liu-yun": {}, "qing-wu": {}, "ru-yao-lan": {}, "ru-yao-lv": {},
    "tian-shui": {}, "yang-pi-zhi": {}, "yan-yu": {}, "yan-zhi": {}, "yao-huo": {},
    "yu-shi": {}, "mo-nai": {}, "nai-cha": {}, "mu-shan-zi": {}, "gladiia": {},
    "peppa": {"sources": {
        "background": ["--display-4"], "foreground": ["--stroke-black"],
        "card": ["--chat-background-assistant"], "primary": ["--pig-accent"],
        "border": ["--stroke-black"], "input": ["--stroke-black"],
        "sidebar": ["--navbar-background"], "chat-user": ["--chat-background-user"]}},
    "starry-night": {"primaryForeground": "--text-on-brand", "sources": {
        "background": ["--color-background-base"], "foreground": ["--text-primary"],
        "card": ["--bg-element-soft"], "primary": ["--color-brand-primary"],
        "secondary": ["--bg-element-soft"], "muted": ["--bg-element-mute"],
        "accent": ["--bg-element-primary"], "border": ["--border-color"],
        "input": ["--border-color"], "sidebar": ["--bg-element-soft"],
        "sidebar-accent": ["--bg-element-primary"], "background-subtle": ["--bg-element-mute"],
        "border-subtle": ["--border-color"], "border-strong": ["--border-hover-color"],
        "chat-user": ["--bg-element-primary"]}},
    "pulse-interactive": {"sources": {
        "background": {"light": ["--background-light-new"], "dark": ["--background-dark-new"]},
        "card": {"light": ["--background-assistant-light-new"], "dark": ["--background-dark-new"]},
        "primary": {"light": ["--button-hover-light"], "dark": ["--button-hover-dark"]},
        "accent": {"light": ["--button-hover-light"], "dark": ["--button-hover-dark"]},
        "chat-user": {"light": ["--chat-background-user-light"],
                      "dark": ["--chat-background-user-dark"]}}},
}


# ---------- CSS 解析（配深扫描，等价 postcss.walkRules） ----------

def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def walk_rules(css):
    """产出 (selector, {prop: value})，任意深度都算（和 postcss.walkRules 一样），
    但只取本层直接声明的变量，不进子规则。"""
    css = strip_comments(css)
    i, n = 0, len(css)
    stack = []          # 当前规则链：[(selector, {decls}), ...]
    out = []
    buf = ""
    while i < n:
        ch = css[i]
        if ch == "{":
            selector = buf.strip()
            rule = (selector, {})
            stack.append(rule)
            buf = ""
        elif ch == "}":
            if stack:
                sel, decls = stack.pop()
                out.append((sel, decls))
            buf = ""
        elif ch == ";":
            if buf.strip():
                decl = buf.strip()
                m = re.match(r"(--[A-Za-z0-9_-]+)\s*:\s*(.*)$", decl, re.S)
                if m and stack:
                    val = m.group(2).strip()
                    val = re.sub(r"\s*!\s*important\s*$", "", val)   # postcss 会把 important 单独放
                    stack[-1][1][m.group(1)] = val
            buf = ""
        else:
            if ch == "\n" and not buf.strip():
                pass
            buf += ch
        i += 1
    if stack:
        sel, decls = stack.pop()
        out.append((sel, decls))
    return out


MODE_SEL = re.compile(r"""^body\[theme-mode=(?:(["'])(light|dark)\1|(light|dark))\]$""")


def read_palette_roots(css):
    out = {"root": {}, "light": {}, "dark": {}}
    for sel, decls in walk_rules(css):
        sel = sel.strip()
        if sel == ":root":
            target = "root"
        else:
            m = MODE_SEL.match(sel)
            target = (m.group(2) or m.group(3)) if m else None
        if not target:
            continue
        out[target].update(decls)
    return out


def merge_mode(root, mode):
    d = dict(root)
    d.update(mode)
    return d


def resolve_value(palette, name, seen=()):
    if name in seen:
        raise ValueError(f"循环引用 {name}")
    if name not in palette:
        raise ValueError(f"变量不存在 {name}")
    val = palette[name]
    return re.sub(r"var\(\s*(--[A-Za-z0-9_-]+)(?:\s*,[^)]*)?\s*\)",
                  lambda m: resolve_value(palette, m.group(1), seen + (name,)), val)


def profile_candidates(profile, canonical, mode):
    cfg = (profile.get("sources") or {}).get(canonical)
    if not cfg:
        return DEFAULT_SOURCES[canonical]
    if isinstance(cfg, list):
        return cfg
    return cfg.get(mode, [])


def choose_source(palette, candidates, required):
    for c in candidates:
        if c in palette:
            return c
    if required:
        raise ValueError(f"profile 指定的源变量缺失: {candidates}")
    return None


def choose_primary_foreground(palette, primary_source):
    prim = P.norm(resolve_value(palette, primary_source))
    if not prim or len(prim) > 7:
        raise ValueError(f"{primary_source} 不是实色")
    best = None
    for name in sorted(palette):
        try:
            v = resolve_value(palette, name)
        except ValueError:
            continue
        c = P.norm(v)
        if not c or len(c) > 7:
            continue
        score = P.contrast(prim, c)
        if best is None or score > best[1]:
            best = (name, score)
    if not best:
        raise ValueError(f"没有能和 {primary_source} 配的实色")
    return best[0]


def compile_mode(theme_id, mode, palette, profile):
    canonical = {}
    configured = set((profile.get("sources") or {}).keys())
    warns = []
    for name, _ in DEFAULT_SOURCES.items():
        cands = profile_candidates(profile, name, mode)
        required = name in configured
        src = choose_source(palette, cands, required)
        if not src:
            warns.append(f"{mode}: 缺 {name}（试过 {','.join(cands)}）")
            continue
        val = resolve_value(palette, src)
        if not P.is_color(val):
            # 非颜色（transparent / 渐变 / unknown 关键字）：不算错，交给 fill_missing 补
            warns.append(f"{mode}: {name} 拿到的是 {val!r}，当缺失处理")
            continue
        canonical[name] = P.norm(val)

    fg = canonical.get("foreground")
    if "card" in canonical and fg:      # 正文本身缺的话交给 fill_missing 补，别写 None 进去
        canonical["card-foreground"] = fg
        canonical["popover"] = canonical["card"]
        canonical["popover-foreground"] = fg
    if "primary" in canonical:
        src = choose_source(palette, profile_candidates(profile, "primary", mode), True)
        pfg_src = profile.get("primaryForeground")
        if not pfg_src:
            pfg_src = choose_primary_foreground(palette, src)
        canonical["primary-foreground"] = P.norm(resolve_value(palette, pfg_src))
        canonical["ring"] = canonical["primary"]
    for surface, partner in SURFACE_PAIRS:
        if surface in canonical and partner not in canonical and fg:
            canonical[partner] = fg
    if "sidebar" in canonical:
        if "primary" in canonical:
            canonical["sidebar-primary"] = canonical["primary"]
            canonical["sidebar-primary-foreground"] = canonical["primary-foreground"]
            canonical["sidebar-ring"] = canonical["ring"]
        if "border" in canonical:
            canonical["sidebar-border"] = canonical["border"]
    return canonical, warns


def _try(palette, name):
    try:
        return resolve_value(palette, name)
    except ValueError:
        return None


def fill_missing(canonical, palette, mode):
    """源主题没给的规范色，用「底色 + 正文」推出来。

    公式对深浅两套是同一条：mix(bg, fg, t) 在深色里是提亮、浅色里是压暗，
    方向由 fg 自己站在哪一端决定，不用分支。
    返回补出来的键名列表（供报告用，别假装是原主题给的）。
    """
    filled = []

    def put(k, v):
        canonical[k] = v
        filled.append(k)

    def pick(*cands):
        for c in cands:
            v = P.norm(_try(palette, c) or "")
            if v and len(v) == 7:
                return v
        return None

    if "background" not in canonical:
        put("background", pick("--color-background-soft", "--chat-background",
                               "--chat-background-white", "--color-white",
                               "--color-white-soft", "--color-black-soft", "--color-black")
            or ("#F0F5F3" if mode == "light" else "#1F2428"))
    bg = canonical["background"]

    if "foreground" not in canonical:
        fg = pick("--color-text", "--color-text-1", "--chat-text-user",
                  "--color-white", "--color-white-soft", "--color-black-soft", "--color-black")
        if not fg or P.contrast(fg, bg) < 4.5:
            # 调色板里找「读得清」的：先要够对比，再挑最不花的那支（正文不该是红的）
            cands = []
            for name in sorted(palette):
                c = P.norm(_try(palette, name) or "")
                if c and len(c) == 7 and P.contrast(c, bg) >= 4.5:
                    cands.append((P.to_oklch(c)[1], -P.contrast(c, bg), c))
            cands.sort()
            fg = cands[0][2] if (cands and cands[0][0] <= 0.06) else None
        if not fg:
            # 没有中性色可用（全彩的主题、或全灰调色板）：按底色推一个
            fg = P.setL(bg, 0.16) if mode == "light" else P.setL(bg, 0.94)
        put("foreground", fg)
    fg = canonical["foreground"]

    def tone(t):
        return P.fix_contrast(P.mix(bg, fg, t), bg, 4.5)

    surfaces = [
        ("card", 0.045), ("secondary", 0.06), ("muted", 0.09), ("accent", 0.12),
        ("background-subtle", 0.09), ("sidebar", 0.03), ("sidebar-accent", 0.12),
        ("code-block", 0.07), ("reference-subtle", 0.07),
    ]
    for name, t in surfaces:
        if name not in canonical:
            put(name, P.mix(bg, fg, t))
    for name, t in (("border", 0.22), ("input", 0.22), ("border-subtle", 0.13),
                    ("border-strong", 0.32)):
        if name not in canonical:
            put(name, P.mix(bg, fg, t))
    for name, t in (("muted-foreground", 0.42), ("foreground-tertiary", 0.55)):
        if name not in canonical:
            put(name, tone(t))
    for name, t in (("card-foreground", 0.0), ("popover-foreground", 0.0),
                    ("secondary-foreground", 0.0), ("muted-foreground", 0.0),
                    ("accent-foreground", 0.0), ("sidebar-foreground", 0.0),
                    ("sidebar-accent-foreground", 0.0), ("reference-foreground", 0.0)):
        if name not in canonical:
            put(name, fg)
    if "popover" not in canonical:
        put("popover", canonical.get("card", P.mix(bg, fg, 0.045)))
    if "chat-user" not in canonical:
        put("chat-user", canonical.get("accent", P.mix(bg, fg, 0.12)))

    if "primary" not in canonical:
        prim = pick("--color-primary", "--color-accent", "--pig-accent")
        if not prim:
            # 挑调色板里最有彩度的那支（主题的「主色」一般是它）
            best = None
            for name in sorted(palette):
                c = P.norm(_try(palette, name) or "")
                if c and len(c) == 7:
                    _, chroma, _ = P.to_oklch(c)
                    if best is None or chroma > best[1]:
                        best = (c, chroma)
            prim = best[0] if best and best[1] >= 0.04 else None
        if not prim:
            prim = P.fix_contrast(P.mix(fg, bg, 0.5), bg, 3.0)
        put("primary", prim)
    if "link" not in canonical:
        put("link", canonical["primary"])
    if "reference" not in canonical:
        put("reference", P.alpha(canonical["primary"], 0x33))
    if "ring" not in canonical:
        put("ring", canonical["primary"])
    if "primary-foreground" not in canonical:
        put("primary-foreground", P.fix_contrast(fg, canonical["primary"], 4.5))
    if "sidebar-primary" not in canonical:
        put("sidebar-primary", canonical["primary"])
        put("sidebar-primary-foreground", canonical["primary-foreground"])
        put("sidebar-ring", canonical["ring"])
    if "sidebar-border" not in canonical:
        put("sidebar-border", canonical["border"])
    return filled


SURFACE_KEYS = {
    "background", "card", "secondary", "muted", "accent", "background-subtle",
    "sidebar", "sidebar-accent", "code-block", "reference-subtle", "popover",
    "input", "chat-user",
}
TEXT_KEYS = {
    "foreground", "muted-foreground", "foreground-tertiary", "card-foreground",
    "popover-foreground", "secondary-foreground", "accent-foreground",
    "sidebar-foreground", "sidebar-accent-foreground", "reference-foreground",
    "primary-foreground",
}
ACCENT_KEYS = {"primary", "link", "reference", "ring", "sidebar-primary", "sidebar-ring"}


def invert_mode(canonical):
    """只给了一套（:root）的主题 —— 比如 Dracula 上游就一个 #282A36 的暗色 ——
    按明度重锚出另一套：面往另一端摊开、文字压到对面、彩色保住色相只压明度。

    保留 alpha：半透明的正文在对面底色上仍然成立。
    """
    import re as _re

    def alpha_of(v):
        return v[7:] if len(v) == 9 else ""

    surf = {k: P.to_oklch(v)[0] for k, v in canonical.items() if k in SURFACE_KEYS}
    text = {k: P.to_oklch(v)[0] for k, v in canonical.items() if k in TEXT_KEYS}
    smin, smax = (min(surf.values()), max(surf.values())) if surf else (0, 1)
    tmin, tmax = (min(text.values()), max(text.values())) if text else (0, 1)
    span = lambda x, lo, hi: 0.0 if hi - lo < 1e-6 else (x - lo) / (hi - lo)

    out = {}
    for k, v in canonical.items():
        L, C, H = P.to_oklch(v)
        a = alpha_of(v)
        if k in SURFACE_KEYS:
            L2 = 0.975 - span(L, smin, smax) * 0.16      # 最深的面 -> 最亮
        elif k in TEXT_KEYS:
            L2 = 0.34 - span(L, tmin, tmax) * 0.10        # 最亮的字 -> 最黑
        elif k in ACCENT_KEYS:
            L2 = min(max(L, 0.42), 0.60)
        else:
            L2 = 1.0 - L
        out[k] = P.oklch_hex((L2, min(C, 0.30), H), int(a, 16) / 255 if a else None)
    bg = out.get("background")
    for k in TEXT_KEYS:
        if k in out and bg:
            out[k] = P.fix_contrast(P.opaque(out[k]), bg, 4.5)
    for k in ACCENT_KEYS:
        if k in out and bg:
            out[k] = P.fix_contrast(P.opaque(out[k]), bg, 3.0)
    for k in ("border", "border-subtle", "border-strong"):
        if k in out and bg:
            out[k] = P.mix(bg, out.get("foreground", "#000000"), 0.22 if k == "border" else
                           (0.14 if k == "border-subtle" else 0.32))
    return out


# ---------- 读取主题 .ts ----------

def read_theme_file(path, group):
    src = open(path, encoding="utf-8").read()

    def field(name):
        m = re.search(rf"^\s*{name}:\s*(['\"])(.*?)\1,\s*$", src, re.M)
        return m.group(2) if m else None

    m = re.search(r"css:\s*`(.*)`\s*,?\s*\}\s*$", src, re.S)
    if not m:
        raise ValueError(f"{path}: 抽不出 css")
    css = m.group(1)
    # 反引号里若有 ${...} 插值，说明是模板动态生成的，得单独看
    return {
        "file": os.path.basename(path),
        "group": group,
        "id": field("id"),
        "name": field("name"),
        "desc": field("description"),
        "css": css,
    }


def all_themes():
    out = []
    for group in ("chineseStyle", "others"):
        d = os.path.join(SRC, group)
        for fn in sorted(os.listdir(d)):
            if fn == "index.ts" or not fn.endswith(".ts"):
                continue
            out.append(read_theme_file(os.path.join(d, fn), group))
    return out


def build_theme(t):
    pal = read_palette_roots(t["css"])
    profile = PROFILES.get(t["id"], {})
    rec = {"id": t["id"], "name": t["name"], "file": t["file"], "group": t["group"],
           "desc": t["desc"], "warns": [], "notes": [], "modes": {}, "inverted": []}
    root_only = not pal["light"] and not pal["dark"] and len(pal["root"]) > 5
    for mode in ("light", "dark"):
        merged = merge_mode(pal["root"], pal[mode])
        if not pal[mode] and not profile.get("sources"):
            rec["notes"].append(f"{mode}: 源文件没有这个模式的块")
        canonical, warns = compile_mode(t["id"], mode, merged, profile)
        filled = fill_missing(canonical, merged, mode)
        rec["modes"][mode] = {"vars": merged, "canonical": canonical, "filled": filled}
        rec["warns"] += warns

    if root_only:
        # 上游只给了一套（通常就是暗色）：判断它是哪一端，另一端用重锚反推
        bg = rec["modes"]["dark"]["canonical"]["background"]
        src = "dark" if P.to_oklch(bg)[0] < 0.5 else "light"
        other = "light" if src == "dark" else "dark"
        rec["modes"][other]["canonical"] = invert_mode(rec["modes"][src]["canonical"])
        rec["inverted"] = [src + "→" + other]
    return rec


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    res = []
    for t in all_themes():
        try:
            r = build_theme(t)
        except Exception as e:
            print(f"!! {t['file']:<20} {type(e).__name__}: {e}")
            continue
        res.append(r)
        f = r["modes"]["light"]["filled"]
        hard = [w for w in r["warns"] if "不是颜色" not in w]
        print(f"{r['id']:<18}{r['name']:<10} 变量 {len(r['modes']['dark']['vars']):>2}"
              f"  补键 {len(f):>2}: {','.join(f[:8])}{'…' if len(f) > 8 else ''}"
              + (f"   ⚠ {'; '.join(hard[:2])}" if hard else ""))
    json.dump(res, open(os.path.join(HERE, "cherry_palettes.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(res)} 个主题 → cherry_palettes.json")
