import pypdf

def get_pdf_text(uploaded_file):
    try:
        pdf_reader=pypdf.PdfReader(uploaded_file)
        text=""
        for page in pdf_reader.pages:
            text+=page.extract_text()+"\n"
        return text
    except Exception as e:
        print(f"ERROR:{e}")
        return ""