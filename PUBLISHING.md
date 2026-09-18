# 发布手册（商城 / Open VSX）

代码和包都准备好了，剩下的是**两个账号**——这一步必须你本人登录（微软账号和 GitHub 账号，
我代替不了）。全程大约五分钟，之后每次发版只要 `python publish.py`。

当前状态：发布者 **`tombliboo0226` 已经建好了**（<https://marketplace.visualstudio.com/publishers/tombliboo0226>
可访问），`package.json` 里的 `publisher` 也是它，扩展 id 就是 `tombliboo0226.yaobian-theme`。
**下一步只差第 2 节的 PAT**，拿到就 `python publish.py`。
发布者 id 必须与 `package.json` 完全一致，否则 `vsce publish` 会报 `Invalid publisher`。

---

## 一、VS Code 商城

> **建发布者和建 PAT 必须用同一个微软账号。** 两个页面各登录一次，很容易顺手用了不同的号；
> 不一致的表现是发布时 `Invalid publisher` 或者 401，而且不容易往这上面想。

### 1. 建发布者 ✅ 已经建好了（`tombliboo0226`），本节留作记录／备用

1. 打开 <https://marketplace.visualstudio.com/manage/createpublisher?managePageRedirect=true>
   （或 <https://marketplace.visualstudio.com/manage> 登录后在左栏点 Create publisher）
2. 用**微软账号**登录（没有就当场注册一个，免费）
3. 填两个字段：
   - **Name**：显示名，随便填（比如 `Yaobian`）
   - **ID**：⚠️ **它会跟着 Name 自动填，一定要手动改成 `tombliboo0226`**（一字不差，全小写）。
     ID 决定扩展的完整名字，**创建后不能改**；它必须和 `package.json` 里的 `publisher`
     完全相同，否则 `vsce publish` 直接报 `Invalid publisher`。
     （不是假设：这个 ID 真的被自动填成过 `tomnliboo26`——`b` 变成 `n`，一眼扫过去看不出来。
     逐字核对，别只看长度。）
4. 勾选同意 **Marketplace Publisher Agreement** → **Create**

### 2. 建 PAT（个人访问令牌）

1. 打开 <https://dev.azure.com> → 右上角**用户设置**（小人图标）→ **Personal access tokens**
   （直达：<https://dev.azure.com/_usersSettings/tokens>）
   - 如果提示你还没有组织，先 **Create an organization**（名字随便，免费）——第一次用
     Azure DevOps 的个人账号基本都会撞上这一步，它跟发布者 ID 没有任何关系，随便起。
2. **New Token**：
   - Name：`vsce`（随便）
   - **Organization：选 `All accessible organizations`** ← 这一项选错是最常见的 401 原因
   - Expiration：按需（最长一年；到期要重新建）
   - Scopes：先点 **Custom defined** → 点 **Show all scopes** → 滚到 **Marketplace** → 勾 **Manage**
3. Create → **立刻复制** token（只显示这一次，离开页面就看不到了）

> ⚠️ **这个令牌有硬期限**：官方文档写着「On December 1, 2026, global Personal Access Tokens
> (PATs) in Azure DevOps are retired」（<https://code.visualstudio.com/api/working-with-extensions/publishing-extension>）。
> 我们要的正是全局 PAT（Organization 选 All accessible 就是），所以它 **2026-12-01 起会失效**。
> 官方给的替代方案（Entra ID + managed identity + service connection）是给 CI 流水线设计的，
> 个人微软账号怎么发还没写清楚。先发出去没问题，到 11 月底我们再看当时的新说法。

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
（vsce 确实认这个变量：`--pat` 的帮助原文是 `defaults to VSCE_PAT environment variable`，
所以不会卡在等你手动输入 token 上。）

发完之后：

- 商城页 <https://marketplace.visualstudio.com/items?itemName=tombliboo0226.yaobian-theme>
  （索引要几分钟）
- 别人就能 `code --install-extension tombliboo0226.yaobian-theme` 了

---

## 二、Open VSX（VSCodium / Cursor / Windsurf）

1. 打开 <https://open-vsx.org> → 右上角 **Sign In** → 用 **GitHub** 登录
2. 头像 → **Settings** → **Access Tokens** → **Generate New Token** → 复制
3. 命名空间：同一个 Settings 页里 **Namespaces** → Create，填 `tombliboo0226`
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
python check_package.py            # ← 守门：包里的东西必须和清单声明的严格对上
python publish.py                  # 两个市场一起发
gh release create v<版本> dist/yaobian-theme-<版本>.vsix
```

`check_package.py` 是补上的窟窿：**vsce 照目录打包，从不看 `contributes.themes`**，所以
「清单声明 72 套、`themes/` 里躺着 74 个 json」这种事它一声不吭就发出去了。这个脚本两边对集合，
多一个少一个都报，另外还查占位符展开、vsixmanifest 里的 Description、LICENSE 是不是裸 MIT。
改动主题目录之后务必跑一次——它红了就是真有问题，别绕过去。

注意 `python pack.py` 是**不装 node 时的退路**（手搓 zip），产物同名、也能装，
但商城走的必须是 `vsce package` 那个（多带 icon/license/changelog 这些资源条目）。

## 四、token 的规矩

- 只放 `C:\temp\vsce-pat.txt` / `C:\temp\ovsx-pat.txt`（或 `%USERPROFILE%\.vsce-pat`），
  这几个名字都在 `.gitignore` 里，不会被提交——**发布前顺手 `git status` 看一眼**。
- PAT 泄露就等于别人能替你发版：真要泄露了，去 Azure DevOps 把那个 token 撤销即可。
- 我（Claude）不会把 token 读进对话；`publish.py --check` 只报「有没有、几位」。
