import streamlit as st
from llama_index.core.llms import ChatMessage
import logging
import time

import pdfplumber, os, re, sys
import ollama,requests

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter  
#from langchain_community.embeddings import HuggingFaceEmbeddings 
#from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_community.vectorstores import FAISS  
from langchain_community.llms import Ollama  

# Initializing an empty list for storing the chat messages and setting up the initial system message
chat_messages = []
system_message='You are a helpful assistant.'

# Defining a function to create new messages with specified roles ('user' or 'assistant')
def create_message(message, role):
  return {
    'role': role,
    'content': message
  }

# Starting the main conversation loop
def chat():
  # Calling the ollama API to get the assistant response
  ollama_response = ollama.chat(model='mistral', stream=True, messages=chat_messages)

  # Preparing the assistant message by concatenating all received chunks from the API
  assistant_message = ''
  for chunk in ollama_response:
    assistant_message += chunk['message']['content']
    print(chunk['message']['content'], end='', flush=True)
    
  # Adding the finalized assistant message to the chat log
  chat_messages.append(create_message(assistant_message, 'assistant'))

# Function for asking questions - appending user messages to the chat logs before starting the `chat()` function
def ask(message):
  chat_messages.append(
    create_message(message, 'user')
  )
  print(f'\n\n--{message}--\n\n')
  chat()

# Sending two example requests using the defined `ask()` function
#ask('Please list the 20 largest cities in the world.')
#ask('How many of the cities listed are in South America?')




def get_models() -> list:
    thelist = requests.get("http://127.0.0.1:11434/api/tags")
    jsondata = thelist.json()
    result = list()

    for model in jsondata["models"]:
        result.append(model["model"])

    return result

print(get_models())