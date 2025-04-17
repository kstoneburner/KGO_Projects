#//*** Python Streamlit Application Example
#//*** https://medium.com/@anoopjohny2000/building-a-llama-3-1-8b-streamlit-chat-app-with-local-llms-a-step-by-step-guide-using-ollama-749931de216a

#//*** Cookie Manager Docs
#https://pypi.org/project/st-cookies-manager/

#You are a conversation partner with Gemma3. Please provide an estimate of the current token count used in our conversation. Focus on the number of tokens, not the specific words. Aim for a concise answer – a number is fine

#Models:
# Wizard-vicuna-uncensored:7b:13B
# deepcoder
# wizardlm-uncensored
# dolphin-mistral
# dolphincoder
# DeepSeek-R1-Distill-Qwen-7B-uncensored



#// python -m streamlit run stream4.py


import streamlit as st
from streamlit import components

#from llama_index.core.llms import ChatMessage
import logging
import time
import secrets
import string

import pdfplumber, os, re, sys
import ollama,requests,json, io
from streamlit_float import *

# Float feature initialization
float_init()

from st_cookies_manager import EncryptedCookieManager



print()

#//*** Global Settings
g = {
	"path" : {
		"chroma" : "persistent_document_db",
		"pdf" : "./pdf",
	},
	"options" : {
		"num_ctx" : 4096,
		"num_ctx" : 2048,
		},
	"cookies" : None,
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

text_input_container = st.container(border=False)

#css = float_css_helper(bottom="0")
#text_input_container.float(css)

response_container = st.container(border=False)
response_container = st.empty()

chat_container = st.container(border=False)
#chat_container.write(st.session_state.whole_chat_text)

def initCookies():

	#//*** Build Secure Password as needed
	if "COOKIES_PASSWORD" not in os.environ:
		alphabet = string.ascii_letters + string.digits
		password = ''.join(secrets.choice(alphabet) for i in range(20))  # for a 20-character password
		os.environ["COOKIES_PASSWORD"] = password
	
	g['cookies'] = EncryptedCookieManager(
    # This prefix will get added to all your cookie names.
    # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
    prefix="ktosiek/st-cookies-manager/",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password=os.environ.get("COOKIES_PASSWORD"),
)
#if not g['cookies'].ready():
    # Wait for the component to load and send us current cookies.
#    st.stop()


def get_models() -> list:
    thelist = requests.get("http://127.0.0.1:11434/api/tags")
    jsondata = thelist.json()
    result = list()

    for model in jsondata["models"]:

    	if "mxbai-embed-large" in model["model"]:
    		continue
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
	def handleStop():
		stop = True
	#//*** Called as Part of On_Change of st.text_input
	print("CALLBACK")
	stop = False
	
	#//*** Writes the Text_input value to the session state using the key prompt_input which is assign to st.text_input
	#st.write(st.session_state.prompt_input,key="prompt_input")

	#//*** Pull the session_state
	prompt = st.session_state.prompt_input
	# generate an embedding for the prompt and retrieve the most relevant doc
	st.sidebar.button('Stop',on_click=handleStop())

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
	ollama_response = ollama.chat(model=g['model'], options=g['options'], stream=True, messages=st.session_state.chat_messages)
	
	# Preparing the assistant message by concatenating all received chunks from the API
	st.session_state.streaming_message = f"***{st.session_state.prompt_input}***\n\r"
	st.session_state.assistant_message = ""
	print(f"QUESTION: {st.session_state.prompt_input}")
	#response_container = st.empty()
	for chunk in ollama_response:
		#//*** Goes to the Screen
		st.session_state.streaming_message += chunk['message']['content']
		
		#//*** Goes to the Chat History
		st.session_state.assistant_message += chunk['message']['content']
		print(chunk['message']['content'], end='', flush=True)
		
		response_container.write(st.session_state.streaming_message)

		if stop:
			return


	# Adding the finalized assistant message to the chat log
	st.session_state.chat_messages.append(create_message(st.session_state.assistant_message, 'assistant'))
	print(st.session_state.chat_messages)
	

	st.session_state.whole_chat_text = st.session_state.streaming_message + "\n\r" + "---" + "\n\r" + st.session_state.whole_chat_text 
	#print(output['response'])
	#st.info(output['response'])
	print("END Response")

	#handlePrompt(handlePromptResponse)

def handleSelectbox():
	st.write(st.session_state['model'])
	g['cookies']['model'] = st.session_state['model']
	g['cookies'].save()
	g['model'] = st.session_state['model']
	print("Cookie: " + g['cookies']['model'])
	print("DONG")

def handleUpload():
		
		print("Handle Upload")

		#st.write(st.session_state['upload'])

		uploaded_file = st.session_state['upload']

		if uploaded_file == None:
			st.session_state.chat_messages = []
			st.session_state.whole_chat_text = ""
			return

		if uploaded_file.type == "application/json":
			#//*** Validate JSON for Chat History
			data = json.loads(uploaded_file.getvalue().decode('utf-8'))
		if 'type' in data.keys():
			if data['type'] == 'chat-history':
				st.session_state.assistant_message = data['chat']

				st.session_state.chat_messages = data['chat']


				for msg in st.session_state.assistant_message:
					if msg['role'] == 'user':
						st.session_state.whole_chat_text += f"\n\r**{msg['content']}**\n\r"
					if msg['role'] == 'assistant':
						st.session_state.whole_chat_text += msg['content'] + "\n\r"

				#chat_container.write(st.session_state.whole_chat_text)
				

def buildExport():
	data = {
		'type' : 'chat-history',
		'model' : g['model'],
		'chat' : st.session_state.chat_messages
	}
	data = json.dumps(data)
	print(data)
	return data
def main():

	initCookies()

	if not g['cookies'].ready():
	    # Wait for the component to load and send us current cookies.
	    st.stop()
	print(st.session_state.run_once)
	st.session_state.run_once = False
	print("Hello World")

	#//*** Build Active Models
	g['models'] = get_models()


	default = 0
	#//*** Model Cookie Not Found, Default to First Value in SelectBox
	if 'model' not in g['cookies']:
		g['cookies']['model'] = g['models'][0]
		g['cookies'].save()
	else:
		if g['cookies']['model'] in g['models']:
			for counter,val in enumerate(g['models']):
				if g['cookies']['model'] == val:
					default = counter


	print(f"Default: {default}")

	#st.sidebar.button("Export", on_click=handle_export())
	
	selectbox = st.sidebar.selectbox("Model", g['models'],key='model', index=default, on_change=handleSelectbox)

	uploaded_file = st.sidebar.file_uploader("Import", type=".json", key='upload', on_change=handleUpload )
	
	#if uploaded_file is not None:
	#	handleUpload(uploaded_file)

	g['model'] = g['models'][0]
	g['model'] = selectbox


	print(g['models'])
	print(f"Active Model: {g['model']}")
	#print("Cookie: " + g['cookies']['model'])
	data = buildExport()

	st.sidebar.download_button(label="Export", data=data, mime="application/jsonl", file_name="llm_chat_history.json")
	

	st.sidebar.write("___")


	
	#//**** Load AI
	print("Load AI")
	print("Prompting")

	# an example prompt

	text_input_container.text_input("Generate Prompt: ", value="",key="prompt_input", on_change=handlePromptResponse, args=None)		
	

	#response_container.write("___")
	
	#chat_container.write(st.session_state.whole_chat_text)
	chat_container.write(f'''<div id="chat-container">{st.session_state.whole_chat_text}</div>''', unsafe_allow_html=True)


	#print("Prompt: ", prompt)

	print(f"Session State Length: {len(st.session_state)}" )
	print("END MAIN")


if __name__ == "__main__":
	main()