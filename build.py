# -*- coding: utf-8 -*-
"""
青瓷 (Qing-ci) VS Code 主题生成器 / 校验器
==========================================
一份映射表 -> 深浅两套 themes/qingci-*.json

改色流程：
  1. 改下面的调色板 D（深）/ L（浅），或改 COLORS 里某一行的值
  2. python build.py          # 生成 + 自检
  3. python pack.py           # 打包成 .vsix
  4. code --install-extension dist/qingci-theme-0.1.0.vsix --force，然后重载窗口

自检内容（全部通过才写文件）：
  · 每个键在【本机这个 VS Code 版本】里确实存在
      - 来源 A：安装目录自带主题（theme-defaults）用到的颜色键
      - 来源 B：内置扩展 package.json 的 contributes.colors
      - 来源 C：workbench 等大 bundle 里的 "键名" 字面量
  · 色值形如 #RGB / #RRGGBB / #RRGGBBAA
  · 深浅两套的键集合完全一致
"""
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VSCODE = r"C:\Users\Administrator\AppData\Local\Programs\Microsoft VS Code"
OUT = os.path.join(HERE, "themes")

# ============================================================
# 调色板
#   锚点只有两个：釉色 #7BA898（强调）与墨色 #2C3635（深色模式的底）
#   其余全是它们的混色档，深浅共用同一套语义
# ============================================================
D = dict(
    bg="#2C3635",      # 内容底色
    pane="#313C3B",    # 侧栏 / 工具栏
    tab="#313C3B",     # 标签栏
    surf="#354140",    # 浮层 / 控件面
    ink="#E6EFEC",     # 正文
    ink2="#A9BCB7",    # 次级文字
    ink3="#7E918C",    # 三级文字 / 注释
    line="#3D4A49",    # 实色分隔线
    lineA="#E6EFEC26",  # 半透明分隔线 15%
    q4="#445352",      # 填充档（代码块底 / 分隔条）
    q5="#3A4745",      # 填充档（更深）
    ctrl="#CFDCD8",    # 控件高亮
    prim="#7BA898",    # 釉色主色
    azure="#8FBFAF",   # 次级强调
    acc="#8FC7B6",     # 文字型强调（链接 / 高亮匹配）
    acc2="#A9DCC9",    # 强调（更高一档）
    sel="#7BA89852",   # 选中 32%
    selm="#7BA8984D",  # 选中 30%（列表行）
    sels="#7BA89826",  # 选中 15%（非活动 / 浅底）
    selx="#7BA89814",  # 选中 8%（最浅底）
    # 语法色（语法高亮专用，语义见下）
    kw="#8FC7B6",      # 关键字 / 控制流        —— 釉
    fn="#BFE6D8",      # 函数 / 方法            —— 釉·亮
    ty="#9CC3D5",      # 类型 / 类 / 命名空间    —— 天青
    tyL="#B4D2DE",     # 属性（天青·亮）
    st="#C8BC97",      # 字符串                 —— 米黄釉
    nu="#C79A7E",      # 数字 / 常量 / 布尔      —— 铁足
    pl="#C0A3B2",      # 装饰器 / 正则 / 预处理  —— 紫口
    cm="#7E918C",      # 注释
    err="#D98A7C",     # 错误 / 删除
    jade="#8FBFAF",    # 修改态（比新增浅一档）
    pale="#C6D8D2",    # 参数 / 属性名（掺白）
)
L = dict(
    bg="#F0F5F3", pane="#E8EFEC", tab="#E1EAE7", surf="#F5F9F7",
    ink="#2C3635", ink2="#5F736D", ink3="#8A9C97",
    line="#D6E1DD", lineA="#2C36351F", q4="#D2DEDA", q5="#E1EAE7",
    ctrl="#FBFDFC", prim="#7BA898", azure="#8FBFAF",
    acc="#2A7263", acc2="#1F6B58",
    sel="#7BA89847", selm="#7BA89840", sels="#7BA8981F", selx="#7BA8980F",
    kw="#31705F", fn="#1F8471", ty="#23667B", tyL="#2C6274",
    st="#6B5F2E", nu="#9A5B3D", pl="#8A5570",
    cm="#6E827D", err="#B4453A", jade="#5F9E8B", pale="#4A5A56",
)
NONE = "#00000000"   # 透明：用来关掉某些默认描边

# ============================================================
# 工作台颜色： key -> (深, 浅)
# ============================================================
COLORS = {
    # ---- 全局 ----
    "foreground":                        (D["ink"],   L["ink"]),
    "descriptionForeground":             (D["ink2"],  L["ink2"]),
    "disabledForeground":                (D["ink2"],  L["ink3"]),
    "errorForeground":                   (D["err"],   L["err"]),
    "focusBorder":                       (D["prim"],  L["prim"]),
    "icon.foreground":                   (D["ink2"],  L["ink2"]),
    "selection.background":              (D["sel"],   L["sel"]),
    "sash.hoverBorder":                  (D["prim"],  L["prim"]),
    "window.activeBorder":               (NONE,       NONE),
    "window.inactiveBorder":             (NONE,       NONE),
    "widget.border":                     (D["line"],  L["line"]),
    "widget.shadow":                     ("#00000055", "#2C36351F"),
    "scrollbar.shadow":                  (NONE,       NONE),
    "scrollbarSlider.background":        ("#5A6B6880", "#B9C9C480"),
    "scrollbarSlider.hoverBackground":   ("#7E918CB3", "#8FA9A2B3"),
    "scrollbarSlider.activeBackground":  ("#8FA9A2CC", "#7E9A93CC"),
    "progressBar.background":            (D["prim"],  L["prim"]),
    "badge.background":                  (D["prim"],  L["prim"]),
    "badge.foreground":                  (D["bg"],    L["bg"]),

    # ---- 标题栏 / 命令中心 ----
    "titleBar.activeBackground":         (D["bg"],    L["pane"]),
    "titleBar.activeForeground":         (D["ink"],   L["ink"]),
    "titleBar.inactiveBackground":       (D["bg"],    L["pane"]),
    "titleBar.inactiveForeground":       (D["ink3"],  L["ink3"]),
    "titleBar.border":                   (D["line"],  L["line"]),
    "commandCenter.background":          (D["pane"],  L["surf"]),
    "commandCenter.foreground":          (D["ink2"],  L["ink2"]),
    "commandCenter.border":              (D["line"],  L["line"]),
    "commandCenter.activeBackground":    (D["surf"],  L["surf"]),
    "commandCenter.activeForeground":    (D["ink"],   L["ink"]),
    "commandCenter.activeBorder":        (D["prim"],  L["prim"]),

    # ---- 活动栏 ----
    "activityBar.background":            (D["bg"],    L["pane"]),
    "activityBar.foreground":            (D["ink"],   L["ink"]),
    "activityBar.inactiveForeground":    (D["ink3"],  L["ink3"]),
    "activityBar.border":                (D["line"],  L["line"]),
    "activityBar.activeBorder":          (D["prim"],  L["prim"]),
    "activityBar.activeBackground":      (D["sels"],  L["selx"]),
    "activityBar.activeFocusBorder":     (D["prim"],  L["prim"]),
    "activityBarTop.activeBorder":       (D["prim"],  L["prim"]),
    "activityBarBadge.background":       (D["prim"],  L["prim"]),
    "activityBarBadge.foreground":       (D["bg"],    L["bg"]),
    "activityErrorBadge.background":     (D["err"],   L["err"]),
    "activityErrorBadge.foreground":     (D["bg"],    L["bg"]),
    "activityWarningBadge.background":   (D["st"],    L["st"]),
    "activityWarningBadge.foreground":   (D["bg"],    L["bg"]),
    "modernActivityBar.border":          (D["line"],  L["line"]),
    "modernActivityBarItem.activeBackground": (D["sels"], L["selx"]),
    "modernActivityBarItem.hoverBackground":  ("#E6EFEC14", "#2C36350F"),
    "modernActivityBarItem.activeForeground": (D["ink"],  L["ink"]),
    "modernActivityBarItem.hoverForeground":  (D["ink"],  L["ink"]),
    "actionBar.toggledBackground":       (D["sels"],  L["selx"]),

    # ---- 侧栏 ----
    "sideBar.background":                (D["pane"],  L["pane"]),
    "sideBar.foreground":                (D["ink2"],  L["ink2"]),
    "sideBar.border":                    (D["line"],  L["line"]),
    "sideBar.dropBackground":            (D["sels"],  L["sels"]),
    "sideBarTitle.foreground":           (D["ink"],   L["ink"]),
    "sideBarSectionHeader.background":   (D["pane"],  L["pane"]),
    "sideBarSectionHeader.foreground":   (D["pale"],  L["ink"]),
    "sideBarSectionHeader.border":       (D["line"],  L["line"]),
    "sideBarStickyScroll.shadow":        ("#00000055", "#2C36351F"),

    # ---- 编辑器组 / 标签 ----
    "editorGroup.border":                (D["line"],  L["line"]),
    "editorGroupHeader.tabsBackground":  (D["tab"],   L["tab"]),
    "editorGroupHeader.tabsBorder":      (D["line"],  L["line"]),
    "editorGroupHeader.border":          (NONE,       NONE),
    "editorGroupHeader.noTabsBackground": (D["tab"],  L["tab"]),
    "editorGroup.emptyBackground":       (D["bg"],    L["bg"]),
    "editorGroup.dropBackground":        (D["sels"],  L["sels"]),
    "editorGroup.dropIntoPromptBackground": (D["surf"], L["surf"]),
    "editorGroup.dropIntoPromptForeground": (D["ink"],  L["ink"]),
    "editorGroup.dropIntoPromptBorder":  (D["prim"],  L["prim"]),
    "tab.activeBackground":              (D["bg"],    L["bg"]),
    "tab.activeForeground":              (D["ink"],   L["ink"]),
    "tab.activeBorder":                  (D["bg"],    L["bg"]),
    "tab.activeBorderTop":               (D["prim"],  L["prim"]),
    "tab.selectedBackground":            (D["bg"],    L["bg"]),
    "tab.selectedForeground":            (D["ink"],   L["ink"]),
    "tab.selectedBorderTop":             (D["azure"], L["jade"]),
    "tab.inactiveBackground":            (D["tab"],   L["tab"]),
    "tab.inactiveForeground":            (D["ink3"],  L["ink2"]),
    "tab.border":                        (D["line"],  L["line"]),
    "tab.hoverBackground":               ("#384443",  L["surf"]),
    "tab.hoverForeground":               (D["ink"],   L["ink"]),
    "tab.unfocusedActiveBackground":     (D["pane"],  L["bg"]),
    "tab.unfocusedActiveForeground":     (D["ink2"],  L["ink2"]),
    "tab.unfocusedActiveBorder":         (D["pane"],  L["bg"]),
    "tab.unfocusedActiveBorderTop":      (D["line"],  L["line"]),
    "tab.unfocusedInactiveBackground":   (D["tab"],   L["tab"]),
    "tab.unfocusedInactiveForeground":   (D["ink2"],  L["ink3"]),
    "tab.unfocusedHoverBackground":      ("#384443",  L["surf"]),
    "tab.lastPinnedBorder":              (D["line"],  L["line"]),

    # ---- 编辑器正文 ----
    "editor.background":                 (D["bg"],    L["bg"]),
    "editor.foreground":                 (D["ink"],   L["ink"]),
    "editor.lineHighlightBackground":    ("#E6EFEC0F", "#2C36350A"),
    "editor.selectionBackground":        (D["sel"],   L["sel"]),
    "editor.selectionHighlightBackground": (D["sels"], L["sels"]),
    "editor.inactiveSelectionBackground": (D["sels"], L["sels"]),
    "editor.wordHighlightBackground":    ("#E6EFEC1A", "#2C363514"),
    "editor.wordHighlightStrongBackground": (D["sels"], L["sels"]),
    "editor.findMatchBackground":        ("#C79A7E66", "#C79A7E5A"),
    "editor.findMatchHighlightBackground": ("#C79A7E33", "#C79A7E30"),
    "editor.findRangeHighlightBackground": ("#E6EFEC14", "#2C36350D"),
    "editor.hoverHighlightBackground":   (D["sels"],  L["sels"]),
    "editor.rangeHighlightBackground":   ("#E6EFEC0D", "#2C363508"),
    "editorWhitespace.foreground":       ("#E6EFEC1F", "#2C36351A"),
    "editorLineNumber.foreground":       (D["ink2"],  L["ink3"]),
    "editorLineNumber.activeForeground": (D["ink2"],  L["ink"]),
    "editorCursor.foreground":           (D["prim"],  "#2F7F6C"),
    "editorCursor.background":           (D["bg"],    L["bg"]),
    "editorMultiCursor.primary.foreground":   (D["prim"], "#2F7F6C"),
    "editorMultiCursor.secondary.foreground": (D["st"],   L["st"]),
    "editorRuler.foreground":            (D["line"],  L["line"]),
    "editorIndentGuide.background":      ("#E6EFEC14", "#2C36350F"),
    "editorIndentGuide.background1":     ("#E6EFEC14", "#2C36350F"),
    "editorIndentGuide.activeBackground": (D["prim"] + "66", L["prim"] + "80"),
    "editorIndentGuide.activeBackground1": (D["prim"] + "66", L["prim"] + "80"),
    "editorCodeLens.foreground":         (D["cm"],    L["cm"]),
    "editorLink.activeForeground":       (D["acc"],   L["acc"]),
    "editorLightBulb.foreground":        (D["st"],    L["st"]),
    "editorLightBulbAutoFix.foreground": (D["prim"],  L["acc"]),
    "editorBracketMatch.background":     (D["sels"],  L["sels"]),
    "editorBracketMatch.border":         (D["prim"],  "#4E8F7C"),
    "editorBracketHighlight.foreground1": (D["kw"],   L["acc"]),
    "editorBracketHighlight.foreground2": (D["ty"],   L["ty"]),
    "editorBracketHighlight.foreground3": (D["st"],   L["st"]),
    "editorBracketHighlight.foreground4": (D["nu"],   L["nu"]),
    "editorBracketHighlight.foreground5": (D["pl"],   L["pl"]),
    "editorBracketHighlight.foreground6": (D["ink2"], L["ink2"]),
    "editorBracketHighlight.unexpectedBracket.foreground": (D["err"], L["err"]),
    "editorBracketPairGuide.background1": (("#E6EFEC12"), ("#2C36350D")),
    "editorBracketPairGuide.background2": (("#E6EFEC12"), ("#2C36350D")),
    "editorBracketPairGuide.background3": (("#E6EFEC12"), ("#2C36350D")),
    "editorBracketPairGuide.background4": (("#E6EFEC12"), ("#2C36350D")),
    "editorBracketPairGuide.background5": (("#E6EFEC12"), ("#2C36350D")),
    "editorBracketPairGuide.background6": (("#E6EFEC12"), ("#2C36350D")),
    "editorBracketPairGuide.activeBackground1": (D["kw"] + "66", L["acc"] + "80"),
    "editorBracketPairGuide.activeBackground2": (D["ty"] + "66", L["ty"] + "80"),
    "editorBracketPairGuide.activeBackground3": (D["st"] + "66", L["st"] + "80"),
    "editorBracketPairGuide.activeBackground4": (D["nu"] + "66", L["nu"] + "80"),
    "editorBracketPairGuide.activeBackground5": (D["pl"] + "66", L["pl"] + "80"),
    "editorBracketPairGuide.activeBackground6": (D["ink2"] + "66", L["ink2"] + "80"),
    "editorGutter.background":           (D["bg"],    L["bg"]),
    "editorGutter.addedBackground":      (D["prim"],  "#4E8F7C"),
    "editorGutter.modifiedBackground":   (D["azure"], L["jade"]),
    "editorGutter.deletedBackground":    (D["err"],   L["err"]),
    "editorGutter.commentRangeForeground": (D["cm"],  L["cm"]),
    "editorGutter.foldingControlForeground": (D["ink2"], L["ink2"]),
    "editorError.foreground":            (D["err"],   L["err"]),
    "editorError.border":                (NONE,       NONE),
    "editorWarning.foreground":          (D["st"],    L["st"]),
    "editorWarning.border":              (NONE,       NONE),
    "editorInfo.foreground":             (D["ty"],    L["ty"]),
    "editorInfo.border":                 (NONE,       NONE),
    "editorHint.foreground":             (D["kw"],    L["acc"]),
    "editorHint.border":                 (NONE,       NONE),
    "editorUnnecessaryCode.border":      ("#E6EFEC33", "#2C363326"),
    "editorUnnecessaryCode.opacity":     (D["bg"] + "AA", L["bg"] + "C0"),
    "editorGhostText.foreground":        (D["cm"],    L["ink3"]),
    "editorGhostText.background":        (NONE,       NONE),
    "editorGhostText.border":            (NONE,       NONE),
    "editorInlayHint.foreground":        (D["cm"],    L["cm"]),
    "editorInlayHint.background":        (D["selx"],  L["selx"]),
    "editorInlayHint.typeForeground":    (D["ink2"],  L["ink2"]),
    "editorInlayHint.typeBackground":    (NONE,       NONE),
    "editorInlayHint.parameterForeground": (D["cm"],  L["cm"]),
    "editorInlayHint.parameterBackground": (NONE,     NONE),
    "editorMarkerNavigation.background": (D["surf"],  L["surf"]),
    "editorMarkerNavigationError.background": (D["err"], L["err"]),
    "editorMarkerNavigationWarning.background": (D["st"], L["st"]),
    "editorMarkerNavigationInfo.background": (D["ty"], L["ty"]),
    "editorStickyScroll.background":     (D["pane"],  L["pane"]),
    "editorStickyScroll.border":         (D["line"],  L["line"]),
    "editorStickyScroll.shadow":         ("#00000055", "#2C36351F"),
    "editorStickyScrollHover.background": (D["sels"], L["sels"]),
    "editorPane.background":             (D["bg"],    L["bg"]),
    "editorCommentsWidget.rangeBackground": (D["selx"], L["selx"]),
    "editorCommentsWidget.rangeActiveBackground": (D["sels"], L["sels"]),
    "editorCommentsWidget.replyInputBackground": (D["surf"], L["surf"]),
    "editorCommentsWidget.resolvedBorder": (D["prim"] + "99", L["prim"] + "99"),
    "editorCommentsWidget.unresolvedBorder": (D["st"] + "99", L["st"] + "99"),
    "sideBySideEditor.horizontalBorder": (D["line"],  L["line"]),
    "sideBySideEditor.verticalBorder":   (D["line"],  L["line"]),

    # ---- 缩略图 ----
    "minimap.background":                (D["bg"],    L["bg"]),
    "minimap.selectionHighlight":        (D["sel"],   L["sel"]),
    "minimap.findMatchHighlight":        ("#C79A7E80", "#C79A7E80"),
    "minimap.errorHighlight":            (D["err"],   L["err"]),
    "minimap.warningHighlight":          (D["st"],    L["st"]),
    "minimap.infoHighlight":             (D["ty"],    L["ty"]),
    "minimapSlider.background":          ("#E6EFEC1A", "#2C363513"),
    "minimapSlider.hoverBackground":     ("#E6EFEC29", "#2C363526"),
    "minimapSlider.activeBackground":    (D["selm"],  L["selm"]),
    "minimapGutter.addedBackground":     (D["prim"],  "#4E8F7C"),
    "minimapGutter.modifiedBackground":  (D["azure"], L["jade"]),
    "minimapGutter.deletedBackground":   (D["err"],   L["err"]),

    # ---- 概览标尺 ----
    "editorOverviewRuler.border":        (D["bg"],    L["bg"]),
    "editorOverviewRuler.findMatchForeground": ("#C79A7E99", "#C79A7E99"),
    "editorOverviewRuler.rangeHighlightForeground": ("#7BA89899", "#7BA89899"),
    "editorOverviewRuler.selectionHighlightForeground": (D["sel"], L["sel"]),
    "editorOverviewRuler.wordHighlightForeground": ("#E6EFEC66", "#2C363566"),
    "editorOverviewRuler.wordHighlightStrongForeground": ("#7BA89899", "#7BA89880"),
    "editorOverviewRuler.modifiedForeground": (D["azure"], L["jade"]),
    "editorOverviewRuler.addedForeground": (D["prim"], "#4E8F7C"),
    "editorOverviewRuler.deletedForeground": (D["err"], L["err"]),
    "editorOverviewRuler.errorForeground": (D["err"], L["err"]),
    "editorOverviewRuler.warningForeground": (D["st"], L["st"]),
    "editorOverviewRuler.infoForeground": (D["ty"],  L["ty"]),
    "editorOverviewRuler.bracketMatchForeground": (D["cm"], L["cm"]),
    "editorOverviewRuler.currentContentForeground": ("#7BA89899", "#7BA89899"),
    "editorOverviewRuler.incomingContentForeground": ("#9CC3D599", "#23667B99"),
    "editorOverviewRuler.commonContentForeground": ("#3D4A49B3", "#C3D1CDB3"),

    # ---- 浮动控件 ----
    "editorWidget.background":           (D["surf"],  L["surf"]),
    "editorWidget.foreground":           (D["ink"],   L["ink"]),
    "editorWidget.border":               (D["line"],  L["line"]),
    "editorHoverWidget.background":      (D["surf"],  L["surf"]),
    "editorHoverWidget.foreground":      (D["ink"],   L["ink"]),
    "editorHoverWidget.border":          (D["line"],  L["line"]),
    "editorHoverWidget.statusBarBackground": (D["pane"], L["pane"]),
    "editorSuggestWidget.background":    (D["surf"],  L["surf"]),
    "editorSuggestWidget.foreground":    (D["ink"],   L["ink"]),
    "editorSuggestWidget.border":        (D["line"],  L["line"]),
    "editorSuggestWidget.selectedBackground": (D["selm"], L["selm"]),
    "editorSuggestWidget.selectedForeground": (D["ink"], L["ink"]),
    "editorSuggestWidget.selectedIconForeground": (D["ink"], L["ink"]),
    "editorSuggestWidget.highlightForeground": (D["acc"], L["acc"]),
    "editorSuggestWidget.focusOutline":  (D["prim"],  L["prim"]),
    "editorSuggestWidgetStatus.foreground": (D["cm"], L["cm"]),
    "debugToolBar.background":           (D["surf"],  L["surf"]),
    "debugExceptionWidget.background":   (D["err"] + "26", L["err"] + "1F"),
    "debugExceptionWidget.border":       (D["err"],   L["err"]),

    # ---- peek 视图 ----
    "peekView.border":                   (D["prim"],  L["prim"]),
    "peekViewEditor.background":         (D["pane"],  L["pane"]),
    "peekViewEditor.matchHighlightBackground": ("#C79A7E4D", "#C79A7E4D"),
    "peekViewResult.background":         (D["bg"],    L["bg"]),
    "peekViewResult.fileForeground":     (D["ink"],   L["ink"]),
    "peekViewResult.lineForeground":     (D["ink2"],  L["ink2"]),
    "peekViewResult.matchHighlightBackground": ("#C79A7E4D", "#C79A7E4D"),
    "peekViewResult.selectionBackground": (D["selm"], L["selm"]),
    "peekViewResult.selectionForeground": (D["ink"],  L["ink"]),
    "peekViewTitle.background":          (D["pane"],  L["pane"]),
    "peekViewTitleDescription.foreground": (D["ink2"], L["ink2"]),
    "peekViewTitleLabel.foreground":     (D["ink"],   L["ink"]),

    # ---- 面板 / 终端 ----
    "panel.background":                  (D["bg"],    L["pane"]),
    "panel.border":                      (D["line"],  L["line"]),
    "panelTitle.activeBorder":           (D["prim"],  L["prim"]),
    "panelTitle.activeForeground":       (D["ink"],   L["ink"]),
    "panelTitle.inactiveForeground":     (D["ink3"],  L["ink3"]),
    "panelTitle.border":                 (D["line"],  L["line"]),
    "panelInput.border":                 (D["line"],  L["line"]),
    "panelSection.border":               (D["line"],  L["line"]),
    "panelSectionHeader.background":     (D["pane"],  L["tab"]),
    "panelSectionHeader.foreground":     (D["ink"],   L["ink"]),
    "panelStickyScroll.background":      (D["bg"],    L["pane"]),
    "panelStickyScroll.border":          (D["line"],  L["line"]),
    "terminal.background":               (D["bg"],    L["pane"]),
    "terminal.foreground":               (D["ink"],   L["ink"]),
    "terminal.border":                   (D["line"],  L["line"]),
    "terminal.selectionBackground":      (D["sel"],   L["sel"]),
    "terminal.inactiveSelectionBackground": (D["sels"], L["sels"]),
    "terminal.tab.activeBorder":         (D["prim"],  L["prim"]),
    "terminal.findMatchBackground":      ("#C79A7E66", "#C79A7E5A"),
    "terminal.findMatchBorder":          ("#C79A7E",   "#C79A7E"),
    "terminalCursor.foreground":         (D["prim"],  "#2F7F6C"),
    "terminalCursor.background":         (D["bg"],    L["bg"]),
    "terminalStickyScroll.background":   (D["bg"],    L["pane"]),
    "terminalStickyScrollHover.background": (D["surf"], L["surf"]),
    # 终端 16 色：同一套语义，浅色模式压暗
    "terminal.ansiBlack":                ("#3D4A49",  "#2C3635"),
    "terminal.ansiRed":                  ("#C0796A",  "#A8433A"),
    "terminal.ansiGreen":                ("#7BA898",  "#357F6A"),
    "terminal.ansiYellow":               ("#C8BC97",  "#8A6E1F"),
    "terminal.ansiBlue":                 ("#9CC3D5",  "#23667B"),
    "terminal.ansiMagenta":              ("#C0A3B2",  "#8A5570"),
    "terminal.ansiCyan":                 ("#8FC7B6",  "#2F7F6C"),
    "terminal.ansiWhite":                ("#CFDCD8",  "#6E827D"),
    "terminal.ansiBrightBlack":          ("#5F736D",  "#5F736D"),
    "terminal.ansiBrightRed":            ("#D98A7C",  "#C0564A"),
    "terminal.ansiBrightGreen":          ("#8FC7B6",  "#4E8F7C"),
    "terminal.ansiBrightYellow":         ("#D8CFA9",  "#A88A2E"),
    "terminal.ansiBrightBlue":           ("#AECFDD",  "#3A7E93"),
    "terminal.ansiBrightMagenta":        ("#CDB3C0",  "#A06E86"),
    "terminal.ansiBrightCyan":           ("#A9DCC9",  "#4E9E8C"),
    "terminal.ansiBrightWhite":          ("#E6EFEC",  "#3F4E4B"),

    # ---- 列表 / 树 ----
    "list.activeSelectionBackground":    (D["selm"],  L["selm"]),
    "list.activeSelectionForeground":    (D["ink"],   L["ink"]),
    "list.activeSelectionIconForeground": (D["ink"],  L["ink"]),
    "list.inactiveSelectionBackground":  (D["sels"],  L["sels"]),
    "list.inactiveSelectionForeground":  (D["ink"],   L["ink"]),
    "list.focusBackground":              (D["selm"],  L["selm"]),
    "list.focusForeground":              (D["ink"],   L["ink"]),
    "list.focusOutline":                 (D["prim"],  L["prim"]),
    "list.focusAndSelectionOutline":     (D["prim"],  L["prim"]),
    "list.inactiveFocusBackground":      (D["sels"],  L["sels"]),
    "list.inactiveFocusOutline":         (D["prim"] + "80", L["prim"] + "80"),
    "list.hoverBackground":              ("#E6EFEC14", "#2C36350F"),
    "list.hoverForeground":              (D["ink"],   L["ink"]),
    "list.highlightForeground":          (D["acc"],   L["acc"]),
    "list.focusHighlightForeground":     (D["acc2"],  L["acc"]),
    "list.dropBackground":               (D["sels"],  L["sels"]),
    "list.errorForeground":              (D["err"],   L["err"]),
    "list.warningForeground":            (D["st"],    L["st"]),
    "list.invalidItemForeground":        (D["err"],   L["err"]),
    "list.deemphasizedForeground":       (D["cm"],    L["ink3"]),
    "list.filterMatchBackground":        ("#C79A7E33", "#C79A7E30"),
    "list.filterMatchBorder":            ("#C79A7E",   "#C79A7E"),
    "listFilterWidget.shadow":           ("#00000055", "#2C36351F"),
    "tree.indentGuidesStroke":           ("#E6EFEC1F", "#2C36351A"),

    # ---- 输入 / 按钮 / 下拉 ----
    "input.background":                  (D["bg"],    L["ctrl"]),
    "input.foreground":                  (D["ink"],   L["ink"]),
    "input.border":                      (D["line"],  L["line"]),
    "input.placeholderForeground":       (D["ink3"],  L["ink3"]),
    "inputOption.activeBackground":      (D["selm"],  L["selm"]),
    "inputOption.activeBorder":          (D["prim"],  L["prim"]),
    "inputOption.activeForeground":      (D["ink"],   L["ink"]),
    "inputOption.hoverBackground":       ("#E6EFEC14", "#2C36350F"),
    "inputValidation.errorBackground":   (D["err"],   "#D9A79B"),
    "inputValidation.errorForeground":   (D["bg"],    L["bg"]),
    "inputValidation.errorBorder":       ("#B4623F",  "#A8433A"),
    "inputValidation.warningBackground": (D["st"],    "#E0D6B2"),
    "inputValidation.warningForeground": (D["bg"],    L["bg"]),
    "inputValidation.warningBorder":     ("#A88A2E",  L["st"]),
    "inputValidation.infoBackground":    (D["ty"],    "#C3DCE6"),
    "inputValidation.infoForeground":    (D["bg"],    L["bg"]),
    "inputValidation.infoBorder":        ("#5F9EB5",  L["ty"]),
    "dropdown.background":               (D["surf"],  L["ctrl"]),
    "dropdown.foreground":               (D["ink"],   L["ink"]),
    "dropdown.border":                   (D["line"],  L["line"]),
    "dropdown.listBackground":           (D["surf"],  L["ctrl"]),
    "checkbox.background":               (D["bg"],    L["ctrl"]),
    "checkbox.foreground":               (D["ink"],   L["ink"]),
    "checkbox.border":                   (D["line"],  "#C3D1CD"),
    "button.background":                 (D["prim"],  L["prim"]),
    "button.foreground":                 (D["bg"],    L["bg"]),
    "button.hoverBackground":            (D["azure"], "#6E9C8C"),
    "button.border":                     (NONE,       NONE),
    "button.secondaryBackground":        (D["line"],  L["q4"]),
    "button.secondaryForeground":        (D["ink"],   L["ink"]),
    "button.secondaryHoverBackground":   (D["q4"],    "#C3D1CD"),
    "button.secondaryBorder":            (NONE,       NONE),
    "extensionButton.prominentBackground": (D["prim"], L["prim"]),
    "extensionButton.prominentForeground": (D["bg"],   L["bg"]),
    "extensionButton.prominentHoverBackground": (D["azure"], "#6E9C8C"),
    "keybindingLabel.foreground":        (D["ink2"],  L["ink2"]),
    "pickerGroup.foreground":            (D["acc"],   L["acc"]),
    "pickerGroup.border":                (D["line"],  L["line"]),

    # ---- 菜单 ----
    "menu.background":                   (D["surf"],  L["surf"]),
    "menu.foreground":                   (D["ink"],   L["ink"]),
    "menu.border":                       (D["line"],  L["line"]),
    "menu.selectionBackground":          (D["selm"],  L["selm"]),
    "menu.selectionForeground":          (D["ink"],   L["ink"]),
    "menu.selectionBorder":              (D["prim"],  L["prim"]),
    "menu.separatorBackground":          (D["line"],  L["line"]),
    "menubar.selectionBackground":       ("#E6EFEC1A", "#2C363513"),
    "menubar.selectionForeground":       (D["ink"],   L["ink"]),

    # ---- 快速输入 ----
    "quickInput.background":             (D["surf"],  L["surf"]),
    "quickInput.foreground":             (D["ink"],   L["ink"]),
    "quickInput.border":                 (D["line"],  L["line"]),
    "quickInputTitle.background":        (D["pane"],  L["pane"]),
    "quickInputList.focusBackground":    (D["selm"],  L["selm"]),
    "quickInputList.focusForeground":    (D["ink"],   L["ink"]),
    "quickInputList.focusIconForeground": (D["ink"],  L["ink"]),
    "quickInputList.focusHighlightForeground": (D["acc"], L["acc"]),
    "quickInputList.hoverBackground":    ("#E6EFEC14", "#2C36350F"),

    # ---- 通知 ----
    "notifications.background":          (D["surf"],  L["surf"]),
    "notifications.foreground":          (D["ink"],   L["ink"]),
    "notifications.border":              (D["line"],  L["line"]),
    "notificationCenter.border":         (D["line"],  L["line"]),
    "notificationCenterHeader.background": (D["pane"], L["pane"]),
    "notificationCenterHeader.foreground": (D["ink"],  L["ink"]),
    "notificationToast.border":          (D["line"],  L["line"]),
    "notificationLink.foreground":       (D["acc"],   L["acc"]),
    "notificationsErrorIcon.foreground": (D["err"],   L["err"]),
    "notificationsWarningIcon.foreground": (D["st"],  L["st"]),
    "notificationsInfoIcon.foreground":  (D["ty"],    L["ty"]),

    # ---- 状态栏（整条上釉）----
    "statusBar.background":              (D["prim"],  L["prim"]),
    "statusBar.foreground":              (D["bg"],    L["bg"]),
    "statusBar.border":                  (D["prim"],  L["prim"]),
    "statusBar.noFolderBackground":      (D["ink2"],  "#8FA9A2"),
    "statusBar.noFolderForeground":      (D["ink"],   L["bg"]),
    "statusBar.debuggingBackground":     (D["nu"],    L["nu"]),
    "statusBar.debuggingForeground":     (D["bg"],    L["bg"]),
    "statusBar.focusBorder":             (D["bg"],    L["bg"]),
    "statusBarItem.hoverBackground":     ("#2C363529", "#2C363524"),
    "statusBarItem.hoverForeground":     (D["bg"],    L["bg"]),
    "statusBarItem.activeBackground":    ("#2C36353D", "#2C363533"),
    "statusBarItem.compactHoverBackground": ("#2C363529", "#2C363524"),
    "statusBarItem.prominentBackground": ("#2C36354D", "#2C36354D"),
    "statusBarItem.prominentForeground": (D["ink"],   D["ink"]),
    "statusBarItem.prominentHoverBackground": ("#2C363566", "#2C363566"),
    "statusBarItem.prominentHoverForeground": (D["ink"], D["ink"]),
    "statusBarItem.remoteBackground":    (D["azure"], L["azure"]),
    "statusBarItem.remoteForeground":    (D["bg"],    L["bg"]),
    "statusBarItem.errorBackground":     ("#C0796A",  "#B4453A"),
    "statusBarItem.focusBorder":         (D["bg"],    L["bg"]),

    # ---- 面包屑 ----
    "breadcrumb.background":             (D["bg"],    L["bg"]),
    "breadcrumb.foreground":             (D["ink3"],  L["ink3"]),
    "breadcrumb.focusForeground":        (D["ink"],   L["ink"]),
    "breadcrumb.activeSelectionForeground": (D["ink"], L["ink"]),
    "breadcrumbPicker.background":       (D["surf"],  L["surf"]),

    # ---- 设置页 / 搜索 ----
    "settings.headerForeground":         (D["ink"],   L["ink"]),
    "settings.modifiedItemIndicator":    ("#C79A7E",  "#C79A7E"),
    "settings.dropdownBackground":       (D["bg"],    L["ctrl"]),
    "settings.dropdownBorder":           (D["line"],  L["line"]),
    "settings.textInputBorder":          (D["line"],  L["line"]),
    "settings.numberInputBorder":        (D["line"],  L["line"]),
    "searchEditor.textInputBorder":      (D["line"],  L["line"]),
    "searchEditor.findMatchBackground":  ("#C79A7E66", "#C79A7E5A"),
    "searchEditor.findMatchBorder":      ("#C79A7E",   "#C79A7E"),

    # ---- Git ----
    "gitDecoration.addedResourceForeground":     (D["prim"], "#4E8F7C"),
    "gitDecoration.modifiedResourceForeground":  (D["st"],   L["st"]),
    "gitDecoration.deletedResourceForeground":   (D["err"],  L["err"]),
    "gitDecoration.renamedResourceForeground":   (D["jade"], L["jade"]),
    "gitDecoration.stageModifiedResourceForeground": (D["prim"], "#4E8F7C"),
    "gitDecoration.stageDeletedResourceForeground":  (D["err"],  L["err"]),
    "gitDecoration.untrackedResourceForeground": (D["jade"], L["jade"]),
    "gitDecoration.ignoredResourceForeground":   ("#5F736D", "#A6B4B0"),
    "gitDecoration.conflictingResourceForeground": (D["pl"], L["pl"]),
    "gitDecoration.submoduleResourceForeground": (D["cm"],   L["ink3"]),
    "git.blame.editorDecorationForeground":      (D["cm"],   L["ink3"]),

    # ---- 差异 / 合并 ----
    "diffEditor.insertedTextBackground": ("#7BA89829", "#7BA89826"),
    "diffEditor.removedTextBackground":  ("#C0796A29", "#C0796A26"),
    "diffEditor.insertedLineBackground": (D["selx"],  L["selx"]),
    "diffEditor.removedLineBackground":  ("#C0796A1F", "#C0796A1A"),
    "diffEditor.diagonalFill":           (D["line"],  L["line"]),
    "diffEditor.border":                 (D["line"],  L["line"]),
    "diffEditor.unchangedRegionBackground": (D["pane"], L["pane"]),
    "diffEditor.move.border":            (D["st"],    L["st"]),
    "diffEditor.moveActive.border":      (D["nu"],    L["nu"]),
    "diffEditorGutter.insertedLineBackground": (D["selx"], L["selx"]),
    "diffEditorGutter.removedLineBackground": ("#C0796A1F", "#C0796A1A"),
    "diffEditorOverview.insertedForeground": ("#7BA898", "#4E8F7C"),
    "diffEditorOverview.removedForeground":  ("#C0796A", L["err"]),
    "merge.border":                      (NONE,       NONE),
    "merge.currentHeaderBackground":     ("#7BA89826", "#7BA89826"),
    "merge.currentContentBackground":    (D["selx"],  "#7BA8981A"),
    "merge.incomingHeaderBackground":    ("#9CC3D526", "#9CC3D526"),
    "merge.incomingContentBackground":   (D["selx"],  "#9CC3D51A"),
    "merge.commonHeaderBackground":      ("#3D4A4926", "#D6E1DD3D"),
    "merge.commonContentBackground":     ("#3D4A4914", "#D6E1DD26"),

    # ---- 笔记本 ----
    "notebook.editorBackground":         (D["bg"],    L["bg"]),
    "notebook.cellEditorBackground":     (D["bg"],    L["bg"]),
    "notebook.cellBorderColor":          (D["line"],  L["line"]),
    "notebook.cellHoverBackground":      ("#E6EFEC0D", "#2C363508"),
    "notebook.cellStatusBarItemHoverBackground": ("#E6EFEC1F", "#2C363513"),
    "notebook.cellToolbarSeparator":     (D["line"],  L["line"]),
    "notebook.cellInsertionIndicator":   (D["prim"],  L["prim"]),
    "notebook.outputContainerBackgroundColor": (D["pane"], L["pane"]),
    "notebook.outputContainerBorderColor": (D["line"], L["line"]),
    "notebook.focusedCellBorder":        (D["prim"],  L["prim"]),
    "notebook.focusedCellBackground":    (D["pane"],  L["pane"]),
    "notebook.focusedEditorBorder":      (D["prim"],  L["prim"]),
    "notebook.selectedCellBorder":       (D["line"],  L["line"]),
    "notebook.inactiveSelectedCellBorder": (D["prim"] + "80", L["prim"] + "80"),
    "notebook.selectedCellBackground":   (D["sels"],  L["selx"]),
    "notebook.symbolHighlightBackground": (D["sels"], L["sels"]),
    "notebookStatusSuccessIcon.foreground": (D["prim"], "#4E8F7C"),
    "notebookStatusErrorIcon.foreground": (D["err"],  L["err"]),
    "notebookStatusRunningIcon.foreground": (D["ty"], L["ty"]),

    # ---- 测试 ----
    "testing.iconPassed":                (D["prim"],  "#4E8F7C"),
    "testing.iconFailed":                (D["err"],   L["err"]),
    "testing.iconQueued":                (D["st"],    L["st"]),
    "testing.iconUnset":                 (D["cm"],    L["ink3"]),
    "testing.iconSkipped":               (D["cm"],    L["ink3"]),
    "testing.runAction":                 (D["prim"],  "#4E8F7C"),
    "testing.coverCountBadgeBackground": (D["prim"],  L["prim"]),
    "testing.coverCountBadgeForeground": (D["bg"],    L["bg"]),
    "testing.message.info.decorationForeground": (D["cm"], L["cm"]),

    # ---- 调试 ----
    "debugIcon.breakpointForeground":    ("#C0796A",  L["err"]),
    "debugIcon.breakpointDisabledForeground": (D["cm"], "#A6B4B0"),
    "debugIcon.breakpointUnverifiedForeground": (D["cm"], L["ink3"]),
    "debugIcon.breakpointCurrentStackframeForeground": (D["st"], L["st"]),
    "debugIcon.breakpointStackframeForeground": (D["prim"], "#4E8F7C"),
    "debugIcon.startForeground":         (D["prim"],  "#4E8F7C"),
    "debugIcon.pauseForeground":         (D["ty"],    L["ty"]),
    "debugIcon.stopForeground":          ("#C0796A",  L["err"]),
    "debugIcon.disconnectForeground":    ("#C0796A",  L["err"]),
    "debugIcon.restartForeground":       (D["prim"],  "#4E8F7C"),
    "debugIcon.stepOverForeground":      (D["acc"],   L["acc"]),
    "debugIcon.stepIntoForeground":      (D["acc"],   L["acc"]),
    "debugIcon.stepOutForeground":       (D["acc"],   L["acc"]),
    "debugIcon.continueForeground":      (D["prim"],  "#4E8F7C"),
    "debugIcon.stepBackForeground":      (D["acc"],   L["acc"]),
    "debugConsole.infoForeground":       (D["ty"],    L["ty"]),
    "debugConsole.errorForeground":      (D["err"],   L["err"]),
    "debugConsole.warningForeground":    (D["st"],    L["st"]),
    "debugConsole.sourceForeground":     (D["acc"],   L["acc"]),
    "debugConsoleInputIcon.foreground":  (D["acc"],   L["acc"]),
    "debugTokenExpression.name":         (D["pale"],  L["ink"]),
    "debugTokenExpression.value":        (D["nu"],    L["nu"]),
    "debugTokenExpression.string":       (D["st"],    L["st"]),
    "debugTokenExpression.number":       (D["nu"],    L["nu"]),
    "debugTokenExpression.boolean":      (D["nu"],    L["nu"]),
    "debugTokenExpression.error":        (D["err"],   L["err"]),
    "debugTokenExpression.type":         (D["ty"],    L["ty"]),
    "debugView.exceptionLabelForeground": (D["bg"],   L["bg"]),
    "debugView.exceptionLabelBackground": ("#C0796A", L["err"]),
    "debugView.stateLabelForeground":    (D["ink"],   L["ink"]),
    "debugView.stateLabelBackground":    (D["selm"],  L["selm"]),
    "debugView.valueChangedHighlight":   (D["selm"],  L["selm"]),

    # ---- 图表（设置页里的彩色图）----
    "charts.foreground":                 (D["ink"],   L["ink"]),
    "charts.lines":                      (D["ink3"],  L["ink3"]),
    "charts.red":                        ("#C0796A",  L["err"]),
    "charts.blue":                       (D["ty"],    L["ty"]),
    "charts.yellow":                     (D["st"],    L["st"]),
    "charts.orange":                     (D["nu"],    L["nu"]),
    "charts.green":                      (D["prim"],  "#4E8F7C"),
    "charts.purple":                     (D["pl"],    L["pl"]),

    # ---- 标记 / 端口 / 仪表 ----
    "problemsErrorIcon.foreground":      (D["err"],   L["err"]),
    "problemsWarningIcon.foreground":    (D["st"],    L["st"]),
    "problemsInfoIcon.foreground":       (D["ty"],    L["ty"]),
    "ports.iconRunningProcessForeground": (D["prim"], "#4E8F7C"),
    "gauge.background":                  ("#E6EFEC1F", "#2C363514"),
    "gauge.foreground":                  (D["ink2"],  L["ink2"]),
    "gauge.border":                      (D["line"],  L["line"]),
    "gauge.errorBackground":             ("#C0796A",  L["err"]),
    "gauge.errorForeground":             (D["ink"],   L["bg"]),
    "gauge.warningBackground":           (D["st"],    L["st"]),
    "gauge.warningForeground":           (D["bg"],    L["bg"]),
    "toolbar.hoverBackground":           ("#E6EFEC1A", "#2C363513"),
    "toolbar.activeBackground":          ("#E6EFEC14", "#2C36350F"),
    "toolbar.hoverOutline":              (D["prim"],  L["prim"]),

    # ---- 欢迎页 / 引导 ----
    "welcomePage.background":            (D["bg"],    L["bg"]),
    "welcomePage.tileBackground":        (D["pane"],  L["pane"]),
    "welcomePage.tileHoverBackground":   (D["surf"],  L["surf"]),
    "welcomePage.tileBorder":            (D["line"],  L["line"]),
    "welcomePage.progress.foreground":   (D["prim"],  L["prim"]),
    "walkThrough.embeddedEditorBackground": (D["bg"], L["bg"]),

    # ---- 行内 AI / 聊天 / 智能体面板 ----
    "inlineChat.background":             (D["surf"],  L["surf"]),
    "inlineChat.foreground":             (D["ink"],   L["ink"]),
    "inlineChat.border":                 (D["prim"],  L["prim"]),
    "inlineChat.shadow":                 ("#00000055", "#2C36351F"),
    "inlineChatDiff.inserted":           ("#7BA89833", "#7BA89826"),
    "inlineChatDiff.removed":            ("#C0796A33", "#C0796A26"),
    "chat.slashCommandBackground":       ("#7BA89833", "#7BA89826"),
    "chat.slashCommandForeground":       (D["acc"],   L["acc"]),
    "chat.editedFileForeground":         (D["st"],    L["st"]),
    "chat.requestBubbleBackground":      (D["surf"],  L["surf"]),
    "chat.requestBubbleHoverBackground": (D["line"],  L["pane"]),
    "chat.thinkingShimmer":              (D["acc"],   L["acc"]),
    "chat.inputWorkingBorderColor1":     (D["prim"],  L["prim"]),
    "chat.inputWorkingBorderColor2":     (D["acc"],   L["acc"]),
    "chat.inputWorkingBorderColor3":     (D["acc2"],  L["acc2"]),
    "agents.background":                 (D["pane"],  L["pane"]),
    "agentsPanel.background":            (D["pane"],  L["pane"]),
    "agentsPanel.foreground":            (D["ink"],   L["ink"]),
    "agentsPanel.border":                (D["line"],  L["line"]),
    "agentsBottomPanel.border":          (D["line"],  L["line"]),
    "agentsCard.border":                 (D["line"],  L["line"]),
    "agentsChatInput.background":        (D["pane"],  L["ctrl"]),
    "agentsChatInput.foreground":        (D["ink"],   L["ink"]),
    "agentsChatInput.border":            (D["line"],  L["line"]),
    "agentsChatInput.focusBorder":       (D["prim"],  L["prim"]),
    "agentsChatInput.placeholderForeground": (D["ink3"], L["ink3"]),
    "agentsNewSessionButton.background": (D["prim"],  L["prim"]),
    "agentsNewSessionButton.foreground": (D["bg"],    L["bg"]),
    "agentsNewSessionButton.border":     (NONE,       NONE),
    "agentsNewSessionButton.hoverBackground": (D["azure"], "#6E9C8C"),
    "agentsBadge.background":            (D["prim"],  L["prim"]),
    "agentsBadge.foreground":            (D["bg"],    L["bg"]),
    "agentsUnreadBadge.background":      (D["prim"],  L["prim"]),
    "agentsUnreadBadge.foreground":      (D["bg"],    L["bg"]),
    "agentsGradient.tintColor":          (D["selx"],  L["selx"]),
    "agentStatusIndicator.background":   (D["prim"],  L["prim"]),

    # ---- 文本 / markdown 预览 ----
    "textBlockQuote.background":         (D["pane"],  L["pane"]),
    "textBlockQuote.border":             (D["prim"],  L["prim"]),
    "textCodeBlock.background":          ("#E6EFEC14", "#2C36350F"),
    "textLink.foreground":               (D["acc"],   L["acc"]),
    "textLink.activeForeground":         (D["acc2"],  L["acc2"]),
    "textPreformat.foreground":          (D["st"],    L["st"]),
    "textPreformat.background":          ("#E6EFEC14", "#2C36350F"),
    "textSeparator.foreground":          ("#E6EFEC1F", "#2C363514"),
}


# ============================================================
# 语法高亮：与 VS Code 自带 dark_vs/dark_plus 同一套 scope 表，只换色
# 顺序 = 优先级（后面的覆盖前面的）
# ============================================================
def tokens(P):
    ink, ink2, cm, kw, fn, ty, tyL, st, nu, pl, err = (
        P["ink"], P["ink2"], P["cm"], P["kw"], P["fn"],
        P["ty"], P["tyL"], P["st"], P["nu"], P["pl"], P["err"])

    def r(scope, **settings):
        return {"scope": scope, "settings": settings}

    return [
        r(["meta.embedded", "source.groovy.embedded", "string meta.image.inline.markdown",
           "variable.legacy.builtin.python"], foreground=ink),
        r("emphasis", fontStyle="italic"),
        r("strong", fontStyle="bold"),
        r("header", foreground=kw, fontStyle="bold"),
        r("comment", foreground=cm),
        r("invalid", foreground=err),
        r("invalid.deprecated", foreground=cm, fontStyle="strikethrough"),
        # 常量 / 数字
        r("constant.language", foreground=nu),
        r(["constant.numeric", "variable.other.enummember",
           "keyword.operator.plus.exponent", "keyword.operator.minus.exponent"], foreground=nu),
        r("constant.regexp", foreground=pl),
        r(["constant.character", "constant.other.option"], foreground=kw),
        r("constant.character.escape", foreground=nu),
        r("support.constant", foreground=nu),
        # 标签 / 属性
        r("entity.name.tag", foreground=kw),
        r(["entity.name.tag.css", "entity.name.tag.less"], foreground=pl),
        r("entity.other.attribute-name", foreground=ty),
        r(["entity.other.attribute-name.class.css", "source.css entity.other.attribute-name.class",
           "entity.other.attribute-name.id.css", "entity.other.attribute-name.parent-selector.css",
           "entity.other.attribute-name.parent.less",
           "source.css entity.other.attribute-name.pseudo-class",
           "entity.other.attribute-name.pseudo-element.css",
           "source.css.less entity.other.attribute-name.id",
           "entity.other.attribute-name.scss"], foreground=pl),
        r("entity.name.label", foreground=ink2),
        r("entity.name.section", foreground=kw),
        r("punctuation.definition.tag", foreground=cm),
        # markdown
        r("markup.underline", fontStyle="underline"),
        r("markup.bold", foreground=kw, fontStyle="bold"),
        r("markup.heading", foreground=kw, fontStyle="bold"),
        r("markup.italic", foreground=pl, fontStyle="italic"),
        r("markup.strikethrough", fontStyle="strikethrough"),
        r("markup.inserted", foreground=P["prim"] if "prim" in P else kw),
        r("markup.deleted", foreground=err),
        r("markup.changed", foreground=ty),
        r("markup.inline.raw", foreground=st),
        r("punctuation.definition.quote.begin.markdown", foreground=cm),
        r("punctuation.definition.list.begin.markdown", foreground=P["prim"]),
        # 预处理 / diff
        r(["meta.preprocessor", "entity.name.function.preprocessor"], foreground=pl),
        r("meta.preprocessor.string", foreground=st),
        r("meta.preprocessor.numeric", foreground=nu),
        r("meta.structure.dictionary.key.python", foreground=ty),
        r("meta.diff.header", foreground=kw),
        r("meta.template.expression", foreground=ink),
        # 存储类
        r("storage", foreground=kw),
        r("storage.type", foreground=kw),
        r(["storage.modifier", "keyword.operator.noexcept"], foreground=kw),
        r(["storage.modifier.import.java", "variable.language.wildcard.java",
           "storage.modifier.package.java"], foreground=ink),
        # 字符串
        r(["string", "meta.embedded.assembly"], foreground=st),
        r("string.tag", foreground=st),
        r("string.value", foreground=st),
        r("string.regexp", foreground=pl),
        r(["punctuation.definition.template-expression.begin",
           "punctuation.definition.template-expression.end",
           "punctuation.section.embedded",
           "punctuation.section.embedded.begin.php",
           "punctuation.section.embedded.end.php"], foreground=kw),
        # 属性名 / 变量
        r(["support.type.vendored.property-name", "support.type.property-name",
           "source.css variable", "source.coffee.embedded"], foreground=ty),
        # 关键字
        r("keyword", foreground=kw),
        r("keyword.control", foreground=kw),
        r("keyword.operator", foreground=ink),
        r(["keyword.operator.new", "keyword.operator.expression", "keyword.operator.cast",
           "keyword.operator.sizeof", "keyword.operator.alignof", "keyword.operator.typeid",
           "keyword.operator.alignas", "keyword.operator.instanceof",
           "keyword.operator.logical.python", "keyword.operator.wordlike"], foreground=kw),
        r("keyword.other.unit", foreground=nu),
        r("variable.language", foreground=kw),
        r(["variable", "meta.definition.variable.name", "support.variable",
           "entity.name.variable", "constant.other.placeholder"], foreground=ink),
        r("variable.parameter", foreground=P["pale"]),
        r(["variable.other.constant", "variable.other.enummember"], foreground=nu),
        r("meta.object-literal.key", foreground=ty),
        # 函数
        r(["entity.name.function", "support.function", "support.constant.handlebars",
           "source.powershell variable.other.member",
           "entity.name.operator.custom-literal"], foreground=fn),
        r(["support.function.be.latex", "support.function.section.latex"], foreground=kw),
        r("support.function.git-rebase", foreground=ty),
        r("constant.sha.git-rebase", foreground=nu),
        # 类型
        r(["support.class", "support.type", "entity.name.type", "entity.name.namespace",
           "entity.other.attribute", "entity.name.scope-resolution", "entity.name.class",
           "storage.type.numeric.go", "storage.type.byte.go", "storage.type.boolean.go",
           "storage.type.string.go", "storage.type.uintptr.go", "storage.type.error.go",
           "storage.type.rune.go", "storage.type.cs", "storage.type.generic.cs",
           "storage.type.modifier.cs", "storage.type.variable.cs",
           "storage.type.annotation.java", "storage.type.generic.java", "storage.type.java",
           "storage.type.object.array.java", "storage.type.primitive.array.java",
           "storage.type.primitive.java", "storage.type.token.java",
           "storage.type.groovy", "storage.type.annotation.groovy",
           "storage.type.parameters.groovy", "storage.type.generic.groovy",
           "storage.type.object.array.groovy", "storage.type.primitive.array.groovy",
           "storage.type.primitive.groovy"], foreground=ty),
        r(["meta.type.cast.expr", "meta.type.new.expr", "support.constant.math",
           "support.constant.dom", "support.constant.json", "entity.other.inherited-class",
           "punctuation.separator.namespace.ruby"], foreground=ty),
        # CSS 值 / 正则细节
        r(["support.constant.property-value", "support.constant.font-name",
           "support.constant.media-type", "support.constant.media",
           "constant.other.color.rgb-value", "constant.other.rgb-value",
           "support.constant.color"], foreground=st),
        r(["punctuation.definition.group.regexp", "punctuation.definition.group.assertion.regexp",
           "punctuation.definition.character-class.regexp",
           "punctuation.character.set.begin.regexp",
           "punctuation.character.set.end.regexp", "keyword.operator.negation.regexp",
           "support.other.parenthesis.regexp"], foreground=st),
        r(["constant.character.character-class.regexp", "constant.other.character-class.set.regexp",
           "constant.other.character-class.regexp", "constant.character.set.regexp"],
          foreground=pl),
        r(["keyword.operator.or.regexp", "keyword.control.anchor.regexp"], foreground=fn),
        r("keyword.operator.quantifier.regexp", foreground=nu),
    ]


def semantic(P):
    """语义高亮：Pylance / clangd / TS 都走这套（主题里定义了就默认启用）"""
    return {
        "namespace": P["ty"], "class": P["ty"], "enum": P["ty"],
        "interface": P["ty"], "struct": P["ty"], "type": P["ty"],
        "typeParameter": {"foreground": P["ty"], "italic": True},
        "enumMember": P["nu"],
        "function": P["fn"], "method": P["fn"],
        "event": P["fn"], "label": P["kw"],
        "decorator": P["pl"], "macro": P["pl"],
        "variable": P["ink"], "parameter": P["pale"], "property": P["tyL"],
        "selfParameter": P["kw"], "clsParameter": P["kw"],
        "magicFunction": {"foreground": P["fn"], "italic": True},
        "keyword": P["kw"], "modifier": P["kw"], "operator": P["ink"],
        "comment": P["cm"], "string": P["st"], "number": P["nu"], "regexp": P["pl"],
        "*.deprecated": {"foreground": P["cm"], "strikethrough": True},
    }


# ============================================================
# 键名校验：本机这个 VS Code 版本到底认哪些键
# ============================================================
def app_root():
    for base in (os.path.join(VSCODE, "resources", "app"),
                 os.path.join(VSCODE, "a44adf7f53", "resources", "app")):
        if os.path.isdir(base):
            return base
    # 兜底：扫哈希目录
    for d in glob.glob(os.path.join(VSCODE, "*", "resources", "app")):
        if os.path.isdir(d):
            return d
    raise SystemExit("找不到 VS Code 的 resources/app，请检查安装路径")


def known_keys(root):
    keys = set()
    # A. 自带主题用到的键
    for f in glob.glob(os.path.join(root, "extensions", "theme-defaults", "themes", "*.json")):
        keys.update((json.load(io.open(f, encoding="utf-8")).get("colors") or {}).keys())
    # B. 内置扩展 contributes.colors
    for root2, _d, files in os.walk(os.path.join(root, "extensions")):
        for f in files:
            if f != "package.json":
                continue
            try:
                d = json.load(io.open(os.path.join(root2, f), encoding="utf-8"))
            except Exception:
                continue
            for c in (d.get("contributes") or {}).get("colors") or []:
                if isinstance(c, dict) and "id" in c:
                    keys.add(c["id"])
    # C. bundle 里的字面量（>2MB 的 js）
    blobs = []
    for root2, _d, files in os.walk(os.path.join(root, "out")):
        for f in files:
            if not f.endswith(".js"):
                continue
            p = os.path.join(root2, f)
            if os.path.getsize(p) > 2 * 1024 * 1024:
                blobs.append(io.open(p, encoding="utf-8", errors="replace").read())
    return keys, blobs


HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def main():
    root = app_root()
    keys, blobs = known_keys(root)
    print("本机 VS Code: %s  ->  已知颜色键 %d 个" % (root, len(keys)))

    unknown, badhex = [], []
    for k, (d, l) in sorted(COLORS.items()):
        for v in (d, l):
            if not HEX.match(v):
                badhex.append((k, v))
        if k not in keys and not any('"%s"' % k in b for b in blobs):
            unknown.append(k)
    if badhex:
        print("!! 非法色值：")
        for k, v in badhex:
            print("   %s = %s" % (k, v))
    if unknown:
        print("!! 本机不认识这些键（%d）—— 删掉或改名：" % len(unknown))
        for k in unknown:
            print("   ", k)
    if badhex or unknown:
        sys.exit(1)

    os.makedirs(OUT, exist_ok=True)
    names = {}
    for mode, idx, ui, name in (("dark", 0, "vs-dark", "青瓷（深）"),
                                ("light", 1, "vs", "青瓷（浅）")):
        P = D if mode == "dark" else L
        theme = {
            "$schema": "vscode://schemas/color-theme",
            "name": name,
            "type": mode,
            "semanticHighlighting": True,
            "colors": {k: v[idx] for k, v in COLORS.items()},
            "tokenColors": tokens(P),
            "semanticTokenColors": semantic(P),
        }
        path = os.path.join(OUT, "qingci-%s.json" % mode)
        io.open(path, "w", encoding="utf-8", newline="\n").write(
            json.dumps(theme, ensure_ascii=False, indent=2) + "\n")
        names[mode] = path
        n_rule = len(theme["tokenColors"])
        print("%-6s -> %s  (%d 个工作台键, %d 条语法规则, %d 条语义规则)"
              % (mode, os.path.basename(path), len(theme["colors"]), n_rule,
                 len(theme["semanticTokenColors"])))

    # 深浅两套键集合必须一致
    a = json.load(io.open(names["dark"], encoding="utf-8"))
    b = json.load(io.open(names["light"], encoding="utf-8"))
    assert set(a["colors"]) == set(b["colors"]), "深浅两套键不一致"
    assert len(a["colors"]) == len(COLORS), "有键没写进去"
    print("\nOK：%d 个键，深浅一致，键名与色值全部通过。" % len(COLORS))


if __name__ == "__main__":
    main()
