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

    # فونت پیش‌فرض
    style = doc.styles['Normal']
    style.font.name = 'B Nazanin'
    style.font.size = Pt(12)

    # تیتر خلاصه اختراع
    p = doc.add_paragraph()
    run = p.add_run("خلاصه اختراع :")
    run.bold = True

    # عنوان اختراع
    title = patent_json["patent_content"]["invention_title"]
    p = doc.add_paragraph()
    run = p.add_run(f"عنوان اختراع: {title}")
    run.bold = True

    # متن خلاصه
    abstract = patent_json["patent_content"]["abstract"]["text"]
    p = doc.add_paragraph(abstract)

    doc.save(output_path)


def description_to_word(patent_json, output_path):
    doc = Document()

    section = doc.sections[0]
    section.right_to_left = True

    style = doc.styles['Normal']
    style.font.name = 'B Nazanin'
    style.font.size = Pt(12)

    d = patent_json["patent_content"]["description"]
    title = patent_json["patent_content"]["invention_title"]

    def bold_paragraph(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.bold = True

    # تیتر اصلی
    bold_paragraph("توصیف اختراع")

    # عنوان اختراع
    bold_paragraph("عنوان اختراع (به گونه ای که در اظهارنامه ذکر گردیده است)")
    doc.add_paragraph(title)

    # زمینه فنی
    bold_paragraph("زمینه فنی اختراع مربوط")
    doc.add_paragraph(d["technical_field"])

    # مشکل فنی و اهداف
    bold_paragraph("مشکل فنی و بیان اهداف اختراع")

    bold_paragraph("مشکل فنی:")
    for i, item in enumerate(d["technical_problem"], 1):
        doc.add_paragraph(f"{i}. {item}")

    bold_paragraph("بیان اهداف اختراع:")
    for i, item in enumerate(d["objectives"], 1):
        doc.add_paragraph(f"{i}. {item}")

    # دانش پیشین
    bold_paragraph("شرح وضعیت دانش پیشین و سابقه پیشرفت هایی که در ارتباط با اختراع ادعایی وجود دارد")
    doc.add_paragraph(d["prior_art"])

    # راه حل
    bold_paragraph("ارائه راه حل برای مشکل فنی موجود همراه با شرح دقیق و کافی و یکپارچه اختراع")
    doc.add_paragraph(d["solution"])

    # فرآیند تولید
    bold_paragraph("شرح دقیق فرآیند تولید پاستا غنی‌شده با پودر برگ مورینگا اولیفرا")
    for step_title, step_text in d["production_process"].items():
        bold_paragraph(step_title)
        doc.add_paragraph(step_text)

    # مزایا
    bold_paragraph("بیان واضح و دقیق مزایای اختراع ادعایی نسبت به اختراعات پیشین")
    for i, adv in enumerate(d["advantages"], 1):
        doc.add_paragraph(f"{i}. {adv}")

    # کاربرد صنعتی
    bold_paragraph("ذکر صریح کاربرد صنعتی اختراع")
    doc.add_paragraph(d["industrial_application"])

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

    # تیترها
    bold_paragraph("ادعانامه")
    bold_paragraph("آنچه ادعا می‌شود:")

    claims = patent_json["patent_content"]["claims"]["items"]

    for i, claim in enumerate(claims, 1):
        p = doc.add_paragraph()
        p.add_run(f"ادعای {i}) ").bold = True
        p.add_run(claim)

    doc.save(output_path)
