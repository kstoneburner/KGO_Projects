# https://vincent.codes.finance/posts/documents-llm/


import os, time, sys
os.system('cls')

model_type = "mixtral:latest"


print("Hola: stuffing_pdf.py")

from langchain_community.document_loaders.pdf import PyPDFLoader


file_path = "DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()


# Prompt
from langchain_core.prompts import PromptTemplate

prompt_template = """Write a long summary of the following document. 
Only include information that is part of the document. 
Do not include your own opinion or analysis.

Document:
"{document}"
Summary:"""
prompt = PromptTemplate.from_template(prompt_template)

# Define LLM Chain

from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain

llm = ChatOpenAI(
    temperature=0.1,
    model_name=model_type,
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)
llm_chain = LLMChain(llm=llm, prompt=prompt)

