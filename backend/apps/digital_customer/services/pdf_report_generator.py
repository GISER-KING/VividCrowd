"""
培训评价报告生成器 - PDF 格式（使用 WeasyPrint）
"""
from io import BytesIO
import markdown
from weasyprint import HTML, CSS


def generate_pdf_from_markdown(markdown_content: str) -> BytesIO:
    """
    使用 WeasyPrint 将 Markdown 内容转换为 PDF

    Args:
        markdown_content: Markdown 格式的报告内容

    Returns:
        BytesIO: PDF 文件的字节流
    """
    # 将 Markdown 转换为 HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=['tables', 'fenced_code', 'nl2br']
    )

    # 添加完整的 HTML 结构和 CSS 样式
    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}

        body {{
            font-family: "Microsoft YaHei", "SimSun", "Arial", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}

        h1 {{
            color: #2c3e50;
            font-size: 24pt;
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #3498db;
            page-break-after: avoid;
        }}

        h2 {{
            color: #3498db;
            font-size: 16pt;
            margin-top: 25px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
            page-break-after: avoid;
        }}

        h3 {{
            color: #34495e;
            font-size: 13pt;
            margin-top: 15px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}

        h4 {{
            color: #555;
            font-size: 11pt;
            margin-top: 12px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }}

        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}

        ul, ol {{
            margin: 10px 0;
            padding-left: 25px;
            page-break-inside: avoid;
        }}

        li {{
            margin: 5px 0;
        }}

        p {{
            margin: 8px 0;
        }}

        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}

        /* 避免在标题后立即分页 */
        h1, h2, h3, h4 {{
            page-break-after: avoid;
        }}

        /* 避免在列表内部分页 */
        ul, ol {{
            page-break-inside: avoid;
        }}

        /* 保持段落完整 */
        p {{
            orphans: 3;
            widows: 3;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

    # 使用 WeasyPrint 生成 PDF
    pdf_buffer = BytesIO()
    HTML(string=full_html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer
