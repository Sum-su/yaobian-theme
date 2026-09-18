# 发布手册（商城 / Open VSX）

代码和包都准备好了，剩下的是**两个账号**——这一步必须你本人登录（微软账号和 GitHub 账号，
我代替不了）。全程大约五分钟，之后每次发版只要 `python publish.py`。

当前状态：`package.json` 里 `publisher` 是 **`tombliboo`**，扩展 id 就是
`tombliboo.yaobian-theme`；商城上这个名字还没人注册（查过，404）。发布者 id 必须与
`package.json` 一致，否则 `vsce publish` 会报 `Invalid publisher`。

---

## 一、VS Code 商城

### 1. 建发布者

1. 打开 <https://marketplace.visualstudio.com/manage>
2. 用**微软账号**登录（没有就当场注册一个，免费）
3. 第一次会让你 Create publisher：
   - **ID 填 `tombliboo`**（要一字不差，全小写）
   - Name / 显示名随便填（比如 `Yaobian`）
4. 建完页面会跳回 Manage 列表

### 2. 建 PAT（个人访问令牌）

1. 打开 <https://dev.azure.com> → 右上角**用户设置**（小人图标）→ **Personal access tokens**
   （直达：<https://dev.azure.com/_usersSettings/tokens>）
2. **New Token**：
   - Name：`vsce`（随便）
   - **Organization：选 `All accessible organizations`** ← 这一项选错是最常见的 401 原因
   - Expiration：按需（最长一年；到期要重新建）
   - Scopes：先点 **Custom defined** → 展开 **Marketplace** → 勾 **Manage**
3. Create → **立刻复制** token（只显示这一次，离开页面就看不到了）

### 3. 存 token 并发布

```bash
# token 存一行，别加引号
notepad C:\temp\vsce-pat.txt

cd C:\temp\yaobian-vscode
python publish.py --check          # 先看准备齐了没
python publish.py --marketplace     # 发
```

`publish.py` 把 token 放进子进程的环境变量（`VSCE_PAT`）而不是命令行——`--pat` 会出现在进程
列表和日志里，这样不会。它也不回显 token。

发完之后：
- 商城页 <https://marketplace.visualstudio.com/items?itemName=tombliboo.yaobian-theme>
  （索引要几分钟）
- 别人就能 `code --install-extension tombliboo.yaobian-theme` 了

---

## 二、Open VSX（VSCodium / Cursor / Windsurf）

1. 打开 <https://open-vsx.org> → 右上角 **Sign In** → 用 **GitHub** 登录
2. 头像 → **Settings** → **Access Tokens** → **Generate New Token** → 复制
3. 命名空间：同一个 Settings 页里 **Namespaces** → Create，填 `tombliboo`
   （首次发布时如果没建，`ovsx` 会提示你去建；Open VSX 还要求签一次 **Publisher Agreement**，
   页面上点一下就行）
4. 存 token 并发布：

```bash
notepad C:\temp\ovsx-pat.txt
cd C:\temp\yaobian-vscode
python publish.py --openvsx
```

两边都发就 `python publish.py`（不带参数）。

---

## 三、以后每次发版

```bash
# 1. 改版本号（gen.py 里那个 0.3.0，顺便改 CHANGELOG.md）
python gen.py                      # 重新生成 72 套 + package.json
python test_mode.py                # 自检（商城不管这个，自己把关）
python falsify_checks.py           # 确认检查还是能红的
npx @vscode/vsce package -o dist/yaobian-theme-<版本>.vsix
python publish.py                  # 两个市场一起发
gh release create v<版本> dist/yaobian-theme-<版本>.vsix
```

注意 `python pack.py` 是**不装 node 时的退路**（手搓 zip），产物同名、也能装，
但商城走的必须是 `vsce package` 那个（多带 icon/license/changelog 这些资源条目）。

## 四、token 的规矩

- 只放 `C:\temp\vsce-pat.txt` / `C:\temp\ovsx-pat.txt`（或 `%USERPROFILE%\.vsce-pat`），
  这几个名字都在 `.gitignore` 里，不会被提交——**发布前顺手 `git status` 看一眼**。
- PAT 泄露就等于别人能替你发版：真要泄露了，去 Azure DevOps 把那个 token 撤销即可。
- 我（Claude）不会把 token 读进对话；`publish.py --check` 只报「有没有、几位」。
