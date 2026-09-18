# -*- coding: utf-8 -*-
"""规范色板 → 角色向量（67 个语义角色）。

青瓷的那一套是手调出来的、已经定稿，所以它的向量是**冻结**的（keyexpr.json 里存了）。
其它主题走这里的公式。公式不是拍脑袋定的，是**从青瓷身上量出来的**：

  把青瓷的每个角色换算到 OKLCH，相对 prim（釉色 #7BA898, H=170.7, C=0.054）看，
  语法色的色相偏移和彩度比在两个模式下高度一致 —— 于是「旋色相 + 按比例缩放彩度 +
  按底色平移明度」就能把一个主题的强调色铺成整套语法色：

      角色    ΔH(相对 prim)   彩度比    深色 L    浅色 L
      kw         +3.1        1.17     0.786     0.499
      fn         +0.8        0.83     0.893     0.553
      ty        +55.0        0.90     0.795     0.478
      tyL       +53.2        0.67     0.846     0.467
      st        -78.5        0.96     0.796     0.486
      nu       -121.0        1.24     0.721     0.536
      pl       +174.8        0.73     0.746     0.518
      cm         +7.5        0.43     0.640     0.589
      err      -141.0        1.85     0.711     0.540

明度先按「底色比青瓷的深/浅多少」整体平移，再过一道 WCAG 4.5:1 兜底：
不管主题多极端，正文级的角色都不会糊在底色上。
"""
import palette as P

# 青瓷量出来的参考值
REF_BG_L = {"dark": 0.323, "light": 0.966}
SYNTAX = {
    #       ΔH      C比    深色L   浅色L   最低对比
    "kw":  (3.1,  1.17, 0.786, 0.499, 4.5),
    "fn":  (0.8,  0.83, 0.893, 0.553, 4.5),
    "ty":  (55.0, 0.90, 0.795, 0.478, 4.5),
    "tyL": (53.2, 0.67, 0.846, 0.467, 4.5),
    "st":  (-78.5, 0.96, 0.796, 0.486, 4.5),
    "nu":  (-121.0, 1.24, 0.721, 0.536, 4.5),
    "pl":  (174.8, 0.73, 0.746, 0.518, 4.5),
    "cm":  (7.5,  0.43, 0.640, 0.589, 3.5),
    "err": (-141.0, 1.85, 0.711, 0.540, 4.5),
}
# 调色板里没给出「彩色」时（素宣那种全灰主题），给语法色一个最低彩度，别整片灰
MIN_C = 0.055

# 语义四色：**色相不跟强调色转**，锚在青瓷定稿的那四个上
# （错误≈30°红、警告≈90°黄、信息≈223°蓝、通过≈173°青绿）。
# 语法色可以随主题的强调色漂移，语义色不行——禅棕的强调色是棕色，按 ΔH 旋 −141°
# 会得到「蓝色的报错、紫色的警告」，界面上一眼就不对。彩度/明度仍跟着主题走。
SEM = {
    #        色相    彩度比   深色L    浅色L    对比度下限
    "err":  (29.5, 1.85, 0.711, 0.540, 4.5),
    "warn": (90.4, 1.35, 0.645, 0.645, 4.5),
    "info": (223.5, 0.90, 0.665, 0.665, 4.5),
    "pos":  (172.7, 1.00, 0.601, 0.601, 3.5),
}
SEM_C_MAX = 0.24          # 语义色别做成荧光（dopamine 那种高彩度强调色会顶到这儿）

# 设计上就该半透明的角色：选中态的四档、半透明分隔线。其余一律压成实色。
TRANSLUCENT = {"lineA", "sel", "selm", "sels", "selx"}

BASE_ROLES = ("bg", "pane", "tab", "surf", "ink", "ink2", "ink3", "line", "lineA", "q4", "q5",
              "ctrl", "prim", "azure", "acc", "acc2", "sel", "selm", "sels", "selx",
              "kw", "fn", "ty", "tyL", "st", "nu", "pl", "cm", "err", "jade", "pale")


def is_dark(mode):
    return mode == "dark"


def comp(c, bg):
    """把半透明色压到底色上，得到它在那个底色上的实际观感（实色）。"""
    r, g, b, a = P.parse(c)
    if a >= 0.999:
        return P.opaque(c)
    return P.mix(bg, P.opaque(c), a)


def shift(c, dL):
    L, C, H = P.to_oklch(c)
    return P.oklch_hex((max(0.0, min(1.0, L + dL)), C, H))


def setl(c, L):
    return P.setL(c, max(0.0, min(1.0, L)))


def setc(c, k):
    """彩度乘 k，并保证不低于 MIN_C（除非原色几乎没彩度）。"""
    L, C, H = P.to_oklch(c)
    return P.oklch_hex((L, max(C * k, MIN_C if C < MIN_C else C * k), H))


def syn(canonical, mode):
    """语法色：旋 prim 的色相、按比例缩彩度、按底色平移明度。"""
    bg = canonical["background"]
    prim = canonical["primary"]
    Hp, Cp = P.to_oklch(prim)[2], P.to_oklch(prim)[1]
    bgL = P.to_oklch(bg)[0]
    dL = bgL - REF_BG_L[mode]
    out = {}
    for name, (dH, ck, Ld, Ll, target) in SYNTAX.items():
        L0 = Ld if is_dark(mode) else Ll
        H = (Hp + dH) % 360
        C = max(Cp * ck, MIN_C)
        c = P.oklch_hex((max(0.0, min(1.0, L0 + dL)), min(C, 0.28), H))
        out[name] = P.fix_contrast(c, bg, target)
    return out


def tier(ink, bg, t, floor):
    """从正文往底色方向退一档（在 OKLCH 明度上退），再过对比度底线。

    t 是从青瓷身上量的：它的 ink2 在明度上退了 28%，ink3 退了 48%。
    """
    Li, Ci, Hi = P.to_oklch(ink)
    Lb = P.to_oklch(bg)[0]
    return P.fix_contrast(P.oklch_hex((max(0.0, min(1.0, Li + (Lb - Li) * t)), Ci, Hi)),
                          bg, floor)


def sem_colors(canonical, mode):
    """语义四色：色相固定（SEM），彩度按强调色的比例、明度按底色平移。"""
    bg = canonical["background"]
    Cp = P.to_oklch(canonical["primary"])[1]
    bgL = P.to_oklch(bg)[0]
    dL = bgL - REF_BG_L[mode]
    out = {}
    for name, (H, ck, Ld, Ll, target) in SEM.items():
        L0 = Ld if is_dark(mode) else Ll
        c = P.oklch_hex((max(0.0, min(1.0, L0 + dL)),
                         max(min(Cp * ck, SEM_C_MAX), MIN_C), H))
        out[name] = P.fix_contrast(c, bg, target)
    return out


def roles_for(C, mode):
    """C：某个模式的规范色板（cherry.py 的 canonical）。返回完整角色向量。"""
    dark = is_dark(mode)

    # ---- 0) 输入先实色化 ----
    # 上游有的主题在 :root 里就把正文/底色写成半透明（清雾的 --color-text 是 95%，
    # 好几个主题的 --navbar-* 是 rgba(...)）。不压掉的话会一路渗进
    # editor.background / titleBar / activityBar —— 半透明的编辑器底色是灾难。
    # 压到「主题自己的底色」上：这才是它在 Cherry Studio 里的实际观感。
    base = comp(C["background"], "#000000" if dark else "#FFFFFF")
    C = dict(C)
    C["background"] = base
    for k, v in list(C.items()):
        if isinstance(v, str):
            try:
                C[k] = comp(v, base)
            except Exception:
                pass
    bg = base
    fg = C["foreground"]
    r = {}

    # ---- 面：底色 / 侧栏 / 标签 / 浮层 / 填充档 ----
    r["bg"] = bg
    r["pane"] = comp(C.get("sidebar") or P.mix(bg, fg, 0.04), bg)
    r["surf"] = comp(C.get("card") or P.mix(bg, fg, 0.05), bg)
    r["tab"] = P.mix(bg, fg, 0.055)
    r["q4"] = comp(C.get("muted") or P.mix(bg, fg, 0.09), bg)
    r["q5"] = comp(C.get("background-subtle") or P.mix(bg, fg, 0.07), bg)
    r["ctrl"] = P.mix(bg, "#FFFFFF", 0.85 if dark else 0.60)

    # ---- 文字三档 ----
    # 次级/三级文字：源里有独立来源就用，但必须是**比正文暗一档**的独立来源。
    # 大部分 v1 主题没有 --color-text-2，回退链会一路退到 --color-text，
    # 「次级文字」于是变成正文本身 —— 72 套里 60 套的注释和正文一样亮。
    r["ink"] = P.fix_contrast(fg, bg, 4.5)
    ci = P.contrast(r["ink"], bg)

    def pick_tier(src, t, floor):
        if src:
            c = comp(src, bg)
            k = P.contrast(c, bg)
            if ci * 0.45 <= k <= ci * 0.95:      # 是一个合理的「暗一档」
                return P.fix_contrast(c, bg, floor), True
        return tier(r["ink"], bg, t, floor), False

    mf = C.get("muted-foreground")
    # 底线跟着正文的可达对比度走：清雾/莫奈这种底色本身是中调的，
    # 硬卡 4.5 会把「次级文字」顶回正文那一档，三档又塌成一档。
    floor2 = min(4.5, max(3.0, ci * 0.72))
    floor3 = min(3.0, max(2.2, ci * 0.50))
    r["ink2"], used2 = pick_tier(mf if mf and mf.upper() != fg.upper() else None, 0.28, floor2)
    f3 = C.get("foreground-tertiary")
    r["ink3"], used3 = pick_tier(f3 if f3 and f3.upper() != fg.upper() else None, 0.48, floor3)
    if P.contrast(r["ink3"], bg) >= P.contrast(r["ink2"], bg) * 0.98:
        r["ink3"] = tier(r["ink2"], bg, 0.35, floor3)     # 三档必须一档比一档暗
    if not (used2 and used3):                      # 记一笔：这套的次级文字是推出来的
        r["_tier_synth"] = (used2, used3)
    r["pale"] = P.fix_contrast(P.mix(r["ink"], bg, 0.22), bg, 4.5)

    # ---- 线 ----
    line = comp(C.get("border") or P.mix(bg, fg, 0.22), bg)
    if P.contrast(line, bg) < 1.10:                 # 太虚的描边在列表里等于没有
        line = P.mix(bg, fg, 0.16)
    # 分隔线不该和正文一样抢眼。peppa 的源色板把 `--color-border` 直接写成正文色
    # （深色 #ECECEC / 浅色 #000000），line 于是等于 ink —— 而 line 有几处是当**底色**
    # 用的（button.secondaryBackground），正文色压上去正好 1:1，字直接消失。
    # 青瓷的 line 对底色只有 1.2–1.5（约 ink 的 12%），这里按 ink 的 28% 封顶，
    # 只碰越界的那一套；往底色里混、保色相，二分找刚好卡到上限的混比。
    cap = max(1.35, P.contrast(r["ink"], bg) * 0.28)
    if P.contrast(line, bg) > cap:
        lo, hi = 0.0, 1.0
        for _ in range(24):
            mid = (lo + hi) / 2
            if P.contrast(P.mix(bg, line, mid), bg) > cap:
                hi = mid
            else:
                lo = mid
        line = P.mix(bg, line, lo)
    r["line"] = line
    r["lineA"] = P.alpha(r["ink"], 0x26 if dark else 0x1F)

    # ---- 强调色族 ----
    # 有些主题的强调色和底色几乎同色（禅棕的棕、长安的朱在深底上只有 1.4:1），
    # VS Code 里 prim 要当焦点框、徽章底色用，糊在一起就是「看不见」。
    # 只推明度、保色相，下限 2.5:1，并在报告里点名。
    prim_raw = comp(C["primary"], bg)
    prim = P.fix_contrast(prim_raw, bg, 2.5)
    if prim != prim_raw:
        r["_prim_nudged"] = prim_raw
    r["prim"] = prim
    r["azure"] = setl(prim, P.to_oklch(prim)[0] + 0.07)
    r["acc"] = P.fix_contrast(prim, bg, 4.5)
    r["acc2"] = P.fix_contrast(prim, bg, 7.0)
    r["jade"] = setl(r["azure"], P.to_oklch(prim)[0] + 0.0) if dark \
        else P.fix_contrast(setl(r["azure"], P.to_oklch(prim)[0] - 0.05), bg, 3.0)
    selb = prim if P.contrast(prim, bg) >= 2.0 else P.mix(prim, fg, 0.30)
    for name, a in (("sel", 0x52 if dark else 0x47), ("selm", 0x4D if dark else 0x40),
                    ("sels", 0x26 if dark else 0x1F), ("selx", 0x14 if dark else 0x0F)):
        r[name] = P.alpha(selb, a)

    # ---- 语法色 ----
    s = syn(C, mode)
    r.update(s)

    # ---- 错误 / 警告 / 提示 / 通过 四族（终端色 + 校验框 + 装饰） ----
    # 上游给了 --color-error 就用它的（dracula 这类 v1 主题有），没有就用锚定的色相
    sem = sem_colors(C, mode)
    r["err"] = P.fix_contrast(comp(C["error"], bg), bg, 4.5) if C.get("error") else sem["err"]
    err, prim = r["err"], r["prim"]
    r["errSoft"] = P.fix_contrast(P.soft(err, 0.13), bg, 3.5)
    r["errHi"] = P.fix_contrast(shift(err, 0.10), bg, 4.5)
    r["errDeep"] = shift(err, -0.13)
    # 三个 *Pale 是 inputValidation 的三个校验框底色，框里的字是 `bg`（模式的两端色）。
    # 所以它是「中间调」而不是「贴近底色的淡色」：往正文那一侧混，保证框里的字看得见。
    # （青瓷自己这套是 fg=bg / bg=errPale，深色模式靠 err 本身够亮才成立。）
    r["errPale"] = P.fix_contrast(P.mix(err, r["ink"], 0.55), bg, 3.5)
    r["errBrown"] = P.fix_contrast(P.mix(err, r["nu"], 0.55), bg, 4.5)

    warn = sem["warn"]
    r["warn"] = warn
    r["warnHi"] = P.mix(warn, "#FFFFFF", 0.45)
    r["warnPale"] = P.fix_contrast(P.mix(warn, r["ink"], 0.55), bg, 3.5)
    r["warnDeep"] = shift(warn, -0.13)

    info = sem["info"]
    r["info"] = info
    r["infoHi"] = P.mix(info, "#FFFFFF", 0.40)
    r["infoPale"] = P.fix_contrast(P.mix(info, r["ink"], 0.55), bg, 3.5)
    r["infoDeep"] = shift(info, -0.13)

    pos = sem["pos"]
    r["posMid"] = pos
    r["posLo"] = P.fix_contrast(shift(pos, -0.09), bg, 3.0)
    r["posHi"] = P.mix(pos, "#FFFFFF", 0.28) if dark else P.mix(pos, bg, 0.22)
    r["posDeep"] = shift(pos, -0.12)
    L, Cc, H = P.to_oklch(pos)
    r["posCyan"] = P.fix_contrast(P.oklch_hex((L, Cc, (H + 14) % 360)), bg, 3.5)

    # ---- 中性阶梯（滚动条 / 忽略的文件 / 概览标尺） ----
    for i, t in enumerate((0.45, 0.35, 0.25, 0.62, 0.45, 0.20, 0.78, 0.32), start=1):
        r[f"grey{i}"] = P.mix(fg, bg, t)
    r["inkDeep"] = P.mix(bg, fg, 0.35)
    r["tabHover"] = P.mix(r["tab"], fg, 0.05)

    # ---- 两个字面色（阴影 / ANSI 白） ----
    r["black"] = "#000000"
    r["white"] = "#FFFFFF"

    # ---- 紫口（pl）的亮/暗两档 ----
    r["plHi"] = P.mix(r["pl"], "#FFFFFF", 0.35)
    r["plDeep"] = P.mix(r["pl"], "#000000", 0.25)

    # ---- 收尾：把半透明压成实色 ----
    # 上游有些主题的正文/底色自带 alpha（清雾的 --color-text 是 95%），
    # 直接带进 VS Code 会变成「标题栏底色半透明」「正文半透明」这类怪东西。
    # 只有设计上就该透的那几个角色（选中、半透明分隔线）保留 alpha。
    for k, v in list(r.items()):
        if k not in TRANSLUCENT and isinstance(v, str):
            r[k] = comp(v, bg)
    return r


if __name__ == "__main__":
    import json
    import os
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    HERE = os.path.dirname(os.path.abspath(__file__))
    import keyexpr as K
    import cherry as Ch

    ke = json.load(open(os.path.join(HERE, "keyexpr.json"), encoding="utf-8"))
    table = {k: tuple(v) for k, v in ke["table"].items()}

    def vector_for(canon, other, mode):
        """一个模式的完整向量：本模式算出来的 31+33 个角色，
        外加三个 Dk 角色 —— 它们的定义就是「另一模式里同名基础角色的取值」
        （青瓷表里那三条字面色 #9CC3D5/#C79A7E/#5F736D 就是这个关系）。"""
        r = roles_for(canon, mode)
        r.pop("_prim_nudged", None)
        r["inkDk"] = other["ink"]
        r["ink2Dk"] = other["ink2"]
        r["nuDk"] = other["nu"]
        r["tyDk"] = other["ty"]
        return r

    # 1) 青瓷：冻结向量必须能复原 567 条
    D, L, _, new = K.build()
    qc_roles = {"dark": K.role_vector(D, L, new, "D"), "light": K.role_vector(D, L, new, "L")}
    bad = []
    for key, (de, le) in table.items():
        for mode, expr in (("dark", de), ("light", le)):
            K.eval_expr(expr, qc_roles[mode])
    print(f"青瓷 567 条 × 2 模式求值：{'全部可求值 ✓' if not bad else '有错'}")

    # 2) 其它主题：算出来，检查键齐、对比度
    themes = json.load(open(os.path.join(HERE, "cherry_palettes.json"), encoding="utf-8"))
    needed = set()
    for de, le in table.values():
        for e in (de, le):
            needed.update(K.role_names(e))
    print(f"表里用到的角色：{len(needed)} 个")
    missing_any = []
    worst = []
    nudged = []
    for t in themes:
        both = {}
        for mode in ("dark", "light"):
            raw = roles_for(t["modes"][mode]["canonical"], mode)
            if "_prim_nudged" in raw:
                nudged.append((t["id"], mode, raw["_prim_nudged"], raw["prim"]))
            both[mode] = raw
        for mode in ("dark", "light"):
            vec = vector_for(t["modes"][mode]["canonical"], both["light" if mode == "dark" else "dark"], mode)
            miss = sorted(r for r in needed if r not in vec)
            if miss:
                missing_any.append((t["id"], mode, miss))
            bg = vec["bg"]
            for r in ("ink", "ink2", "kw", "cm", "st", "nu", "err", "prim", "acc"):
                c = P.contrast(vec[r], bg)
                if c < 3.0:
                    worst.append((t["id"], mode, r, round(c, 2), vec[r], bg))
    print(f"角色齐备：{'✓' if not missing_any else missing_any[:3]}")
    print(f"对比度 < 3.0 的角色：{len(worst)} 处" + (f"  例：{worst[:4]}" if worst else ""))
    print(f"prim 因可读性被提亮的：{len(nudged)} 处")
    for n in nudged:
        print(f"    {n[0]:<18}{n[1]:<6}{n[2]} -> {n[3]}")
    out = {}
    for t in themes:
        both = {m: roles_for(t["modes"][m]["canonical"], m) for m in ("dark", "light")}
        out[t["id"]] = {m: vector_for(t["modes"][m]["canonical"],
                                      both["light" if m == "dark" else "dark"], m)
                        for m in ("dark", "light")}
    json.dump(out,
              open(os.path.join(HERE, "role_vectors.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"→ role_vectors.json（{len(themes)} 主题 × 2 模式）")
