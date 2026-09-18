# -*- coding: utf-8 -*-
"""
把主题打成 .vsix（不依赖 vsce：vsix 就是个 zip + 两份清单）
产物：dist/<名字>-<版本>.vsix（版本号从 package.json 读）
安装：code --install-extension dist/<名字>-<版本>.vsix --force
"""
import io
import json
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
PKG = os.path.join(HERE, "package.json")

CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".md" ContentType="text/markdown"/>
</Types>
"""

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011"
                 xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{name}" Version="{version}" Publisher="{publisher}" />
    <DisplayName>{display}</DisplayName>
    <Description xml:space="preserve">{desc}</Description>
    <Tags>{tags}</Tags>
    <Categories>{categories}</Categories>
    <GalleryFlags>Public</GalleryFlags>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{engine}" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="ui" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionPack" Value="" />
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Icons.Default" Path="extension/icon.png" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.License" Path="extension/LICENSE" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.Changelog" Path="extension/CHANGELOG.md" Addressable="true" />
  </Assets>
</PackageManifest>
"""


def nls(text):
    """把 package.json 里的 %key%（displayName/description 那些）按 package.nls.json 展开。

    商城发布走的是 vsce，它自己会展开；这里手搓的 vsix 也得展开，否则清单里会印着一串
    「%description%」——本地装上去看着就像坏了。
    """
    p = os.path.join(HERE, "package.nls.json")
    if not os.path.isfile(p) or "%" not in text:
        return text
    table = json.load(io.open(p, encoding="utf-8"))
    for k, v in table.items():
        text = text.replace("%" + k + "%", v)
    if "%" in text:
        raise SystemExit("package.json 里有没展开的 %%键%%：%s" % text)
    return text


def main():
    pkg = json.load(io.open(PKG, encoding="utf-8"))
    files = ["package.json", "package.nls.json", "package.nls.zh-cn.json",
             "README.md", "LICENSE", "NOTICE.md", "CHANGELOG.md", "icon.png"]
    for t in pkg["contributes"]["themes"]:
        files.append(t["path"].lstrip("./").replace("/", os.sep))
    for f in files:
        p = os.path.join(HERE, f)
        if not os.path.isfile(p):
            raise SystemExit("缺文件：%s" % p)

    manifest = MANIFEST.format(
        name=pkg["name"], version=pkg["version"], publisher=pkg["publisher"],
        display=nls(pkg["displayName"]), desc=nls(pkg["description"]),
        tags=",".join(pkg.get("keywords", [])),
        categories=",".join(pkg.get("categories", [])),
        engine=pkg["engines"]["vscode"],
    )

    os.makedirs(DIST, exist_ok=True)
    vsix = os.path.join(DIST, "%s-%s.vsix" % (pkg["name"], pkg["version"]))
    with zipfile.ZipFile(vsix, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("extension.vsixmanifest", manifest)
        for f in files:
            z.write(os.path.join(HERE, f), "extension/" + f.replace(os.sep, "/"))
    print("%s  (%d KB)" % (vsix, os.path.getsize(vsix) // 1024))


if __name__ == "__main__":
    main()
