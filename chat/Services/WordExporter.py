import json
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from django.conf import settings


def summary_to_word(patent_json, output_path):
    doc = Document()
    section = doc.sections[0]
    section.right_to_left = True

    style = doc.styles['Normal']
    style.font.name = 'B Nazanin'
    style.font.size = Pt(12)

    # تیتر خلاصه
    p = doc.add_paragraph()
    p.add_run("خلاصه اختراع:").bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # عنوان اختراع
    title = patent_json.get("patent_content", {}).get("invention_title")
    if title:
        p = doc.add_paragraph()
        p.add_run(f"عنوان اختراع: {title}").bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # متن خلاصه
    abstract = patent_json.get("patent_content", {}).get("abstract", {}).get("text")
    if abstract:
        p = doc.add_paragraph(abstract)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(output_path)


def description_to_word(patent_json, output_path):
    doc = Document()
    section = doc.sections[0]
    section.right_to_left = True

    style = doc.styles['Normal']
    style.font.name = 'B Nazanin'
    style.font.size = Pt(12)

    def bold_paragraph(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        return p

    d = patent_json.get("patent_content", {}).get("description", {})
    title = patent_json.get("patent_content", {}).get("invention_title")

    bold_paragraph("توصیف اختراع")

    # عنوان اختراع
    if title:
        bold_paragraph("عنوان اختراع (به گونه ای که در اظهارنامه ذکر گردیده است)")
        p = doc.add_paragraph(title)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # زمینه فنی
    technical_field = d.get("technical_field")
    if technical_field:
        bold_paragraph("زمینه فنی اختراع مربوط")
        p = doc.add_paragraph(technical_field)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # مشکل فنی و اهداف
    technical_problem = d.get("technical_problem", [])
    objectives = d.get("objectives", [])
    if technical_problem or objectives:
        bold_paragraph("مشکل فنی و بیان اهداف اختراع")
        if technical_problem:
            bold_paragraph("مشکل فنی:")
            for i, item in enumerate(technical_problem, 1):
                p = doc.add_paragraph(f"{i}. {item}")
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if objectives:
            bold_paragraph("بیان اهداف اختراع:")
            for i, item in enumerate(objectives, 1):
                p = doc.add_paragraph(f"{i}. {item}")
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # دانش پیشین
    prior_art = d.get("prior_art")
    if prior_art:
        bold_paragraph("شرح وضعیت دانش پیشین و سابقه پیشرفت هایی که در ارتباط با اختراع ادعایی وجود دارد")
        p = doc.add_paragraph(prior_art)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # راه حل
    solution = d.get("solution")
    if solution:
        bold_paragraph("ارائه راه حل برای مشکل فنی موجود همراه با شرح دقیق و کافی و یکپارچه اختراع")
        p = doc.add_paragraph(solution)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # فرآیند تولید
    production_process = d.get("production_process", {})
    if production_process:
        bold_paragraph("شرح دقیق فرآیند تولید")
        for step_title, step_text in production_process.items():
            bold_paragraph(step_title)
            p = doc.add_paragraph(step_text)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # مزایا
    advantages = d.get("advantages", [])
    if advantages:
        bold_paragraph("بیان واضح و دقیق مزایای اختراع ادعایی نسبت به اختراعات پیشین")
        for i, adv in enumerate(advantages, 1):
            p = doc.add_paragraph(f"{i}. {adv}")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # کاربرد صنعتی
    industrial_application = d.get("industrial_application")
    if industrial_application:
        bold_paragraph("ذکر صریح کاربرد صنعتی اختراع")
        p = doc.add_paragraph(industrial_application)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(output_path)


def claims_to_word(patent_json, output_path):
    doc = Document()
    section = doc.sections[0]
    section.right_to_left = True

    style = doc.styles['Normal']
    style.font.name = 'B Nazanin'
    style.font.size = Pt(12)

    def bold_paragraph(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        return p

    bold_paragraph("ادعانامه")
    bold_paragraph("آنچه ادعا می‌شود:")

    claims = patent_json.get("patent_content", {}).get("claims", {}).get("items", [])
    for i, claim in enumerate(claims, 1):
        p = doc.add_paragraph()
        p.add_run(f"ادعای {i}) ").bold = True
        p.add_run(claim)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(output_path)
