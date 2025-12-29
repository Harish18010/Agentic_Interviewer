from fpdf import FPDF

def generate_pdf_report(candidate_name, role, feedback_data, filename="Interview_Report.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Interview Report: {role}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Candidate: {candidate_name}", ln=True)
    pdf.ln(10)
    

    for item in feedback_data:
       
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"Q{item['index']}: {item['question']}")
        
     
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 10, f"Your Answer: {item['user_answer']}")
        
      
        status_color = (0, 128, 0) if "Correct" in item['status'] else (255, 0, 0)
        pdf.set_text_color(*status_color)
        pdf.cell(0, 10, f"Status: {item['status']}", ln=True)
        pdf.set_text_color(0, 0, 0) # Reset to black
        
       
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 10, f"Detailed Feedback: {item['detailed_feedback']}")
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    pdf.output(filename)
    return filename