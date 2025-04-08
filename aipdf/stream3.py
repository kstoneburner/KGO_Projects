#//*** Python Streamlit Application Example
#//*** https://medium.com/@anoopjohny2000/building-a-llama-3-1-8b-streamlit-chat-app-with-local-llms-a-step-by-step-guide-using-ollama-749931de216a

#// python -m streamlit run stream3.py


import streamlit as st
from llama_index.core.llms import ChatMessage
import logging
import time

import pdfplumber, os, re, sys
import ollama,requests

#from langchain_community.document_loaders import PDFPlumberLoader
#from langchain_experimental.text_splitter import SemanticChunker
#from langchain.text_splitter import RecursiveCharacterTextSplitter  
#from langchain_community.embeddings import HuggingFaceEmbeddings 
#from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_openai.embeddings import OpenAIEmbeddings

#from langchain_community.vectorstores import FAISS  
#from langchain_community.llms import Ollama  

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



logging.basicConfig(level=logging.INFO)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

st.session_state.prompt_input = ""


def get_models() -> list:
    thelist = requests.get("http://127.0.0.1:11434/api/tags")
    jsondata = thelist.json()
    result = list()

    for model in jsondata["models"]:
        result.append(model["model"])

    return result


def handlePrompt():
	st.text_input("Chat Prompt: ", value="Who was Bill Clinton?",key="prompt_input", on_change=handlePromptResponse, args=None)
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

# Defining a function to create new messages with specified roles ('user' or 'assistant')
def create_message(message, role):
  return {
    'role': role,
    'content': message
  }


def handlePromptResponse():
	#//*** Called as Part of On_Change of st.text_input
	print("CALLBACK")

	#//*** Writes the Text_input value to the session state using the key prompt_input which is assign to st.text_input
	st.write(st.session_state.prompt_input)

	#//*** Pull the session_state
	prompt = st.session_state.prompt_input
	# generate an embedding for the prompt and retrieve the most relevant doc
	st.sidebar.write("Generating Response")
	# generate a response combining the prompt and data we retrieved in step 2
	#output = ollama.generate(
	#  model=g["model"],
	#  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
	#)
	# Calling the ollama API to get the assistant response
	ollama_response = ollama.chat(model=g['model'], stream=True, messages=st.session_state.chat_messages)

	# Preparing the assistant message by concatenating all received chunks from the API
	assistant_message = ''

	for chunk in ollama_response:
		assistant_message += chunk['message']['content']
		print(chunk['message']['content'], end='', flush=True)

	# Adding the finalized assistant message to the chat log
	st.session_state.chat_messages.append(create_message(assistant_message, 'assistant'))

	#print(output['response'])
	#st.info(output['response'])
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

	with open('whole_dashboard.txt', 'r', encoding='utf-8') as f:
		data = f.read()

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

	#//*** Build Active Models
	g['models'] = get_models()

	g['model'] = g['models'][0]
	print(g['models'])
	print(f"Active Model: {g['model']}")

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

	output = ollama.chat(
	  model=g["model"],
	  messages=[{'role': 'user', 'content' :"Using this data: {data}. Respond to this prompt: {prompt}"}]
	)

	for chunk in output:
  		print(chunk['message']['content'], end='', flush=True)


if __name__ == "__main__":
	main()