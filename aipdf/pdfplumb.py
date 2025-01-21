#ollama prompt: write a python script that builds a chatbot that references information in a PDF. All Libraries including the ollama chatbot must run locally
# pip install pdfplumber
# ollama run codeqwen
import pdfplumber, os
from ollama import Client

file_path = "DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf"

if not os.path.isfile:
    with pdfplumber.open(file_path,unicode_norm="NFC") as pdf:
        text = ""
        for page in pdf.pages:
            try:
                text += page.extract_text()
            except:
                pass


    print(text)

    with open("test.txt","w") as f:
        f.write(str(text.encode('utf8')))

with open("test.txt","r") as f:
    text = f.read();

print(text) 
print("Done!")

ollama_url = "http://localhost:11434"

def ollama_query(prompt):
    ollama = Client(ollama_url)
    response = ollama.generate('codeqwen', prompt=prompt)
    #return response['choices'][0]['text'].strip()
    return response['response']

while True:
    user_input = input("User: ")
    if user_input.lower() == 'exit':
        break

    # Build your prompt here, e.g., concatenate user's input with the extracted text
    prompt = f"{text} User: {user_input}"
    ollama_response = ollama_query(prompt)

    print("Ollama:", ollama_response)

