# 修改简历

上传一份基础简历和招聘 JD，一次获得岗位专版 PDF、一条可直接复制的 HR 打招呼文案，以及包含全部简历页面的单张长图。

技能会读取 JD，从招聘职责与产品经营角度组织两个具体项目，写清技术栈、实现内容和核心技术作用，再同步改写项目、工作、实习和技能部分，并完成排版检查。

| 项目 | 内容 |
| --- | --- |
| 显示名称 | 修改简历 |
| 调用命令 | `$jd-project-examples` |
| 必需输入 | 基础简历 + 招聘 JD |
| 默认交付 | 岗位专版 PDF + HR 打招呼文案 + 单张 JPEG 简历长图 |
| 仓库地址 | [dashuaige-cn/jd-project-examples](https://github.com/dashuaige-cn/jd-project-examples) |

中文名称用于界面展示，英文标识用于命令和安装目录。两者对应同一个技能。

## 使用说明

### 上传文件后调用

安装后，在 Codex 中上传基础简历和招聘 JD。JD 可以是截图、文字或文件，基础简历可以是 PDF、Word、图片或文字。

然后发送：

```text
$jd-project-examples

根据附件中的基础简历和招聘 JD 修改简历。
替换全部旧项目，同步修改工作经历、实习经历和技能。
交付 PDF、可直接复制的 HR 打招呼文案和完整简历长图。
```

不需要先准备两个项目的 Markdown 文档。已有明确的项目资料时，也可以一并提供，技能会优先使用你指定的项目。

### 使用本地文件路径

文件已在当前电脑上时，可以直接提供路径，例如：

```text
$jd-project-examples

基础简历：E:\resume\我的简历.pdf
招聘 JD：E:\resume\岗位要求.png
请按这个岗位改写简历，保存到 E:\resume\output。
```

上面的路径是示例，使用时替换为实际存在的文件路径。

### 可追加的要求

- 项目与公司的对应关系，例如“项目一对应正式工作，项目二对应实习”。
- 版式、页数或保存位置，例如“控制在两页，保留证件照”。
- 指定已有项目、职责或实测数据，优先用这些材料改写。
- 如需 Word 文件，明确提出；默认的招呼文案和长图会同时提供。

### 默认会修改哪些内容

- **项目经历**：删除旧项目，仅保留本次两个项目，并展开技术实现与交付。
- **工作与实习经历**：删除旧项目职责，同步重写；实习职责采用参与、联调、验证等与角色相称的表述。
- **求职意向与技能**：按目标 JD 调整，让全文的技术栈与职责一致。
- **个人资料**：保留基础简历中的姓名、联系方式、教育背景、公司、任职时间、职位与照片。
- **排版与输出**：默认生成 A4、通常 1 至 2 页的岗位专版 PDF，保留原始简历，同时提供招呼文案与长图。

### 每次交付的三项内容

1. **PDF 简历**：用于附件投递和正式保存。
2. **HR 打招呼文案**：根据本次岗位和最终简历编写，默认约 60 至 120 字，放在独立文字代码块中，直接复制即可发送。
3. **完整简历长图**：从最终 PDF 按页码顺序导出并纵向拼接成一张 JPEG，默认宽度 1600 像素，适合在聊天里作为图片发送。两页简历会包含完整的两页。

无需每次重复要求这三项。只想补齐其中一项时，可以发送“把这份简历导出成长图”或“根据这份简历写一句 HR 打招呼语”；不会因此重写整份简历。

技能随附长图导出脚本，需要 Python、Pillow、pypdf 和 Poppler 的 `pdftoppm`。已完成 PDF 后，也可以手动导出：

```sh
python scripts/export_resume_image.py --pdf "最终简历.pdf" --output "岗位主题_姓名_长图.jpg"
```

在技能目录中执行以上命令，或将脚本改成完整路径；输入和输出路径换成实际路径。默认保护同名输出文件，明确更新时加 `--force`。导出只读取 PDF，图片与原 PDF 保持相同内容。

本技能沿用创建者约定，按用户已确认的落地项目口径处理，不再重复询问项目是否落地。没有提供的同步精度、性能提升、量产规模、客户和收入等数据不会自动补写；后续明确提供的项目状态与事实优先。

## 安装教程

如果这台电脑已经安装了本技能，直接调用即可，无需再次安装。当前版本将显示名称改为“修改简历”，英文调用命令保持不变。

### 方法一：让 Codex 安装

在要使用该技能的 Codex 环境中发送：

```text
$skill-installer

请从 https://github.com/dashuaige-cn/jd-project-examples 安装“修改简历”技能。
技能位于仓库根目录，分支为 main。
使用完整下载模式安装，参数为 --path . --name jd-project-examples --method download。
私有仓库可复用本机已授权的 GitHub CLI 凭据，仅向安装子进程临时传递凭据，不打印或保存令牌。
如果下载模式无法认证，请改用下方方法二的完整 Git 克隆，不要对仓库根目录进行稀疏克隆。
如果已经安装，请先检查现有版本，不要直接覆盖我的本地改动。
```

这里必须说明“仓库根目录”和安装目录名，因为 `SKILL.md` 直接位于仓库根目录，而非某个子文件夹。完整下载会同时保留 `agents/openai.yaml` 和 `scripts/`；根目录稀疏克隆可能漏掉界面配置和长图导出脚本。

安装后在下一条消息中调用 `$jd-project-examples`；如果技能仍未出现，重启 Codex 后再试。此方式使用的具体安装目录以安装器回执为准。

### 私有仓库的访问准备

本仓库当前为私有仓库。安装时需要使用有访问权限的 GitHub 账号；只有网页登录，不代表本地 Git 或安装器也已获得权限。

如采用 GitHub CLI 授权，先安装 [GitHub CLI](https://cli.github.com/)，再在终端执行：

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
```

按命令提示在浏览器完成授权，不需要把密码或令牌发送给 Codex。已有可用的 Git 凭据或 SSH 授权时，可以沿用现有方式。

### 方法二：通过 Git 手动安装

根据 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)，新环境可使用用户级目录 `~/.agents/skills/`。如果你已有一份由安装器管理的本技能，请更新原位置，不要再安装第二份。

Windows PowerShell：

```powershell
$skillRoot = Join-Path $HOME '.agents\skills'
New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
git clone https://github.com/dashuaige-cn/jd-project-examples.git (Join-Path $skillRoot 'jd-project-examples')
```

macOS / Linux：

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/dashuaige-cn/jd-project-examples.git ~/.agents/skills/jd-project-examples
```

若提示目标目录已存在，不要删除原目录；先检查它是否为已安装版本，以及是否有自己的改动。

安装后的主要文件应为：

```text
jd-project-examples/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── export_resume_image.py
└── README.md
```

新技能通常会被自动发现；未出现时重启 Codex，再发送使用示例中的命令。

### 方法三：下载 ZIP 手动安装

在有访问权限的账号中打开仓库，选择 **Code → Download ZIP**，解压后将含有 `SKILL.md` 和 `agents` 的文件夹命名为 `jd-project-examples`，放到用户级技能目录 `~/.agents/skills/` 下。

不要多嵌套一层 `jd-project-examples-main`，也不要只复制 `SKILL.md` 而漏掉界面配置和 `scripts` 目录。已安装时请先检查并备份自己的改动，避免重复安装。

## 更新与常见问题

通过 Git 手动安装且没有本地改动时，可以在该技能目录中执行：

```sh
git pull --ff-only
```

通过安装器或 ZIP 安装的版本，可以把本仓库链接发给 Codex，要求检查并更新现有安装。先保留自己的改动，不要盲目覆盖。

| 问题 | 处理方式 |
| --- | --- |
| 界面里找不到“修改简历” | 检查安装回执和文件位置；若未刷新，重启 Codex。 |
| 输入中文名称没有显式调用 | 使用命令 `$jd-project-examples`。 |
| 下载出现 404 或权限错误 | 确认账号拥有私有仓库权限，并完成本地 Git/安装器授权。 |
| 提示同名目录已存在 | 先检查已装版本，不要直接删除目录或重复安装。 |
| 只得到文字，没有 PDF | 说明需要实际 PDF 文件；当前环境还需具备 PDF 生成与渲染能力。 |
| 长图没有生成 | 检查 Pillow、pypdf、Poppler 是否可用；以最终 PDF 重新运行导出脚本。 |

技能本身是工作流指令，不包含完整的 PDF/Word 转换引擎。文件生成会复用当前 Codex 环境的 PDF 或文档技能及相应工具。

## 参考

- [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)
- [GitHub CLI 浏览器授权说明](https://cli.github.com/manual/gh_auth_login)
- [GitHub CLI 配置 Git 凭据](https://cli.github.com/manual/gh_auth_setup-git)
