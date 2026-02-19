from pypdf import PdfReader

def textToPdf(file_path:str):

    reader = PdfReader(file_path)
    res = " "
    for page in reader.pages:

        res = res + page.extract_text()
    
    return res
    


