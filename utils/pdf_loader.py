import fitz  

def get_pdf_text(uploaded_file):
    try:
        file_stream = uploaded_file.read()
        doc = fitz.open(stream=file_stream, filetype="pdf")
        
        full_content = ""
        extracted_links = []

        for page in doc:
           
            full_content += page.get_text() + "\n"
            
            links = page.get_links()
            for link in links:
                if "uri" in link:
                    extracted_links.append(link["uri"])
        
        doc.close()

        
        if extracted_links:
            full_content += "\n--- EXTRACTED LINKS ---\n"
            full_content += "\n".join(set(extracted_links))

        return full_content
    except Exception as e:
        print(f"Error parsing PDF with links: {e}")
        return ""