#!/usr/bin/env python3
"""
Markdown to PDF converter for weekly reports.
Usage: python md_to_pdf.py <input.md> [output.pdf]
"""

import sys
import os

def convert_with_pdfkit(md_path, pdf_path):
    """Convert using pdfkit (requires wkhtmltopdf)."""
    import pdfkit
    import markdown

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    html_full = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: "Microsoft YaHei", sans-serif; padding: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{html}
</body>
</html>'''

    pdfkit.from_string(html_full, pdf_path)
    print(f"PDF generated: {pdf_path}")

def convert_with_weasyprint(md_path, pdf_path):
    """Convert using weasyprint."""
    from weasyprint import HTML
    import markdown

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    html_full = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @page {{ margin: 2cm; }}
        body {{ font-family: "Microsoft YaHei", sans-serif; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
{html}
</body>
</html>'''

    HTML(string=html_full).write_pdf(pdf_path)
    print(f"PDF generated: {pdf_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <input.md> [output.pdf]")
        sys.exit(1)

    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    pdf_path = sys.argv[2] if len(sys.argv) > 2 else md_path.rsplit('.', 1)[0] + '.pdf'

    # Try pdfkit first, fallback to weasyprint
    try:
        convert_with_pdfkit(md_path, pdf_path)
    except ImportError:
        try:
            convert_with_weasyprint(md_path, pdf_path)
        except ImportError:
            print("Error: Please install pdfkit or weasyprint")
            print("  pip install pdfkit markdown")
            print("  or")
            print("  pip install weasyprint markdown")
            sys.exit(1)

if __name__ == '__main__':
    main()
