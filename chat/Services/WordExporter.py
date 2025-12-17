import json
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from django.conf import settings

def json_to_word(patent_json: dict, output_path: str):
    """
    این تابع JSON اختراع را گرفته و آن را به یک فایل Word تبدیل می‌کند.
    """
    doc = Document()

    # تنظیم فونت فارسی پیش‌فرض
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'  # می‌توان به Nazanin یا IranSans تغییر داد
    font.size = Pt(12)

    content = patent_json.get("patent_content", {})

    # --- عنوان اختراع ---
    title_text = content.get("invention_title", "عنوان اختراع ندارد")
    title = doc.add_heading(title_text, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- کلمات کلیدی ---
    keywords = content.get("keywords", [])
    if keywords:
        doc.add_heading("کلمات کلیدی", level=1)
        doc.add_paragraph("، ".join(keywords))

    # --- چکیده ---
    abstract = content.get("abstract", {}).get("text", "")
    if abstract:
        doc.add_heading("چکیده", level=1)
        doc.add_paragraph(abstract)

    # --- شرح اختراع ---
    description = content.get("description", {})

    def add_section(title, text):
        if text:
            doc.add_heading(title, level=1)
            doc.add_paragraph(text)

    add_section("زمینه فنی اختراع", description.get("technical_field", ""))
    add_section("مشکل فنی و اهداف اختراع", description.get("technical_problem_and_objectives", ""))
    add_section("پیشینه اختراع", description.get("prior_art_and_background", ""))
    add_section("راه‌حل فنی", description.get("technical_solution", ""))
    add_section("شرح کامل فرآیند", description.get("detailed_description", ""))

    # --- مراحل فرآیند ---
    process_steps = description.get("process_steps", [])
    if process_steps:
        doc.add_heading("مراحل فرآیند", level=1)
        for step in process_steps:
            doc.add_paragraph(step, style='List Number')

    add_section("شرایط فرآیند", description.get("process_conditions", ""))
    add_section("مواد اولیه", description.get("materials_and_inputs", ""))
    add_section("تجهیزات مورد استفاده", description.get("equipment_used", ""))
    add_section("کاربرد صنعتی", description.get("industrial_applicability", ""))

    # --- ادعاها ---
    claims = content.get("claims", {})
    independent_claims = claims.get("independent_claims", [])
    dependent_claims = claims.get("dependent_claims", [])

    if independent_claims:
        doc.add_heading("ادعاهای مستقل", level=1)
        for c in independent_claims:
            doc.add_paragraph(c, style='List Number')

    if dependent_claims:
        doc.add_heading("ادعاهای وابسته", level=1)
        for c in dependent_claims:
            doc.add_paragraph(c, style='List Number')

    # --- ذخیره فایل ---
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
