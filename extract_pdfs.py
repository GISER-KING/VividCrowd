import fitz
import sys

def extract_pdf_text(pdf_path, output_path):
    """提取PDF文本内容"""
    try:
        doc = fitz.open(pdf_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"总页数: {len(doc)}\n\n")
            for i in range(len(doc)):
                page = doc[i]
                text = page.get_text()
                f.write(f"\n{'='*50}\n")
                f.write(f"第 {i+1} 页\n")
                f.write(f"{'='*50}\n\n")
                f.write(text)
                f.write("\n")
        doc.close()
        print(f"成功提取 {pdf_path} 到 {output_path}")
    except Exception as e:
        print(f"提取失败: {e}")

if __name__ == "__main__":
    pdf_files = [
        (r"docs\20260206产品文档\AI数字面试平台-算法.pdf", "algorithm.txt"),
        (r"docs\20260206产品文档\简历分析.pdf", "resume.txt"),
        (r"docs\20260206产品文档\用户端和管理端.pdf", "user_admin.txt")
    ]

    for pdf_path, output_path in pdf_files:
        extract_pdf_text(pdf_path, output_path)
