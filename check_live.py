#!/usr/bin/env python3
"""查商城上的实际状态。

为什么需要它：刚发布时前端会滞后——`items?itemName=...` 网页 404、`code --install-extension`
报 `not found`，但后台其实已经是 public 了。拿那些当失败会白折腾。权威判据是 gallery 查询
接口（`vsce publish` 打的就是它），这个脚本打的就是它。

用法：
    python check_live.py                    # 查本仓库的扩展
    python check_live.py ms-python.python    # 查别的（用来做对照）
"""
import json
import sys
import urllib.error
import urllib.request

PUBLISHER = "tombliboo0226"
NAME = "yaobian-theme"
API = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"


def query(full_name):
    req = urllib.request.Request(
        API,
        data=json.dumps({
            "filters": [{"criteria": [{"filterType": 7, "value": full_name}]}],
            "flags": 914,
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json;api-version=7.2-preview.1",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    full = sys.argv[1] if len(sys.argv) > 1 else f"{PUBLISHER}.{NAME}"

    try:
        data = query(full)
    except urllib.error.URLError as e:
        print(f"连不上商城：{e}")
        return 1

    exts = data["results"][0]["extensions"]
    if not exts:
        print(f"商城上查不到 {full}")
        print("（刚发布的话过几分钟再试；一直查不到才是真没发上去）")
        return 1

    e = exts[0]
    v = e["versions"][0]
    flags = e.get("flags") or ""
    got = {p.strip() for p in flags.split(",") if p.strip()}

    print(f"完整名   = {e['publisher']['publisherName']}.{e['extensionName']}")
    print(f"显示名   = {e.get('displayName')}")
    print(f"版本     = {v['version']}")
    print(f"flags    = {flags}")
    print(f"最后更新 = {v.get('lastUpdated')}")

    # 两个标志各管一件事，缺哪个就说明卡在哪一步
    print()
    # 记号一律用 ASCII：Windows 控制台默认 GBK，'✓' 会让 print 抛 UnicodeEncodeError
    if "public" in got:
        print("  [OK] public    -- 已公开发布")
    else:
        print("  [  ] public    -- 还没公开")
    if "validated" in got:
        print("  [OK] validated -- 校验流水线已跑完，可以安装了")
    else:
        print("  [  ] validated -- 校验还没跑完：此时 items 页会 404、")
        print("                    `code --install-extension` 报 not found，都是正常现象。")
        print("                    等它变成 validated 再试（通常几分钟到十几分钟）。")

    stats = {s.get("statisticName"): s.get("value") for s in e.get("statistics", [])}
    if stats:
        print("统计     =", ", ".join(f"{k}={n}" for k, n in stats.items() if n))

    print("Assets   =")
    for f in v.get("files", []):
        kind = (f.get("assetType") or "").rsplit(".", 1)[-1]
        print(f"  {kind}")

    for p in v.get("properties", []):
        if p.get("key") == "Microsoft.VisualStudio.Code.Engine":
            print(f"引擎要求 = {p.get('value')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
