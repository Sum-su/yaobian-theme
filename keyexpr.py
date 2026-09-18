# -*- coding: utf-8 -*-
"""把 build.py 里 567 条手写色值编译成「角色表达式」表。

做法：用哨兵 dict 求值 build.py 的 COLORS，得到每条 key 的 (深, 浅) 是
「某个角色」还是「字面色」。角色直接留名；字面色按下面的规则转成角色表达式：

  · 该字面色的 RGB 与同模式（或另一模式）某角色完全相同 → 用那个角色（+alpha）
  · 对不上任何角色 → 新建一个角色，青瓷的取值就冻结成这个字面色

于是：**青瓷的角色向量一代入，567 条必须逐字节复原**（verify() 会证明这一点），
新角色的取值/公式只影响别的主题。
"""
import ast
import json
import os
import re
import sys

import palette as P

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build.py")

# 对不上任何角色的字面色 → 新角色名（值从青瓷冻结，公式见 roles.py）
LITERAL_ROLE = {
    "#C0796A": "errSoft",   "#A8433A": "errDeep",  "#C0564A": "errHi",
    "#D9A79B": "errPale",   "#B4623F": "errBrown",
    "#A88A2E": "warn",      "#D8CFA9": "warnHi",   "#E0D6B2": "warnPale",
    "#8A6E1F": "warnDeep",
    "#5F9EB5": "info",      "#AECFDD": "infoHi",   "#C3DCE6": "infoPale",
    "#3A7E93": "infoDeep",
    "#4E8F7C": "posMid",    "#2F7F6C": "posLo",    "#6E9C8C": "posHi",
    "#4E9E8C": "posCyan",   "#357F6A": "posDeep",
    "#A6B4B0": "grey1",     "#8FA9A2": "grey2",    "#B9C9C4": "grey3",
    "#5A6B68": "grey4",     "#7E9A93": "grey5",    "#C3D1CD": "grey6",
    "#3F4E4B": "grey7",     "#2C3633": "inkDeep",  "#384443": "tabHover",
    "#CDB3C0": "plHi",      "#A06E86": "plDeep",
    "#C79A7E": "hl",        "#5F736D": "grey8",
    "#3D4A49": "line",      "#D6E1DD": "line",     "#E6EFEC": "ink",
    "#F0F5F3": "bg",        "#2C3635": "bg",
    "#000000": "black",     "#FFFFFF": "white",
}
NONE = "NONE"


class RoleRef(str):
    """角色引用。build.py 里有 `D["prim"] + "66"` 这种写法，
    拼上去的两位十六进制是 alpha —— 用子类把这件事记下来，
    免得回头从字符串上猜（`tab`/`jade`/`acc` 的尾巴本身就长这样）。"""

    def __new__(cls, s, role=None, alpha=None):
        o = super().__new__(cls, s)
        o.role, o.alpha = role, alpha
        return o

    def __add__(self, other):
        if isinstance(other, str) and re.fullmatch(r"[0-9A-Fa-f]{2}", other):
            return RoleRef(str(self) + other, self.role, other)
        return str(self) + str(other)


class Rec(dict):
    def __init__(self, tag):
        self.tag = tag

    def __getitem__(self, k):
        return RoleRef(f"{self.tag}:{k}", k, None)


def load_build(path=BUILD):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)

    def role_dict(name):
        node = next(n for n in tree.body
                    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == name)
        v = node.value
        if isinstance(v, ast.Call):
            return {kw.arg: kw.value.value for kw in v.keywords}
        return {k.value: val.value for k, val in zip(v.keys, v.values)}

    D, L = role_dict("D"), role_dict("L")
    node = next(n for n in tree.body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "COLORS")
    colors = eval(compile(ast.Expression(node.value), "<colors>", "eval"),
                  {"D": Rec("D"), "L": Rec("L"), "NONE": NONE})
    return D, L, colors


def rgb_of(spec):
    base = spec.split("@")[0] if "@" in spec else spec
    if base.startswith("#"):
        r, g, b, _ = P.parse(base)
        return f"#{r:02X}{g:02X}{b:02X}"
    return base


def spec_rgb(spec, role_rgb):
    """一个 spec 实际代表的不透明色（角色引用要按它自己那个模式的取值算）。"""
    if spec == NONE or isinstance(spec, RoleRef) and not ref_mode(spec):
        return None
    if isinstance(spec, RoleRef):
        return role_rgb[ref_mode(spec)][spec.role]
    s = spec.upper()
    return s[:7] if s.startswith("#") else None


def ref_mode(spec):
    """RoleRef 的字符串是 "D:ink"（带 alpha 是 "D:ink66"），取出它来自哪个模式。"""
    return spec.split(":", 1)[0] if ":" in spec else None


def to_expr(spec, mode, role_rgb):
    """spec: 角色引用 D:x / L:x，或字面色 #RRGGBB[AA]，或 NONE"""
    if spec == NONE:
        return "NONE"
    if isinstance(spec, RoleRef):           # 角色，可能带 alpha 后缀（如 D["prim"] + "66"）
        role = spec.role
        if ref_mode(spec) and ref_mode(spec) != mode:
            # build.py 里 `(D["ink"], D["ink"])` 这种写法：浅色槽里引的是**深色**的 ink。
            # 那不是「本模式的 ink」，得记成 inkDk —— 否则别的主题会拿浅色的深色墨
            # 去当浅色模式的字色（禅棕就是深棕压深棕，看不见）。
            role = f"{role}Dk"
        return f"A({role},0x{spec.alpha})" if spec.alpha else role
    spec = spec.upper()
    rgb, a = spec[:7], spec[7:]
    suffix = f",0x{a}" if a else ""
    for role, val in role_rgb[mode].items():   # 只认同模式：跨模式的同名值要登记成新角色
        if val == rgb:
            return f"A({role}{suffix})" if a else role
    other = "L" if mode == "D" else "D"
    for role, val in role_rgb[other].items():  # 只有另一模式有 → 建 <role>Dk（公式见 roles.py）
        if val == rgb:
            return f"A({role}Dk{suffix})" if a else f"{role}Dk"
    role = LITERAL_ROLE.get(rgb)
    if not role:
        raise KeyError(f"未登记的字面色 {rgb}")
    return f"A({role}{suffix})" if a else role


def build():
    D, L, colors = load_build()
    role_rgb = {"D": {r: v.upper()[:7] for r, v in D.items()},
                "L": {r: v.upper()[:7] for r, v in L.items()}}
    # 角色表达式表（按组合去重）
    combos = {}
    for key, (d, l) in colors.items():
        combos.setdefault((d, l), []).append(key)
    table, new_roles = {}, {}
    for (d, l), keys in combos.items():
        de = to_expr(d, "D", role_rgb)
        le = to_expr(l, "L", role_rgb)
        for k in keys:
            table[k] = (de, le)
        for spec, expr in ((d, de), (l, le)):
            rgb = spec_rgb(spec, role_rgb) or ""
            if rgb.startswith("#") and len(rgb) == 7:
                for r in role_names(expr):
                    if r in role_rgb["D"] or r in role_rgb["L"]:
                        continue          # 已有角色（bg/ink/line 这些），别用冻结值盖掉
                    if r in LITERAL_ROLE.values() or r.endswith("Dk"):
                        new_roles.setdefault(r, {})["D" if spec is d else "L"] = rgb
    return D, L, table, new_roles


EXPR_ROLE = re.compile(r"A\(([a-zA-Z_][a-zA-Z0-9_]*)(?:,0x[0-9a-fA-F]+)?\)")


def role_names(expr):
    """表达式里真正引用到的角色名（A(prim,0x66) -> prim；裸名字 -> 名字）。"""
    expr = expr.strip()
    if expr == "NONE":
        return []
    if expr.startswith("A("):
        return [EXPR_ROLE.fullmatch(expr).group(1)] if EXPR_ROLE.fullmatch(expr) else []
    return [expr]


def eval_expr(expr, roles):
    """表达式求值：角色名 / A(角色,alpha) / NONE。"""
    expr = expr.strip()
    if expr == "NONE":
        return None
    m = re.fullmatch(r"A\((\w+)(?:,(0x[0-9a-fA-F]+))?\)", expr)
    if m:
        return P.alpha(roles[m.group(1)], int(m.group(2), 16) if m.group(2) else None)
    return roles[expr]


def role_vector(D, L, new_roles, mode):
    """青瓷在某个模式下的角色向量：31 个手调角色 + 冻结的新角色。"""
    roles = dict(D if mode == "D" else L)
    for r, val in new_roles.items():
        roles[r] = val.get(mode) or list(val.values())[0]
    return roles


def resolve_spec(spec, roles, mode=None):
    """把 build.py 里的原始 spec 解析成它代表的色值（用于对照）。"""
    if spec == NONE:
        return None
    if isinstance(spec, RoleRef):
        role = spec.role
        if mode and ref_mode(spec) and ref_mode(spec) != mode:
            role = f"{role}Dk"
        return P.alpha(roles[role], int(spec.alpha, 16)) if spec.alpha else roles[role]
    return spec.upper()


def verify(D, L, table):
    """一代入青瓷的角色向量，必须逐字节复原 567 条。"""
    _, _, colors = load_build()
    _, _, _, new_roles = build()
    bad = []
    for key, (d, l) in colors.items():
        for mode, spec in (("D", d), ("L", l)):
            roles = role_vector(D, L, new_roles, mode)
            want = resolve_spec(spec, roles, mode)
            got = eval_expr(table[key][0 if mode == "D" else 1], roles)
            if got != want:
                bad.append((key, mode, want, got))
    return bad


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    D, L, table, new_roles = build()
    print(f"键 {len(table)}  组合 {len(set(table.values()))}  新角色 {len(new_roles)}")
    bad = verify(D, L, table)
    print(f"青瓷复原校验：{'全部逐字节一致 ✓' if not bad else f'不一致 {len(bad)} 条'}")
    for row in bad[:25]:
        print("   ", row)
    json.dump(
        {"table": {k: list(v) for k, v in table.items()},
         "new_roles": new_roles,
         "qingci": {"D": D, "L": L}},
        open(os.path.join(HERE, "keyexpr.json"), "w", encoding="utf-8"),
        ensure_ascii=False, indent=1)
    print("→ keyexpr.json")
