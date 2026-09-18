# -*- coding: utf-8 -*-
"""色彩数学：sRGB <-> OKLab/OKLCH、混合、明度调整、对比度修正。

手调色值的习惯是「在 sRGB 里混色、在感知空间里调明度」，所以：
  - mix()/alpha()  在 sRGB 空间做（和设计稿一致）
  - lighten/darken/desat 在 OKLCH 空间做（感知均匀）
  - fix_contrast() 只推 L、保留 H/C，直到满足 WCAG 对比度
"""
import math

# ---------- 基础 ----------

NAMED = {
    "transparent": (0, 0, 0, 0.0), "black": (0, 0, 0, 1.0), "white": (255, 255, 255, 1.0),
    "red": (255, 0, 0, 1.0), "green": (0, 128, 0, 1.0), "blue": (0, 0, 255, 1.0),
    "yellow": (255, 255, 0, 1.0), "orange": (255, 165, 0, 1.0), "gray": (128, 128, 128, 1.0),
    "grey": (128, 128, 128, 1.0), "silver": (192, 192, 192, 1.0), "purple": (128, 0, 128, 1.0),
    "pink": (255, 192, 203, 1.0), "brown": (165, 42, 42, 1.0), "cyan": (0, 255, 255, 1.0),
    "magenta": (255, 0, 255, 1.0), "navy": (0, 0, 128, 1.0), "teal": (0, 128, 128, 1.0),
    "currentcolor": None,
}


def parse(c):
    """'#RGB' / '#RRGGBB' / '#RRGGBBAA' / 'rgb()' / 'rgba()' / 'hsl()' / 'oklch()' / 关键字"""
    c = c.strip()
    if c.lower() in NAMED:
        v = NAMED[c.lower()]
        if v is None:
            raise ValueError(f"不是具体色值 {c!r}")
        return v
    if c.startswith(("rgb", "hsl", "hw")):
        return _parse_func(c)
    if c.startswith(("oklch", "oklab")):
        return _parse_ok(c)
    c = c.lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    if len(c) == 4:
        c = ''.join(ch * 2 for ch in c)
    if len(c) == 6:
        c += 'ff'
    if len(c) != 8:
        raise ValueError(f"bad color {c!r}")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16) / 255)


def _parse_ok(c):
    import re
    m = re.fullmatch(r"(oklch|oklab)\(([^)]*)\)", c, re.I)
    if not m:
        raise ValueError(f"bad color {c!r}")
    kind, body = m.group(1).lower(), m.group(2)
    head, _, tail = body.partition("/")
    parts = [x for x in re.split(r"[,\s]+", head.strip()) if x]
    if len(parts) < 3:
        raise ValueError(f"bad color {c!r}")
    if len(parts) == 3:
        Lraw = parts[0]
        L = float(Lraw.rstrip("%")) / (100 if Lraw.endswith("%") else 1)
        nums = (L, float(parts[1]), float(parts[2])) if kind == "oklch" else (L, float(parts[1]), float(parts[2]))
    else:                                   # oklch(L C H) 已在上支；这里兜底
        nums = tuple(float(x.rstrip("%")) for x in parts[:3])
    a = 1.0
    if tail.strip():
        t = tail.strip()
        a = float(t.rstrip("%")) / (100 if t.endswith("%") else 1)
    if kind == "oklch":
        rgb = from_oklch(nums)
    else:
        rgb = from_oklab(nums)
    return (round(rgb[0]), round(rgb[1]), round(rgb[2]), a)


def _parse_func(c):
    import re
    m = re.fullmatch(r"(rgba?|hsla?)\(([^)]*)\)", c, re.I)
    if not m:
        raise ValueError(f"bad color {c!r}")
    kind, body = m.group(1).lower(), m.group(2)
    parts = [x for x in re.split(r"[,\s/]+", body.strip()) if x]
    if len(parts) < 3:
        raise ValueError(f"bad color {c!r}")
    nums = [float(x.rstrip('%')) for x in parts[:3]]
    a = 1.0
    if len(parts) > 3:
        a = float(parts[3].rstrip('%'))
        if len(parts[3]) and parts[3].endswith('%'):
            a /= 100
    if kind.startswith("rgb"):
        r, g, b = nums
    else:
        h, s, l = nums[0] % 360 / 360, nums[1] / 100, nums[2] / 100
        if s == 0:
            r = g = b = l * 255
        else:
            def hue(p, q, t):
                t = t % 1
                if t < 1 / 6: return p + (q - p) * 6 * t
                if t < 1 / 2: return q
                if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
                return p
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r, g, b = hue(p, q, h + 1 / 3) * 255, hue(p, q, h) * 255, hue(p, q, h - 1 / 3) * 255
    return (round(r), round(g), round(b), a)


def is_color(c):
    """能不能当成一个色值用（梯度/图片/关键字不算）。"""
    if not isinstance(c, str):
        return False
    t = c.strip().lower()
    if not t or t in ("none", "transparent", "currentcolor", "inherit", "initial"):
        return False
    if "gradient(" in t or t.startswith("url(") or t.startswith("var("):
        return False
    try:
        parse(t)
        return True
    except Exception:
        return False


def norm(c):
    """任意 CSS 色值 -> '#RRGGBB[AA]'；不是颜色就返回 None。"""
    if not is_color(c):
        return None
    r, g, b, a = parse(c)
    return hexs((r, g, b), a)


def hexs(rgb, a=None):
    r, g, b = (max(0, min(255, round(v))) for v in rgb[:3])
    out = f"#{r:02X}{g:02X}{b:02X}"
    if a is not None and a < 0.999:
        out += f"{max(0, min(255, round(a * 255))):02X}"
    return out


def is_hex(c):
    try:
        parse(c)
        return True
    except Exception:
        return False


def alpha(c, a):
    """给颜色套 alpha（保留原色）。a 可以是 0-255 的整数或 0-1 的浮点。"""
    r, g, b, _ = parse(c)
    if isinstance(a, int) and a > 1:
        a = a / 255
    return hexs((r, g, b), a)


def opaque(c):
    r, g, b, a = parse(c)
    return hexs((r, g, b), a)


# ---------- sRGB <-> OKLab ----------

def _lin(v):
    v = v / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _srgb(v):
    v = 0.0 if v < 0 else (1.0 if v > 1 else v)
    v = v * 12.92 if v <= 0.0031308 else 1.055 * (v ** (1 / 2.4)) - 0.055
    return v * 255


def to_oklab(c):
    r, g, b, _ = parse(c)
    r, g, b = _lin(r), _lin(g), _lin(b)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def from_oklab(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return (_srgb(r), _srgb(g), _srgb(bb))


def to_oklch(c):
    L, a, b = to_oklab(c)
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360)


def from_oklch(lch):
    L, C, H = lch
    return from_oklab((L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H))))


def oklch_hex(lch, a=None):
    return hexs(from_oklch(lch), a)


# ---------- 变换 ----------

def mix(c1, c2, t):
    """sRGB 空间线性插值：t=0 得 c1，t=1 得 c2。"""
    r1, g1, b1, _ = parse(c1)
    r2, g2, b2, _ = parse(c2)
    return hexs((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


def dL(c, delta):
    """明度平移（OKLCH L 加 delta，clamp 0-1）。"""
    L, C, H = to_oklch(c)
    return oklch_hex((max(0.0, min(1.0, L + delta)), C, H))


def scaleL(c, k):
    """明度缩放（相对 L）。"""
    L, C, H = to_oklch(c)
    return oklch_hex((max(0.0, min(1.0, L * k)), C, H))


def setL(c, L):
    _, C, H = to_oklch(c)
    return oklch_hex((L, C, H))


def desat(c, k):
    """彩度缩放：k=0 变灰，1 不变。"""
    L, C, H = to_oklch(c)
    return oklch_hex((L, C * k, H))


def soft(c, spread=0.13, ck=0.9):
    """「柔化」：把明度往中灰（0.62）拉，彩度略降 —— 用于 soft 错误/警告色。"""
    L, C, H = to_oklch(c)
    L2 = L + (0.62 - L) * spread * 3
    return oklch_hex((max(0.0, min(1.0, L2)), C * ck, H))


def lum(c):
    r, g, b, _ = parse(c)
    f = lambda v: (v / 255) / 12.92 if (v / 255) <= 0.04045 else (((v / 255) + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(c1, c2):
    l1, l2 = lum(c1), lum(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def fix_contrast(fg, bg, target=4.5, max_steps=64):
    """推 fg 的明度直到对 bg 的对比度 >= target；保留色相/彩度。"""
    if contrast(fg, bg) >= target:
        return opaque(fg)
    L, C, H = to_oklch(fg)
    bgL, _, _ = to_oklch(bg)
    # 朝「fg 已经偏的那一侧」继续推 —— 这样一定是在拉开对比度，而且还保得住色相。
    # （早先是按 bg 明度盲选方向：底色偏亮就往下推。碰上「深底 + 更深的字」
    #   这种少见组合会越推越糊，最后只能退到纯黑/纯白。）
    sign = 1 if L >= bgL else -1
    lo, hi = 0.0, 1.0
    best = fg
    for _ in range(max_steps):
        mid = (lo + hi) / 2
        cand = oklch_hex((max(0.0, min(1.0, L + sign * mid)), C, H))
        if contrast(cand, bg) >= target:
            best = cand
            hi = mid
        else:
            lo = mid
    if contrast(best, bg) < target:      # 推不动就退到黑白极端
        best = "#FFFFFF" if bgL < 0.5 else "#000000"
        if contrast(best, bg) < target:
            best = "#000000" if bgL < 0.5 else "#FFFFFF"
    return hexs(parse(best))
