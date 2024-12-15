from decimal import InvalidOperation
import PyPDF2
from docx import Document

def extract_text_from_file(uploaded_file):
    
     # Process PDF file
    if uploaded_file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
     # Process text files (e.g., .txt)
    elif uploaded_file.name.endswith('.txt'):
        text = uploaded_file.read().decode('utf-8')  # Read and decode text
        return text
      
     # Read and process the .docx file
    elif uploaded_file.name.endswith('.docx'):
        # Load the .docx file
        document = Document(uploaded_file)
        text = []
        for paragraph in document.paragraphs:
            text.append(paragraph.text)             # Extract text from each paragraph
        text = "\n".join(text)
        return text
    else:
        raise InvalidOperation("Invalid Operations")