# Taxon - 下载文件夹整理器

一个功能强大、可扩展的命令行工具，用于自动整理下载文件夹中的文件。

## 功能特性

### 核心功能
- ✅ **自动分类**：根据文件扩展名自动将文件归类到不同子文件夹
- ✅ **自定义规则**：支持基于关键词、正则表达式或扩展名的自定义分类规则
- ✅ **冲突处理**：智能处理文件名冲突（重命名、跳过或覆盖）
- ✅ **定时运行**：支持定时自动整理
- ✅ **干运行模式**：预览整理效果而不实际移动文件

### 支持的分类
默认支持以下文件类型：
- 📷 **图片**：jpg, jpeg, png, gif, bmp, svg, webp
- 📄 **文档**：pdf, doc, docx, txt, rtf, md
- 📦 **压缩包**：zip, rar, 7z, tar, gz
- 🎵 **音频**：mp3, wav, flac, aac
- 🎬 **视频**：mp4, avi, mov, mkv, wmv
- 💻 **代码**：py, js, html, css, java, cpp
- ⚙️ **可执行文件**：exe, msi, dmg, pkg, deb
- 📁 **其他**：未匹配的文件

## 安装

1. 克隆或下载项目
2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

整理指定文件夹：
```bash
python taxon.py organize --path /path/to/downloads
```

使用配置中的默认路径：
```bash
python taxon.py organize
```

### 命令详解

#### 1. 整理文件 (`organize`)

```bash
python taxon.py organize [选项]
```

选项：
- `--path, -p`: 要整理的文件夹路径（默认使用配置中的路径）
- `--dry-run, -d`: 只模拟运行，不实际移动文件
- `--conflict, -c`: 冲突解决策略（rename/skip/overwrite）

示例：
```bash
# 整理默认下载文件夹
python taxon.py organize

# 整理指定文件夹（模拟运行）
python taxon.py organize --path ~/Downloads --dry-run

# 使用跳过策略处理冲突
python taxon.py organize --conflict skip
```

#### 2. 定时运行 (`schedule`)

```bash
python taxon.py schedule [选项]
```

选项：
- `--interval, -i`: 运行间隔（分钟，默认60）
- `--path, -p`: 要整理的文件夹路径
- `--dry-run, -d`: 只模拟运行

示例：
```bash
# 每30分钟自动整理一次
python taxon.py schedule --interval 30

# 每10分钟整理指定文件夹
python taxon.py schedule --interval 10 --path ~/Downloads
```

#### 3. 规则管理 (`rules`)

```bash
python taxon.py rules <操作> [选项]
```

操作：
- `list`: 列出所有自定义规则
- `add`: 添加新规则
- `remove`: 删除规则
- `clear`: 清空所有规则

添加规则选项：
- `--name, -n`: 规则名称
- `--type, -t`: 规则类型（keyword/regex/extension）
- `--pattern, -p`: 匹配模式
- `--folder, -f`: 目标文件夹
- `--priority`: 优先级（数字越大优先级越高）
- `--case-sensitive`: 是否区分大小写

示例：
```bash
# 列出所有规则
python taxon.py rules list

# 添加关键词规则：文件名包含"发票"的文件移动到"invoices"文件夹
python taxon.py rules add --name "发票文件" --type keyword --pattern "发票" --folder invoices

# 添加正则规则：匹配日期格式的文件
python taxon.py rules add --name "日期文件" --type regex --pattern "\d{4}-\d{2}-\d{2}" --folder dated --priority 10

# 添加扩展名规则：.xlsx文件移动到"excel"文件夹
python taxon.py rules add --name "Excel文件" --type extension --pattern ".xlsx" --folder excel

# 删除规则
python taxon.py rules remove --name "发票文件"
```

#### 4. 配置管理 (`config`)

```bash
python taxon.py config <操作> [值]
```

操作：
- `show`: 显示当前配置
- `set-path`: 设置默认下载文件夹路径
- `set-conflict`: 设置冲突解决策略

示例：
```bash
# 查看配置
python taxon.py config show

# 设置默认下载路径
python taxon.py config set-path ~/Downloads

# 设置冲突解决策略为跳过
python taxon.py config set-conflict skip
```

## 规则类型说明

### 1. 关键词规则 (keyword)
匹配文件名中包含指定关键词的文件。

示例：
```bash
python taxon.py rules add --name "工作文件" --type keyword --pattern "工作" --folder work
```

### 2. 正则表达式规则 (regex)
使用正则表达式匹配文件名。

示例：
```bash
# 匹配包含日期的文件：2024-01-01_report.pdf
python taxon.py rules add --name "日期文件" --type regex --pattern "\d{4}-\d{2}-\d{2}" --folder dated
```

### 3. 扩展名规则 (extension)
匹配特定扩展名的文件。

示例：
```bash
python taxon.py rules add --name "Excel文件" --type extension --pattern ".xlsx" --folder excel
```

## 冲突解决策略

- **rename**（默认）：如果目标文件已存在，自动重命名新文件（添加数字后缀）
- **skip**：如果目标文件已存在，跳过该文件
- **overwrite**：如果目标文件已存在，覆盖旧文件

## 配置文件

配置文件默认保存在 `~/.taxon_config.json`，包含以下内容：

```json
{
  "default_download_path": "/home/user/Downloads",
  "rules": [
    {
      "name": "发票文件",
      "rule_type": "keyword",
      "pattern": "发票",
      "target_folder": "invoices",
      "priority": 0,
      "case_sensitive": false
    }
  ],
  "conflict_resolution": "rename",
  "dry_run": false
}
```

## 扩展性

### 添加新的文件类型分类

编辑 `utils/file_utils.py` 中的 `get_file_category` 函数，添加新的扩展名映射：

```python
cate_rules = {
    'images': ['.jpg', '.jpeg', '.png', ...],
    'your_category': ['.ext1', '.ext2', ...],
    # ...
}
```

### 自定义规则优先级

规则按优先级排序，优先级高的规则会先匹配。如果多个规则都匹配，使用优先级最高的规则。

## 示例场景

### 场景1：整理工作文件
```bash
# 添加规则：文件名包含"项目"的文件移动到"projects"文件夹
python taxon.py rules add --name "项目文件" --type keyword --pattern "项目" --folder projects

# 添加规则：.xlsx文件移动到"excel"文件夹
python taxon.py rules add --name "Excel文件" --type extension --pattern ".xlsx" --folder excel

# 整理文件
python taxon.py organize
```

### 场景2：定时整理
```bash
# 设置默认下载路径
python taxon.py config set-path ~/Downloads

# 启动定时任务（每30分钟运行一次）
python taxon.py schedule --interval 30
```

### 场景3：预览整理效果
```bash
# 使用干运行模式查看整理效果
python taxon.py organize --dry-run
```

## 注意事项

1. 首次运行前建议使用 `--dry-run` 模式预览效果
2. 定时任务会持续运行，按 Ctrl+C 停止
3. 规则优先级：自定义规则 > 默认扩展名分类
4. 配置文件会自动创建，无需手动创建


