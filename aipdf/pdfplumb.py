#ollama prompt: write a python script that builds a chatbot that references information in a PDF. All Libraries including the ollama chatbot must run locally
# pip install pdfplumber
# ollama run codeqwen
import pdfplumber

file_path = "DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf"

with pdfplumber.open(file_path) as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text()


print(text)
