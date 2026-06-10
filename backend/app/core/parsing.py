from pypdf import PdfReader

def extract_pdf_text(file_path:str):

    reader = PdfReader(file_path)
    res = " "
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            res += page_text
    return res
    


