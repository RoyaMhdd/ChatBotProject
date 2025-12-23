import json
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def safe_get(d, keys, default=""):
    """
    گرفتن مقدار از دیکشنری چند سطحی بدون خطا
    keys: لیست کلیدها
    """
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d


def create_document():
    doc = Document()
    section = doc.sections[0]
    section.right_to_left = True

    style = doc.styles['Normal']
    style.font.name = 'B Nazanin'
    style.font.size = Pt(12)

    return doc


def add_bold_paragraph(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    return p


def summary_to_word(patent_json, output_path):
    doc = create_document()

    add_bold_paragraph(doc, "خلاصه اختراع :")

    title = safe_get(patent_json, ["patent_content", "invention_title"])
    if title:
        add_bold_paragraph(doc, f"عنوان اختراع: {title}")

    abstract = safe_get(patent_json, ["patent_content", "abstract", "text"])
    if abstract:
        doc.add_paragraph(abstract)

    try:
        doc.save(output_path)
    except Exception as e:
        print(f"خطا در ذخیره فایل: {e}")


def description_to_word(patent_json, output_path):
    doc = create_document()

    d = safe_get(patent_json, ["patent_content", "description"], {})
    title = safe_get(patent_json, ["patent_content", "invention_title"])

    add_bold_paragraph(doc, "توصیف اختراع")

    # عنوان اختراع
    add_bold_paragraph(doc, "عنوان اختراع (به گونه ای که در اظهارنامه ذکر گردیده است)")
    if title:
        doc.add_paragraph(title)

    # زمینه فنی
    tech_field = safe_get(d, ["technical_field"])
    if tech_field:
        add_bold_paragraph(doc, "زمینه فنی اختراع مربوط")
        doc.add_paragraph(tech_field)

    # مشکل فنی و اهداف
    tech_problem = safe_get(d, ["technical_problem"], [])
    objectives = safe_get(d, ["objectives"], [])

    if tech_problem or objectives:
        add_bold_paragraph(doc, "مشکل فنی و بیان اهداف اختراع")

    if tech_problem:
        add_bold_paragraph(doc, "مشکل فنی:")
        for i, item in enumerate(tech_problem, 1):
            doc.add_paragraph(f"{i}. {item}")

    if objectives:
        add_bold_paragraph(doc, "بیان اهداف اختراع:")
        for i, item in enumerate(objectives, 1):
            doc.add_paragraph(f"{i}. {item}")

    # دانش پیشین
    prior_art = safe_get(d, ["prior_art"])
    if prior_art:
        add_bold_paragraph(doc, "شرح وضعیت دانش پیشین و سابقه پیشرفت هایی که در ارتباط با اختراع ادعایی وجود دارد")
        doc.add_paragraph(prior_art)

    # راه حل
    solution = safe_get(d, ["solution"])
    if solution:
        add_bold_paragraph(doc, "ارائه راه حل برای مشکل فنی موجود همراه با شرح دقیق و کافی و یکپارچه اختراع")
        doc.add_paragraph(solution)

    # فرآیند تولید
    production_process = safe_get(d, ["production_process"], {})
    if production_process:
        add_bold_paragraph(doc, "شرح دقیق فرآیند تولید پاستا غنی‌شده با پودر برگ مورینگا اولیفرا")
        for step_title, step_text in production_process.items():
            if step_title:
                add_bold_paragraph(doc, step_title)
            if step_text:
                doc.add_paragraph(step_text)

    # مزایا
    advantages = safe_get(d, ["advantages"], [])
    if advantages:
        add_bold_paragraph(doc, "بیان واضح و دقیق مزایای اختراع ادعایی نسبت به اختراعات پیشین")
        for i, adv in enumerate(advantages, 1):
            doc.add_paragraph(f"{i}. {adv}")

    # کاربرد صنعتی
    industrial_app = safe_get(d, ["industrial_application"])
    if industrial_app:
        add_bold_paragraph(doc, "ذکر صریح کاربرد صنعتی اختراع")
        doc.add_paragraph(industrial_app)

    try:
        doc.save(output_path)
    except Exception as e:
        print(f"خطا در ذخیره فایل: {e}")


def claims_to_word(patent_json, output_path):
    doc = create_document()

    add_bold_paragraph(doc, "ادعانامه")
    add_bold_paragraph(doc, "آنچه ادعا می‌شود:")

    claims = safe_get(patent_json, ["patent_content", "claims", "items"], [])

    for i, claim in enumerate(claims, 1):
        p = doc.add_paragraph()
        p.add_run(f"ادعای {i}) ").bold = True
        p.add_run(claim)

    try:
        doc.save(output_path)
    except Exception as e:
        print(f"خطا در ذخیره فایل: {e}")
