import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def create_doc_style(doc):
    section = doc.sections[0]
    section.right_to_left = True
    style = doc.styles['Normal']
    style.font.name = 'B Nazanin'
    style.font.size = Pt(12)
    return doc


def summary_to_word(patent_json, output_path):
    doc = Document()
    create_doc_style(doc)

    # تیتر خلاصه
    p = doc.add_paragraph("خلاصه اختراع:")
    p.runs[0].bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # عنوان اختراع
    title = patent_json.get("patent_content", {}).get("invention_title")
    p = doc.add_paragraph(f"عنوان اختراع: {title if title else 'ارائه نشده'}")
    p.runs[0].bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # متن خلاصه داخل براکت
    abstract = patent_json.get("patent_content", {}).get("abstract", {}).get("text")
    p = doc.add_paragraph(f"{abstract if abstract else 'ارائه نشده'}")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(output_path)


def description_to_word(patent_json, output_path):
    doc = Document()
    create_doc_style(doc)

    def add_bold_paragraph(text):
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.runs[0].bold = True
        return p

    d = patent_json.get("patent_content", {}).get("description", {})
    title = patent_json.get("patent_content", {}).get("invention_title")

    add_bold_paragraph("توصیف اختراع")
    add_bold_paragraph("عنوان اختراع (به گونه ای که در اظهارنامه ذکر گردیده است)")
    p = doc.add_paragraph(f"{title if title else 'ارائه نشده'}")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    technical_field = d.get("technical_field", "ارائه نشده")
    add_bold_paragraph("زمینه فنی اختراع مربوط")
    p = doc.add_paragraph(f"{technical_field}")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    technical_problem = d.get("technical_problem", [])
    objectives = d.get("objectives", [])
    add_bold_paragraph("مشکل فنی و بیان اهداف اختراع")
    if technical_problem:
        add_bold_paragraph("مشکل فنی:")
        for i, item in enumerate(technical_problem, 1):
            p = doc.add_paragraph(f"{i}. {item}")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p = doc.add_paragraph("ارائه نشده")
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    if objectives:
        add_bold_paragraph("بیان اهداف اختراع:")
        for i, item in enumerate(objectives, 1):
            p = doc.add_paragraph(f"{i}. {item}")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p = doc.add_paragraph("ارائه نشده")
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    prior_art = d.get("prior_art", "ارائه نشده")
    add_bold_paragraph("شرح وضعیت دانش پیشین و سابقه پیشرفت هایی که در ارتباط با اختراع ادعایی وجود دارد")
    p = doc.add_paragraph(f"{prior_art}")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    solution = d.get("solution", "ارائه نشده")
    add_bold_paragraph("ارائه راه حل برای مشکل فنی موجود همراه با شرح دقیق و کافی و یکپارچه اختراع")
    p = doc.add_paragraph(f"{solution}")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    production_process = d.get("production_process", {})
    add_bold_paragraph("شرح دقیق فرآیند تولید")
    if production_process:
        for step_title, step_text in production_process.items():
            add_bold_paragraph(step_title)
            p = doc.add_paragraph(f"{step_text}")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p = doc.add_paragraph("ارائه نشده")
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    advantages = d.get("advantages", [])
    add_bold_paragraph("بیان واضح و دقیق مزایای اختراع ادعایی نسبت به اختراعات پیشین")
    if advantages:
        for i, adv in enumerate(advantages, 1):
            p = doc.add_paragraph(f"{i}. {adv}")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p = doc.add_paragraph("ارائه نشده")
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    industrial_application = d.get("industrial_application", "ارائه نشده")
    add_bold_paragraph("ذکر صریح کاربرد صنعتی اختراع")
    p = doc.add_paragraph(f"{industrial_application}")
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(output_path)


def claims_to_word(patent_json, output_path):
    doc = Document()
    create_doc_style(doc)

    def add_bold_paragraph(text):
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.runs[0].bold = True
        return p

    add_bold_paragraph("ادعانامه")
    add_bold_paragraph("آنچه ادعا می‌شود:")

    claims = patent_json.get("patent_content", {}).get("claims", {}).get("items", [])
    if claims:
        for i, claim in enumerate(claims, 1):
            p = doc.add_paragraph(f"[ادعای {i}) {claim}]")
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p = doc.add_paragraph("ارائه نشده")
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(output_path)
