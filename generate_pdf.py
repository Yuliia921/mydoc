from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf(fields: dict, template_name: str) -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVuB", "", "DejaVuSans-Bold.ttf", uni=True)
    pdf.add_page()

    key_width = 60
    val_width = pdf.w - pdf.l_margin - pdf.r_margin - key_width

    pdf.set_font("DejaVuB", "", 14)
    pdf.cell(0, 10, template_name, ln=True, align="C")
    pdf.ln(5)

    def write_block(title, pairs):
        if pairs:
            pdf.set_font("DejaVuB", "", 12)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font("DejaVu", "", 12)
            for key, value in pairs:
                value = value.strip()
                if value:
                    y_before = pdf.get_y()
                    pdf.set_xy(pdf.l_margin, y_before)
                    pdf.cell(key_width, 10, f"{key}:", ln=False)
                    pdf.multi_cell(val_width, 10, value)
            pdf.ln(2)

    write_block("👩 Пациент", [
        ("ФИО", fields.get("ФИО", "")),
        ("Последняя менструация", fields.get("Последняя менструация", ""))
    ])

    write_block("🧠 Матка и структуры", [
        ("Положение матки", fields.get("Положение матки", "")),
        ("Размер плодного яйца", fields.get("Размер плодного яйца", "")),
        ("Размер эмбриона", fields.get("Размер эмбриона", "")),
        ("Желточный мешок", fields.get("Желточный мешок", "")),
        ("Расположение хориона", fields.get("Расположение хориона", "")),
        ("Желтое тело", fields.get("Желтое тело", ""))
    ])

    write_block("👶 Плод", [
        ("Сердцебиение и ЧСС", fields.get("Сердцебиение и ЧСС", ""))
    ])

    write_block("📎 Дополнительные данные", [
        ("", fields.get("Дополнительные данные", ""))
    ])
    write_block("📌 Заключение", [
        ("", fields.get("Заключение", ""))
    ])
    write_block("📋 Рекомендации", [
        ("", fields.get("Рекомендации", ""))
    ])

    pdf.ln(4)
    pdf.cell(0, 10, "Врач акушер-гинеколог Куриленко Юлия Сергеевна", ln=True)
    pdf.cell(0, 10, "+37455987715", ln=True)
    pdf.cell(0, 10, "Telegram: https://t.me/doc_Kurilenko", ln=True)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Куриленко_Юлия_{now}.pdf"
    filepath = os.path.join("tmp", filename)
    os.makedirs("tmp", exist_ok=True)
    pdf.output(filepath)

    return filepath