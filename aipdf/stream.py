#//*** Python Streamlit Application Example
#//*** https://medium.com/@anoopjohny2000/building-a-llama-3-1-8b-streamlit-chat-app-with-local-llms-a-step-by-step-guide-using-ollama-749931de216a

#// python -m streamlit run stream.py


import streamlit as st
from llama_index.core.llms import ChatMessage
import logging
import time

import pdfplumber, os, re, sys
import ollama,chromadb

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter  
#from langchain_community.embeddings import HuggingFaceEmbeddings 
#from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_community.vectorstores import FAISS  
from langchain_community.llms import Ollama  

#//*** Global Settings
g = {
	"path" : {
		"chroma" : "persistent_document_db",
		"pdf" : "./pdf",
	},
	"embedding_model" : "mxbai-embed-large",
	"model" : "llama3.2",
	"model" : "deepseek-r1:1.5b",
	"model" : "deepseek-r1:70b",
	"model" : "gemma3:1b",
	"model" : "mixtral",
}#//*** END global Settings

g["embedding_model"] = g["model"]
path_model = g["model"]
path_model = path_model.replace(":","_")

path_model = f"pdf_{path_model}"

file_path = "DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf"
#//*** Used to store files that in the database. For starter we will not add duplicate file names
db_files = []
process_pdf = False

collection_name = file_path.split(".")[0]
print(collection_name)

#//*** Spin up Chroma DB interfcae
#client = chromadb.Client() #<---  Memory only Client
client = chromadb.PersistentClient(path=path_model) # <--- Save Documents to Disk
collection = client.get_or_create_collection(name="docs")
#collection = client.get_or_create_collection(name="collection_name")




logging.basicConfig(level=logging.INFO)

if 'messages' not in st.session_state:
    st.session_state.messages = []


def handlePrompt():
	st.text_input("Generate Prompt: ", value="Summarize OGML",key="prompt_input", on_change=handlePromptResponse, args=None)
	st.text_input("Chat Prompt: ", value="Summarize OGML",key="prompt_input_chat", on_change=handlePromptChat, args=None)
	#callback(prompt)

def dd():
	print("CALLBACK")
	st.write(st.session_state.prompt_input)
	print(st.session_state.prompt_input)

def list_to_string(input_list):
	
	output = ""
	#//*** Combine the Query results into a single data string for the llm.
	for text in input_list:
		print(text)
		output+=text

	return output

def handlePromptResponse():
	#//*** Called as Part of On_Change of st.text_input
	print("CALLBACK")

	#//*** Writes the Text_input value to the session state using the key prompt_input which is assign to st.text_input
	st.write(st.session_state.prompt_input)

	#//*** Pull the session_state
	prompt = st.session_state.prompt_input
	# generate an embedding for the prompt and retrieve the most relevant doc
	st.info("Building Embedding Response")
	st.sidebar.write("Building Embedding Response")
	response = ollama.embeddings(
	  prompt=prompt,
	  model=g["model"]
	)

	print("=== Response ----")
	st.sidebar.write("Getting Results")
	results = collection.query(
	  query_embeddings=[response["embedding"]],
	  n_results=10
	)

	data = results['documents'][0][0]
	st.sidebar.write(results)
	print("Prompting")
	#print(results['documents'][0][0])
	#print(response)
	#print(results)

	st.info("Generating Response")
	# generate a response combining the prompt and data we retrieved in step 2
	output = ollama.generate(
	  model=g["model"],
	  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
	)

	print(output['response'])
	st.info(output['response'])
	print("END Response")

	#handlePrompt(handlePromptResponse)

def handlePromptChat():
	#//*** Called as Part of On_Change of st.text_input
	print("CALLBACK")

	#//*** Writes the Text_input value to the session state using the key prompt_input which is assign to st.text_input
	st.write(st.session_state.prompt_input)

	#//*** Pull the session_state
	prompt = st.session_state.prompt_input
	# generate an embedding for the prompt and retrieve the most relevant doc
	st.info("Building Embedding Response")
	st.sidebar.write("Building Embedding Response")
	response = ollama.embeddings(
	  prompt=prompt,
	  model=g["model"]
	)

	print("=== Response ----")
	st.sidebar.write("Getting Results")
	results = collection.query(
	  query_embeddings=[response["embedding"]],
	  n_results=10
	)

	data = results['documents'][0][0]

	data = list_to_string(results['documents'][0])
	st.sidebar.write(data)
	print("Prompting")
	#print(results['documents'][0][0])
	#print(response)
	#print(results)

	st.info("Generating Response")
	# generate a response combining the prompt and data we retrieved in step 2
	output = ollama.generate(
	  model=g["model"],
	  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
	)

	print(output['response'])
	st.info(output['response'])
	print("END Response")

	#handlePrompt(handlePromptResponse)

def main():
	print("Hello World")


	# Title
	#st.title("Hello GeeksForGeeks !!!")

	# success
	#st.success("Success")

	# success
	#st.info("Information")

	# success
	#st.warning("Warning")

	# success
	#st.error("Error")

	# Exception - This has been added later
	#exp = ZeroDivisionError("Trying to divide by Zero")
	#st.exception(exp)

	st.sidebar.write("___")
	
	#//**** Load AI
	print("Load AI")
	print("Prompting")

	# an example prompt
	prompt = "Summarize OGML"
	#prompt = "What are the best things in life?"
	prompt = "using OG Script Reference How would I configure a rosstalk listener in Dashboard?"

	print("Initialize Handle Prompt")
	handlePrompt()

	#print("Prompt: ", prompt)

	print("END MAIN")
	return
	# generate an embedding for the prompt and retrieve the most relevant doc
	response = ollama.embeddings(
	  prompt=prompt,
	  model=g["model"]
	)

	print("=== Response ----")
	results = collection.query(
	  query_embeddings=[response["embedding"]],
	  n_results=10
	)

	data = results['documents'][0][0]



	print("Prompting")
	#print(results['documents'][0][0])
	#print(response)
	#print(results)

	# generate a response combining the prompt and data we retrieved in step 2
	#output = ollama.generate(
	#  model=g["model"],
	#  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
	#)

	#print(output['response'])
	#st.info(output['response'])
	#print("END MAIN")

	output = ollama.chat(
	  model=g["model"],
	  messages=[{'role': 'user', 'content' :"Using this data: {data}. Respond to this prompt: {prompt}"}]
	)

	for chunk in output:
  		print(chunk['message']['content'], end='', flush=True)


if __name__ == "__main__":
	main()