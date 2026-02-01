---
name: weekly-report-generator
description: 自动生成周度工作汇报并可导出 PDF 附件。当用户需要：(1) 生成周报/工作总结/周度汇报，(2) 导出周报 PDF，(3) 整理本周工作内容时触发。读取模板和项目数据，输出 Markdown 格式汇报或 PDF 文件。
---

# 周报生成器

## 工作流程

1. 读取模板 `assets/template.md`
2. 使用 Glob 定位项目相关文件（如 TODO、CHANGELOG、git log 等）
3. 使用 Read 提取关键数据
4. 填充模板，生成周报
5. （可选）导出 PDF 附件

## 推荐工具

- Read - 读取模板和项目文件
- Glob - 定位相关文件
- Write - 写入生成的周报文件
- Bash - 执行 PDF 转换命令

## 数据来源

按优先级查找以下文件获取周报素材：

| 数据类型 | 文件模式 |
|---------|---------|
| 任务记录 | `**/TODO.md`, `**/tasks.md` |
| 变更日志 | `**/CHANGELOG.md`, `**/CHANGES.md` |
| 会议纪要 | `**/meeting*.md`, `**/notes/*.md` |
| 项目文档 | `**/README.md`, `**/docs/*.md` |

## 输出格式

### Markdown 输出
- 格式：Markdown
- 风格：简洁专业，条目清晰
- 结构：按模板章节组织

### PDF 输出
- 使用 Python 脚本 `scripts/md_to_pdf.py` 转换
- 依赖：markdown、weasyprint 或 pdfkit
- 输出路径：与 Markdown 文件同目录

## PDF 生成方法

### 方法一：使用 pdfkit（推荐）

```python
import pdfkit
import markdown

md_content = open('weekly_report.md').read()
html = markdown.markdown(md_content, extensions=['tables'])
html_full = f'<html><head><meta charset="utf-8"><style>body{{font-family:sans-serif;padding:20px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px}}</style></head><body>{html}</body></html>'
pdfkit.from_string(html_full, 'weekly_report.pdf')
```

### 方法二：使用 weasyprint

```python
from weasyprint import HTML
import markdown

md_content = open('weekly_report.md').read()
html = markdown.markdown(md_content, extensions=['tables'])
HTML(string=html).write_pdf('weekly_report.pdf')
```

## 使用示例

### 示例一：生成 Markdown 周报

用户输入：
> 帮我生成本周的工作周报

执行步骤：
1. 读取 `assets/template.md` 获取模板结构
2. 使用 Glob 查找 `**/TODO.md`、`**/CHANGELOG.md` 等文件
3. 使用 Read 提取本周相关内容
4. 汇总数据，填充模板
5. 输出完整周报

### 示例二：生成 PDF 附件

用户输入：
> 生成本周周报并导出 PDF

执行步骤：
1. 完成 Markdown 周报生成
2. 使用 Write 保存 `weekly_report.md`
3. 执行 PDF 转换脚本
4. 输出 `weekly_report.pdf`
