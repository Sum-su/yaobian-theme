# 发布手册（商城 / Open VSX）

代码和包都准备好了，剩下的是**账号**——这一步必须你本人登录（微软账号和 GitHub 账号，
我代替不了）。

当前状态：发布者 **`tombliboo0226`** 已建好，扩展 **`tombliboo0226.yaobian-theme@0.3.0`
已于 2026-09-18 上架**。发布者 id 必须与 `package.json` 完全一致，否则会报 `Invalid publisher`。

---

## 一、VS Code 商城

### 0. 发版：两条路，先看这条

| | 手动拖 vsix | `vsce publish` |
|---|---|---|
| 需要 PAT | **不需要**（走浏览器登录会话） | 需要 |
| 怎么发 | 发布者管理页 → **Upload extension** → 拖 vsix | `python publish.py --marketplace` |
| 版本号重复 | 会拒绝（改版本号后重打包即可） | 同样拒绝 |
| 脚本化 / CI | ✗ | ✓ |

**v0.3.0 就是这么发出去的：手动拖的，没用 PAT。** 所以别把 PAT 当成发版的前置条件——
它只是「一条命令发版」这个便利功能的前置条件。第一次发、或不常发，用 UI 就够了：

```
npx @vscode/vsce package --out dist/yaobian-theme-<版本>.vsix
python check_package.py                       # 必跑，见第三节
# 然后到 manage/publishers/tombliboo0226 的 Upload extension 页把 vsix 拖进去
```

> ⚠️ **上传成功后前端会滞后几分钟。** 判断「发成功没有」**要查 gallery API，不能看条目页**：
> 上传完 1 分钟时，`items?itemName=...` 网页还是 **404**、`code --install-extension` 报
> `not found`，但 gallery 查询接口**已经能查到**且 `flags = public`
> （精确名 / 按发布者列举 / 全文搜 三种查法都能查到）。拿条目页 404 当失败会让你白折腾。
> 核实方法见本节末尾。

### 1. 建发布者 ✅ 已经建好了（`tombliboo0226`），本节留作记录／备用

> **发布者 ID 不能改。** 一个账号可以建多个发布者，所以填错了就另建一个，不用将就。

1. 打开 <https://marketplace.visualstudio.com/manage/createpublisher?managePageRedirect=true>
   （或 <https://marketplace.visualstudio.com/manage> 登录后在左栏点 Create publisher）
2. 用**微软账号**登录（没有就当场注册一个，免费）
3. 填两个字段：
   - **Name**：显示名，随便填（比如 `Yaobian`）
   - **ID**：⚠️ **它会跟着 Name 自动填，一定要手动改成 `tombliboo0226`**（一字不差，全小写）。
     ID 决定扩展的完整名字；它必须和 `package.json` 里的 `publisher` 完全相同。
     （不是假设：这个 ID 真的被自动填成过 `tomnliboo26`——`b` 变成 `n`，一眼扫过去看不出来。
     逐字核对，别只看长度。）
4. 勾选同意 **Marketplace Publisher Agreement** → **Create**

### 2. 建 PAT（只有想用 `publish.py` 时才需要）

> **建发布者和建 PAT 必须用同一个微软账号。** 两个页面各登录一次，很容易顺手用了不同的号；
> 不一致的表现是发布时 `Invalid publisher` 或者 401，而且不容易往这上面想。

1. 打开 <https://dev.azure.com> → 用**建发布者的同一个微软账号**登录 → 选（或先建）一个组织
   → 右上角**用户设置**（头像旁边那个齿轮／小人图标）→ **Personal access tokens**

   ⚠️ **这里没有「跟组织无关」的直达链接**，别去找。PAT 页面挂在组织下面：
   `https://dev.azure.com/<你的组织>/_usersSettings/tokens` 只有组织存在时才活。
   （踩过：`dev.azure.com/_usersSettings/tokens` 和 `app.vssps.visualstudio.com/_usersSettings/tokens`
   都长得像直达页，实际**都返回 404** `The resource cannot be found.`。官方文档给的第一步也是
   「Sign in to your organization」，不是给链接。）

   - 没有组织就先建（名字随便，免费）——第一次用 Azure DevOps 的个人账号基本都会撞上这一步，
     它跟发布者 ID 没有任何关系。`https://go.microsoft.com/fwlink/?LinkId=307137` 会直接带你进建组织流程。
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
> 替代路径的入口是 `vsce publish --azure-credential`（我核对过 `publish.js`：这个分支走
> `getAzureCredentialAccessToken()`，和 `--pat` / `--oidc` 并列，不是纸上方案）。

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
  （**索引要几分钟**，见下面的核实法）
- 别人就能 `code --install-extension tombliboo0226.yaobian-theme` 了

### 4. 怎么核实「真的发出去了」

**别拿条目页的 404 当失败。** 刚发布时前端会滞后：网页 404、`code --install-extension` 报
`not found`，但后台其实已经收下了。权威判据是 gallery 查询接口（`vsce publish` 打的就是它）：

```bash
python check_live.py        # 仓库里带的小脚本，直接打印商城上的实际状态
```

它打的是 `POST https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery`，
按精确名查，打印版本、`flags`、以及 CDN 上的 Assets。

**`flags` 里有两个标志，各管一件事，缺哪个就知道卡在哪：**

| flags | 含义 | 此时能装吗 |
|---|---|---|
| `public` | 已公开发布（**上传后立刻就有**） | ✗ |
| `validated` | 校验流水线跑完（**要等几分钟到十几分钟**） | ✓ |

刚上传完是 `public` 光杆一个，这时候条目页 404、装不了，**都是正常的**。
等它变成 `public, validated`（对照：`ms-python.python` 就是这个状态）才真正可安装。

上传后立刻能看到的是：

```
完整名   = tombliboo0226.yaobian-theme
版本     = 0.3.0
flags    = public
Assets   = Content.Details（README）/ Icons.Default / Icons.Small / VSIXPackage
```

Assets 四项齐 = README、图标、包都传上去了（这也是为什么商城必须用 `vsce package` 的产物）。

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

# 2. 发（二选一，见第一节 §0 的对照表）
python publish.py                  # 有 PAT：两个市场一起发
#   或  手动：把 dist/ 里那个 vsix 拖到管理页的 Upload extension

# 3. 核实 + 存档
python check_live.py               # 等到 flags 出现 validated 才算真的可装
gh release create v<版本> dist/yaobian-theme-<版本>.vsix
```

**版本号不能重复**——商城和 Open VSX 都会拒绝已存在的版本，所以每次发版第 1 步必须先改版本号。

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
