# 飞书文档写入工具

将本地 Markdown 文件一键发布到飞书文档。

## 功能特性

- 支持写入到我的空间、指定文件夹、知识库
- 自动上传本地图片
- 保留代码块语法高亮
- 支持单个文件或批量处理
- 重复文档检测与处理
- 支持配置默认知识库，简化命令

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置凭证

复制 `.env.example` 为 `.env`，填入飞书应用凭证：

```
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 可选：配置默认知识库（配置后可直接使用 --target wiki）
FEISHU_DEFAULT_WIKI_SPACE_ID=你的知识库space_id
FEISHU_DEFAULT_WIKI_NODE_TOKEN=你的知识库node_token
```

### 3. 获取飞书凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 在「权限管理」中开通以下权限：
   - `docs:doc` - 云空间文件管理
   - `drive:drive` - 云空间文件访问
   - `wiki:wiki` - 知识库管理（如需写入知识库）

### 4. 将应用添加为云文档/知识库协作者

**重要**：应用需要被添加为目标文档/知识库的协作者才能写入内容。

云文档的所有者或有「可管理」权限的协作者，可按以下步骤添加应用：

1. 打开云文档或知识库
2. 点击右上角 **「···」** 图标
3. 选择 **「更多」** > **「添加文档应用」**
4. 搜索并选择目标应用
5. 为应用分配 **「可编辑」** 或 **「可管理」** 权限
6. 点击 **「添加」**

添加成功后，应用将出现在当前文档的协作者列表中。

### 5. 使用

```bash
# 写入到我的空间
python -m scripts.feishu_writer ./doc.md

# 写入到指定文件夹
python -m scripts.feishu_writer ./doc.md --target folder --folder-token fldcnxxxxxx

# 写入到知识库（使用 .env 中配置的默认知识库）
python -m scripts.feishu_writer ./doc.md --target wiki

# 写入到指定知识库
python -m scripts.feishu_writer ./doc.md --target wiki --wiki-token FWn9wEcZhixVLrk2z5scBx8DnTe

# 批量处理目录
python -m scripts.feishu_writer ./docs/ --target folder --folder-token fldcnxxxxxx
```

## 命令参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `path` | - | MD 文件或目录路径 | 必填 |
| `--target` | `-t` | 目标位置 (space/folder/wiki) | space |
| `--folder-token` | `-f` | 文件夹 token | - |
| `--wiki-token` | `-w` | 知识库 node_token（可在 .env 中配置默认值） | - |
| `--on-duplicate` | - | 重复处理 (ask/update/skip/new) | ask |
| `--no-check-duplicate` | - | 不检查重复 | false |

## 如何获取 Token

### 文件夹 Token

1. 在飞书云文档中打开目标文件夹
2. 查看浏览器地址栏：`https://xxx.feishu.cn/drive/folder/fldcnXXXXXX`
3. `fldcnXXXXXX` 即为 folder-token

### 知识库 Node Token

1. 打开目标知识库页面
2. 查看地址栏：`https://xxx.feishu.cn/wiki/FWn9wEcZhixVLrk2z5scBx8DnTe`
3. `/wiki/` 后面的字符串 `FWn9wEcZhixVLrk2z5scBx8DnTe` 即为 node_token

### 知识库 Space ID

Space ID 是知识库的内部标识（数字），可通过以下方式获取：
- 程序会自动通过 node_token 查询 space_id
- 也可手动配置在 `.env` 的 `FEISHU_DEFAULT_WIKI_SPACE_ID` 中

## 支持的 Markdown 格式

| 格式 | 示例 | 支持 |
|------|------|------|
| 标题 | `# H1` ~ `###### H6` | ✓ |
| 加粗 | `**text**` | ✓ |
| 斜体 | `*text*` | ✓ |
| 行内代码 | `` `code` `` | ✓ |
| 代码块 | ` ```python ` | ✓ |
| 无序列表 | `- item` | ✓ |
| 有序列表 | `1. item` | ✓ |
| 引用 | `> quote` | ✓ |
| 链接 | `[text](url)` | ✓ |
| 图片 | `![alt](path)` | ✓ |
| 分割线 | `---` | ✓ |

## 作为 Claude Code 技能使用

在 Claude Code 中直接使用：

```
/feishu-write ./doc.md --target folder --folder-token fldcnxxxxxx
```

## 常见问题

### Q: 提示「获取 token 失败」

检查 `.env` 中的 App ID 和 App Secret 是否正确。

### Q: 提示「权限不足」或「permission denied」

1. 确认应用权限已在飞书开放平台开通并发布
2. **确认应用已被添加为目标文档/知识库的协作者**（见上方「将应用添加为协作者」步骤）
3. 确认应用的协作者权限为「可编辑」或「可管理」

### Q: 提示「node permission denied, tenant needs edit permission」

应用没有目标知识库的编辑权限。请按照上方步骤将应用添加为知识库的协作者，并授予「可编辑」权限。

### Q: 图片上传失败

- 确保图片路径正确
- 检查图片格式是否支持（jpg/png/gif）
- 确认应用有云空间写入权限

### Q: 网络图片无法显示

当前版本暂不支持直接使用网络图片，请先下载到本地。

### Q: block_type 相关错误

飞书 API 要求 block_type 为数字类型。本工具已正确处理，如遇到此问题请更新到最新版本。

## 许可证

MIT License
