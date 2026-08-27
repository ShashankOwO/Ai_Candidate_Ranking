from pathlib import Path
from pypdf import PdfReader
from docx import Document



def extract_pdf_text(file_path:str)->str:

    reader=PdfReader(file_path)

    text=[]

    for page in reader.pages:
        page_text=page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_docx_text(file_path:str)->str:

    document=Document(file_path)

    text=[]

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


def extract_resume_text(
        file_path:str,
        file_type:str,
)->str:

    if file_type=="application/pdf":
        return extract_pdf_text(file_path)

    if file_type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_docx_text(file_path)

    raise ValueError(
        "Unsupported resume format"
    )
