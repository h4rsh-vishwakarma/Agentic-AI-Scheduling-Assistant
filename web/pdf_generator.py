from fpdf import FPDF
from datetime import datetime
import os
def parse_datetime_flexible(dt_str):
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        # Handle fallback like '10:00' or '10:30'
        return datetime.strptime(dt_str, "%H:%M")
def generate_calendar_pdf(name, calendar_data, output_path):
    print(f"\n📄 Generating PDF for: {name}")
    print(f"📁 Output path: {output_path}")

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt=f"{name}'s Updated Calendar", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        
        for meeting in calendar_data.get("meetings", []):
            try:
                start = parse_datetime_flexible(meeting["start"]).strftime('%Y-%m-%d %H:%M')
                end = parse_datetime_flexible(meeting["end"]).strftime('%Y-%m-%d %H:%M')
                title = meeting.get("title", "No Title")
                pdf.cell(200, 10, txt=f"{title}: {start} - {end}", ln=True)
            except Exception as e:
                pdf.cell(200, 10, txt=f"❌ Error parsing meeting: {e}", ln=True)

        pdf.output(output_path)
        print(f"✅ PDF successfully written to: {output_path}")
        print("📂 Exists after write?", os.path.exists(output_path))

    except Exception as e:
        print(f"❌ Error during PDF generation: {e}")
