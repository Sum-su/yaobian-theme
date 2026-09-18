# -*- coding: utf-8 -*-
"""窑变 · 深浅模式切换器 —— 「跟随系统」与「手动」两条路，随时换，且继承当前深浅。

只管 VS Code 的四个设置键：

    workbench.colorTheme                 手动模式用哪套（值是主题标签，如「湖光（深）」）
    window.autoDetectColorScheme         开着 = 跟随系统
    workbench.preferredDarkColorTheme    跟随系统时，系统深色用哪套
    workbench.preferredLightColorTheme   跟随系统时，系统浅色用哪套

VS Code 自己的规则：`autoDetectColorScheme` 开着时 `workbench.colorTheme` 被忽略，
按系统亮暗在 preferredDark/Light 里选；关掉时又回到 `workbench.colorTheme`。
所以「手动时选的那套」天然被记住——本脚本的活儿是把 **36 个家族 × 深浅** 都成对
喂进那两个槽位，并且在切换时以**此刻正在显示的那套**为起点。

    python mode.py status            现在什么模式、哪一家、系统是深是浅
    python mode.py list              列出 36 个家族（id ↔ 标签）
    python mode.py auto [家族]       跟随系统；家族缺省 = 当前这套的家族
    python mode.py manual [家族]     切回手动，钉住**此刻显示的那套**（继承切换前的深浅）
    python mode.py dark|light [家族] 手动钉死深浅
    python mode.py tasks [--force]   把入口写进 VS Code 用户级 tasks.json（命令面板里用）

家族参数 id 和标签都认：`hu-guang` / `湖光` 等价。

**安全**：只改上面那四个键，settings.json 其余部分逐字节不动——不做「反序列化再写回」，
免得把注释、缩进、键序（以及别的扩展那串带密钥的配置）重排或丢掉。脚本从不打印
settings.json 的内容，只打印这四个键；改动前留一份 settings.json.yaobian-bak 备份。
"""
import argparse
import io
import json
import os
import shutil
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "package.json")
SETTINGS = os.path.join(os.environ["APPDATA"], "Code", "User", "settings.json")
STATE_DB = os.path.join(os.environ["APPDATA"], "Code", "User", "globalStorage", "state.vscdb")
TASKS = os.path.join(os.environ["APPDATA"], "Code", "User", "tasks.json")

SUFFIX = {"（深）": "dark", "（浅）": "light"}
KEYS = {
    "theme": "workbench.colorTheme",
    "auto": "window.autoDetectColorScheme",
    "dark": "workbench.preferredDarkColorTheme",
    "light": "workbench.preferredLightColorTheme",
}


# ---------------------------------------------------------------- JSON 文本手术
def _skip_string(t, i):
    """t[i] 是引号，返回字符串结束后的下标。"""
    i += 1
    while i < len(t):
        if t[i] == "\\":
            i += 2
            continue
        if t[i] == '"':
            return i + 1
        i += 1
    raise ValueError("字符串没有闭合（settings.json 被改坏了？）")


def scan_top(text):
    """配深扫描，只收**顶层**（深度 1）的键。

    不用正则：同一个键可能出现在 `"[python]"` 这类语言作用域块里，正则分不清层级，
    会改错那一个——而 VS Code 对改错的键是静默忽略，看起来就是「没反应」。
    返回 {key: (key_start, val_start, val_end, val_text)}。
    """
    out = {}
    i, depth, n = 0, 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = _skip_string(text, i)
            k = j
            while k < n and text[k] in " \t\r\n":
                k += 1
            if depth == 1 and k < n and text[k] == ":":
                v = k + 1
                while v < n and text[v] in " \t\r\n":
                    v += 1
                if v < n and text[v] == '"':
                    ve = _skip_string(text, v)
                else:
                    d, ve = 0, v
                    while ve < n:
                        ch = text[ve]
                        if ch in "{[":
                            d += 1
                        elif ch in "}]":
                            if d == 0:
                                break
                            d -= 1
                        elif ch == "," and d == 0:
                            break
                        elif ch == '"':
                            ve = _skip_string(text, ve) - 1
                        ve += 1
                out[text[i + 1:j - 1]] = (i, v, ve, text[v:ve])
                i = ve
                continue
            i = j
            continue
        if c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
        i += 1
    return out


def _indent_of(text):
    """照抄文件里顶层键的缩进——取**最常见**的那个，不是第一个。

    这份 settings.json 的第一个顶层键恰好缩进 8 格（其余都是 4 格），只看第一个的话，
    插进去的新键就跟满文件对不齐（2026-09-18 真机上就是这么歪了一次）。
    """
    sc = scan_top(text)
    counts = {}
    for k in sc:
        line = text.rfind("\n", 0, sc[k][0]) + 1
        seg = text[line:line + 40]
        ind = seg[:len(seg) - len(seg.lstrip())]
        if ind:
            counts[ind] = counts.get(ind, 0) + 1
    if not counts:
        return "    "
    return max(counts.items(), key=lambda kv: (kv[1], len(kv[0])))[0]


def set_key(text, key, value_text):
    """把顶层 key 的值换成 value_text；没有这个键就插在根对象末尾。"""
    hit = scan_top(text).get(key)
    if hit:
        _, vs, ve, old = hit
        return text[:vs] + value_text + text[ve:], old
    nl = "\r\n" if "\r\n" in text else "\n"
    end = len(text.rstrip())
    assert text[:end].endswith("}"), "settings.json 的根对象没有正常结束"
    close = end - 1
    before = text[:close].rstrip()
    comma = "" if before.endswith("{") or before.endswith(",") else ","
    ind = _indent_of(text)
    ins = f'{comma}{nl}{ind}"{key}": {value_text}{nl}'
    return text[:close] + ins + text[close:], None


def read_text(path):
    raw = open(path, "rb").read()
    bom = raw[:3] == b"\xef\xbb\xbf"
    return raw.decode("utf-8-sig"), bom


def write_text(path, text, bom):
    if os.path.exists(path):
        shutil.copy2(path, path + ".yaobian-bak")
    data = text.encode("utf-8")
    open(path, "wb").write((b"\xef\xbb\xbf" if bom else b"") + data)


# ---------------------------------------------------------------- 主题家族
def families():
    pkg = json.load(io.open(PKG, encoding="utf-8"))
    fams = {}
    for t in pkg["contributes"]["themes"]:
        for suf, mode in SUFFIX.items():
            if t["label"].endswith(suf):
                fams.setdefault(t["label"][:-len(suf)], {})[mode] = t["label"]
                break
    return fams


def resolve_family(arg, fams):
    if arg is None:
        return None
    if arg in fams:
        return arg
    for fam, pair in fams.items():
        if arg in pair.values() or arg in (pair.get("dark", ""), pair.get("light", "")):
            return fam
    for fam in fams:
        if fam.lower() == arg.lower():
            return fam
    raise SystemExit("没有这个家族：%s（用 `python mode.py list` 看有哪些）" % arg)


# ---------------------------------------------------------------- 现状
def live_label():
    """当前**真正渲染**的那套主题的标签：读 state.vscdb 的 colorThemeData。

    活库有锁，连 -wal/-shm 一起拷到 temp 再读；VS Code 没开时主库也是最新的。
    读不到就返回 None（脚本会退回「设置里的值 + 系统深浅」去推断）。
    """
    tmp = os.path.join(tempfile.gettempdir(), "yaobian-state-copy")
    os.makedirs(tmp, exist_ok=True)
    dst = os.path.join(tmp, "state.vscdb")
    try:
        for suf in ("", "-wal", "-shm"):
            if os.path.exists(dst + suf):
                os.remove(dst + suf)
            if os.path.exists(STATE_DB + suf):
                shutil.copy2(STATE_DB + suf, dst + suf)
        con = sqlite3.connect(dst)
        row = con.execute("select value from ItemTable where key='colorThemeData'").fetchone()
        con.close()
        if not row:
            return None
        v = row[0].decode("utf-8", "replace") if isinstance(row[0], bytes) else row[0]
        return json.loads(v).get("label")
    except Exception:
        return None


def os_is_dark():
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        v, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
        return not bool(v)
    except Exception:
        return None


def current(fams, st):
    """此刻在显示的是哪家的哪一套。返回 (family, mode, 来源说明)。"""
    lab = live_label()
    note = ""
    if lab:
        for fam, pair in fams.items():
            for mode, l in pair.items():
                if l == lab:
                    return fam, mode, "正在渲染"
        # 活库读到了主题、但不是窑变的：此刻屏幕上根本不是窑变（多半是 `workbench.colorTheme`
        # 被删了、回落到内置主题——卸载提供该主题的扩展就会触发，见 README）。下面的答案都是
        # 按设置推断的，别让它冒充「此刻显示」。
        note = "；注意：此刻真正渲染的是「%s」" % lab
    theme = st.get(KEYS["theme"])
    for fam, pair in fams.items():
        for mode, l in pair.items():
            if l == theme:
                return fam, mode, "设置里的手动值" + note
    d = os_is_dark()
    slot = KEYS["light"] if d is False else KEYS["dark"]
    for fam, pair in fams.items():
        for mode, l in pair.items():
            if l == st.get(slot):
                return fam, mode, "系统深浅 + preferred 槽位" + note
    fam = next(iter(fams))
    return fam, "dark", "没找到窑变的设置，按第一个家族兜底" + note


# ---------------------------------------------------------------- 命令
def slot(tag, st, fams):
    """preferred 槽位指的是哪一家的哪一套。返回 (模式, 标签, (家族, 模式) 或 None)。"""
    mode = "dark" if tag == "dark" else "light"
    lab = st.get(KEYS[tag])
    for fam, pair in fams.items():
        if pair[mode] == lab:
            return lab, (fam, mode)
    return lab, None


def cmd_status(fams, st, path):
    fam, mode, src = current(fams, st)
    auto = st.get(KEYS["auto"])
    d = os_is_dark()
    print("模式      ：" + ("跟随系统" if auto else "手动"))
    print("此刻显示  ：%s（%s；依据：%s）" % (fams[fam][mode], fam, src))
    print("系统深浅  ：" + ("深色" if d else "浅色" if d is False else "读不到"))
    print("四个键    ：")
    for k in (KEYS["theme"], KEYS["auto"], KEYS["dark"], KEYS["light"]):
        print("    %-38s %s" % (k, st.get(k, "(未设置)")))
    dl, df = slot("dark", st, fams)
    ll, lf = slot("light", st, fams)
    if auto:
        # 跟随系统时说了算的是两个 preferred 槽位，**不是**此刻显示的那一套：
        # 系统一切换就会去读槽位，所以这里必须报槽位，否则用户会以为自己在跟湖光，
        # 实际系统一翻就跳回青瓷。
        print("⇒ 系统深色 → %s%s" % (dl or "(指向的不是窑变的主题)", "  ← 现在用这个" if d else ""))
        print("   系统浅色 → %s%s" % (ll or "(指向的不是窑变的主题)", "  ← 现在用这个" if d is False else ""))
        if df and lf and df[0] != lf[0]:
            print("   ⚠ 两个槽位不是同一家（%s / %s）——多半是在主题选择器里手点过。"
                  % (df[0], lf[0]))
            print("     想配对：python mode.py auto <家族>")
    elif df and lf and df[0] == lf[0]:
        print("⇒ 两个 preferred 槽位配的是同一家：%s / %s" % (dl, ll))
    else:
        print("⇒ 想跟随系统：python mode.py auto %s（会把槽位配成 %s / %s）"
              % (fam, fams[fam]["dark"], fams[fam]["light"]))
    return 0


def apply(path, changes, dry):
    """changes: {键: 值文本}。返回实际改动的键。"""
    text, bom = read_text(path)
    before = text
    changed = []
    for k, v in changes.items():
        text, old = set_key(text, k, v)
        if old != v:
            changed.append((k, old, v))
    if not changed:
        print("四个键已经就是这个值，没动文件。")
        return []
    if dry:
        print("（--dry-run，不落盘）将要改：")
        for k, old, v in changed:
            print("    %-38s %s → %s" % (k, old, v))
        return changed
    write_text(path, text, bom)
    for k, old, v in changed:
        print("    %-38s %s → %s" % (k, old, v))
    return changed


def cmd_auto(fams, st, path, arg, dry):
    fam = resolve_family(arg, fams) or current(fams, st)[0]
    print("跟随系统（家族 %s）：" % fam)
    apply(path, {KEYS["dark"]: '"%s"' % fams[fam]["dark"],
                 KEYS["light"]: '"%s"' % fams[fam]["light"],
                 KEYS["auto"]: "true"}, dry)
    d = os_is_dark()
    print("⇒ 系统现在是%s色，会显示 %s" % ("深" if d else "浅" if d is False else "？（读不到）",
                                            fams[fam]["light" if d is False else "dark"]))
    return 0


def cmd_manual(fams, st, path, arg, want, dry):
    fam, mode, src = current(fams, st)
    fam = resolve_family(arg, fams) or fam
    mode = want or mode                       # 不给 dark/light 就继承此刻显示的深浅
    print("切回手动（继承 %s 的 %s）：" % (src, "深色" if mode == "dark" else "浅色"))
    apply(path, {KEYS["theme"]: '"%s"' % fams[fam][mode], KEYS["auto"]: "false"}, dry)
    print("⇒ 现在是 %s，不再跟系统走" % fams[fam][mode])
    return 0


def cmd_list(fams, st, path):
    for i, (fam, pair) in enumerate(fams.items(), 1):
        print("%2d  %-8s %s / %s" % (i, fam, pair["dark"], pair["light"]))
    print("共 %d 个家族（%d 套主题）" % (len(fams), len(fams) * 2))
    return 0


def cmd_tasks(fams, st, path, force):
    """把入口写进**用户级** tasks.json：命令面板 → Tasks: Run Task → 窑变：…

    纯声明式，不需要扩展带代码；家族清单直接从 package.json 现拉，不会过期。
    已有的 tasks.json 里若有**不是**本工具的条目，默认拒绝覆盖（那可能是你自己写的任务）。
    """
    prog = os.path.join(HERE, "mode.py")
    def task(label, argv, quiet=True):
        return {
            "label": label, "type": "shell", "command": "python",
            "args": [prog] + argv, "problemMatcher": [],
            "presentation": {"reveal": "silent" if quiet else "always",
                             "panel": "shared", "close": quiet, "echo": False, "focus": False},
        }
    fams_sorted = list(fams)
    tasks = {
        "version": "2.0.0",
        "tasks": [
            task("窑变：跟随系统（当前家族）", ["auto"]),
            task("窑变：跟随系统（选家族）", ["auto", "${input:family}"]),
            task("窑变：切回手动（继承此刻显示的深浅）", ["manual"]),
            task("窑变：手动 · 深", ["dark"]),
            task("窑变：手动 · 浅", ["light"]),
            task("窑变：状态", ["status"], quiet=False),
            task("窑变：列出家族", ["list"], quiet=False),
        ],
        # pickString 传出来的就是选项字符串本身，所以这里直接放**家族名**——
        # 它既是给 mode.py 的参数（resolve_family 认家族名），也是人能读的（「湖光」）。
        "inputs": [{
            "id": "family", "type": "pickString", "description": "选一个家族",
            "options": list(fams_sorted),
        }],
    }
    if os.path.exists(TASKS):
        old = io.open(TASKS, encoding="utf-8-sig").read()
        try:
            ot = json.loads(old)
        except ValueError:
            ot = None
        if ot is None:
            raise SystemExit("已有的 tasks.json 不是纯 JSON（带注释？），怕覆盖掉你的任务，"
                             "这里不写了。要写就先自己备份/清理：%s" % TASKS)
        foreign = [t.get("label") for t in ot.get("tasks", [])
                   if not str(t.get("label", "")).startswith("窑变：")]
        if foreign and not force:
            raise SystemExit("你的 tasks.json 里还有别的任务 %s ——不覆盖。"
                             "确认要合并（会先备份）就加 --force。" % foreign)
        shutil.copy2(TASKS, TASKS + ".yaobian-bak")
    os.makedirs(os.path.dirname(TASKS), exist_ok=True)
    io.open(TASKS, "w", encoding="utf-8", newline="\n").write(
        json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
    print("→ %s（%d 个任务，家族清单 %d 项）" % (TASKS, len(tasks["tasks"]), len(fams_sorted)))
    print("  用：Ctrl+Shift+P → `Tasks: Run Task` → 选「窑变：…」")
    return 0


def main():
    # 两个流都要设：报错走 stderr，只设 stdout 的话错误信息在 GBK 控制台里会变乱码
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="窑变 · 深浅模式切换器",
                                 epilog="家族参数 id 和标签都认：hu-guang / 湖光 等价")
    ap.add_argument("cmd", choices=["status", "list", "auto", "manual", "dark", "light",
                                     "tasks"])
    ap.add_argument("family", nargs="?")
    ap.add_argument("--settings", default=SETTINGS, help="settings.json 路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印要改什么，不落盘")
    ap.add_argument("--force", action="store_true", help="tasks：覆盖/合并已有的 tasks.json")
    a = ap.parse_args()

    if not os.path.exists(a.settings):
        raise SystemExit("找不到 settings.json：%s" % a.settings)
    fams = families()
    text, _ = read_text(a.settings)
    st = {k: v[3] for k, v in scan_top(text).items()}
    st = {k: (json.loads(v) if v in ("true", "false") else v.strip('"'))
          for k, v in st.items() if k in KEYS.values()}

    if a.cmd == "status":
        return cmd_status(fams, st, a.settings)
    if a.cmd == "list":
        return cmd_list(fams, st, a.settings)
    if a.cmd == "tasks":
        return cmd_tasks(fams, st, a.settings, a.force)
    if a.cmd == "auto":
        return cmd_auto(fams, st, a.settings, a.family, a.dry_run)
    if a.cmd == "manual":
        return cmd_manual(fams, st, a.settings, a.family, None, a.dry_run)
    return cmd_manual(fams, st, a.settings, a.family,
                      "dark" if a.cmd == "dark" else "light", a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
