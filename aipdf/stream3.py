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
	"run_once" : True,
	"model" : "llama3.2",
	"model" : "deepseek-r1:1.5b",
	"model" : "deepseek-r1:70b",
	"model" : "gemma3:1b",
	"model" : "mixtral",
}#//*** END global Settings



logging.basicConfig(level=logging.INFO)

#//*** initialize Session State Lists
for x in ['messages','chat_messages']:
	if x not in st.session_state:
		st.session_state[x]	= []

#//*** initialize Session State Strings
for x in ['prompt_input','streaming_message','whole_chat_text']:
	if x not in st.session_state:
		st.session_state[x]	= ""
if "run_once" not in st.session_state:
	st.session_state.run_once = True

if st.session_state.run_once:
	text_input_container = st.container(border=True)
	response_container = st.container(border=True)

def get_models() -> list:
    thelist = requests.get("http://127.0.0.1:11434/api/tags")
    jsondata = thelist.json()
    result = list()

    for model in jsondata["models"]:
        result.append(model["model"])

    return result



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
	st.write(st.session_state.prompt_input,key="prompt_input")

	#//*** Pull the session_state
	prompt = st.session_state.prompt_input
	# generate an embedding for the prompt and retrieve the most relevant doc
	st.sidebar.write("Generating Response")
	# generate a response combining the prompt and data we retrieved in step 2
	#output = ollama.generate(
	#  model=g["model"],
	#  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
	#)
	#//*** Add the Message to the Chat History
	st.session_state.chat_messages.append(
    	create_message(prompt, 'user')
  	)
	# Calling the ollama API to get the assistant response
	ollama_response = ollama.chat(model=g['model'], stream=True, messages=st.session_state.chat_messages)
	
	# Preparing the assistant message by concatenating all received chunks from the API
	st.session_state.streaming_message = f"***{st.session_state.prompt_input}***  "
	st.session_state.assistant_message = ""
	print(f"QUESTION: {st.session_state.prompt_input}")
	response_container = st.empty()
	for chunk in ollama_response:
		#//*** Goes to the Screen
		st.session_state.streaming_message += chunk['message']['content']
		
		#//*** Goes to the Chat History
		st.session_state.assistant_message += chunk['message']['content']
		print(chunk['message']['content'], end='', flush=True)
		
		response_container.write(st.session_state.streaming_message)


	# Adding the finalized assistant message to the chat log
	st.session_state.chat_messages.append(create_message(st.session_state.assistant_message, 'assistant'))
	print(st.session_state.chat_messages)
	#print(output['response'])
	#st.info(output['response'])
	print("END Response")

	#handlePrompt(handlePromptResponse)



def main():

	if st.session_state.run_once:
		print(st.session_state.run_once)
		st.session_state.run_once = False
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
		#prompt = "Summarize OGML"
		#prompt = "What are the best things in life?"
		prompt = "using OG Script Reference How would I configure a rosstalk listener in Dashboard?"
		text_input_container.text_input("Generate Prompt: ", value="Summarize OGML",key="prompt_input", on_change=handlePromptResponse, args=None)
		
		#response_container.write("___")
		


		#print("Prompt: ", prompt)

		print("END MAIN")


if __name__ == "__main__":
	main()