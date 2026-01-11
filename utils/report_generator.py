from fpdf import FPDF

def clean_text(text):
    if not isinstance(text, str):
        return str(text)
    
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2026": "...",
        "\u2212": "-",
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
        
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(candidate_name, role, feedback_data, filename="Interview_Report.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Interview Report: {clean_text(role)}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Candidate: {clean_text(candidate_name)}", ln=True)
    pdf.ln(10)
    
    for item in feedback_data:
       
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"Q{item.get('index', '#')}: {clean_text(item['question'])}")
        
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 10, f"Your Answer: {clean_text(item['user_answer'])}")
        
        status_color = (0, 128, 0) if "Correct" in item['status'] else (255, 0, 0)
        pdf.set_text_color(*status_color)
        pdf.cell(0, 10, f"Status: {clean_text(item['status'])}", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 10, f"Detailed Feedback: {clean_text(item['detailed_feedback'])}")
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    pdf.output(filename)
    return filename