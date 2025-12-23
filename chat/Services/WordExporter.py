import json
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from django.conf import settings



def summary_to_word(patent_json, output_path):
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(12)

    content = patent_json.get("patent_content", {})

    title = content.get("invention_title", "عنوان اختراع ندارد")
    doc.add_heading(title, level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    abstract = content.get("abstract", {}).get("text", "")
    if abstract:
        doc.add_heading("خلاصه اختراع", level=1)
        doc.add_paragraph(abstract)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)


def description_to_word(patent_json, output_path):
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(12)

    content = patent_json.get("patent_content", {})
    description = content.get("description", {})

    doc.add_heading("توضیح اختراع", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_section(title, key):
        text = description.get(key, "")
        if text:
            doc.add_heading(title, level=1)
            doc.add_paragraph(text)

    add_section("زمینه فنی اختراع", "technical_field")
    add_section("مشکل فنی و اهداف اختراع", "technical_problem_and_objectives")
    add_section("پیشینه اختراع", "prior_art_and_background")
    add_section("راه‌حل فنی", "technical_solution")
    add_section("شرح کامل فرآیند", "detailed_description")

    steps = description.get("process_steps", [])
    if steps:
        doc.add_heading("مراحل فرآیند", level=1)
        for step in steps:
            doc.add_paragraph(step, style='List Number')

    add_section("شرایط فرآیند", "process_conditions")
    add_section("مواد اولیه", "materials_and_inputs")
    add_section("تجهیزات مورد استفاده", "equipment_used")
    add_section("کاربرد صنعتی", "industrial_applicability")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)


def claims_to_word(patent_json, output_path):
    doc = Document()

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(12)

    content = patent_json.get("patent_content", {})
    claims = content.get("claims", {})

    doc.add_heading("ادعانامه", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    for c in claims.get("independent_claims", []):
        doc.add_paragraph(c, style='List Number')

    for c in claims.get("dependent_claims", []):
        doc.add_paragraph(c, style='List Number')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)

