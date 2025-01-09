########################################################################################################################################
### Source Documents
########################################################################################################################################
### https://medium.com/@harjot802/building-a-local-pdf-chat-application-with-mistral-7b-llm-langchain-ollama-and-streamlit-67b314fbab57
########################################################################################################################################
########################################################################################################################################
### Dependencies
########################################################################################################################################
#pip install --user langchain langchain-openai langchain-community langchain-chroma langchain-ollama langchain-ollama streamlit pypdf chromadb
########################################################################################################################################

#//*** Clear the Command Line
import os
os.system('cls')


from langchain import hub
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
#from langchain.llms import Ollama
#from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM

#from langchain.embeddings.ollama import OllamaEmbeddings
#from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings

#from langchain.vectorstores import Chroma
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import streamlit as st

import time, sys

model_type = "llama3.2"

print("Hola!")


###########################################################################################################
# Load the document and split the documents into chunks before embedding them in your vector database. 
# I chose chunk size of 1500 tokens. You can change this to fit your specific use-case.
###########################################################################################################
#print("Tokenizing PDF")
#loader = PyPDFLoader("DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf")
#data = loader.load()

#text_splitter = RecursiveCharacterTextSplitter(
#    chunk_size=1500, chunk_overlap=100)
#all_splits = text_splitter.split_documents(data)

###########################################################################################################
# Persist database to your disc to save it using vectorstore.persist() 
# so that you don’t have preprocess the document everytime.
###########################################################################################################

persist_directory = 'jj'

print("") 
#vectorstore = Chroma.from_documents(
#    documents=all_splits, embedding=OllamaEmbeddings(model="llama3.2"),persist_directory=persist_directory)

#vectorstore.persist()

###########################################################################################################
# After saving, you can choose the persistence directory and load it from the disk. 
# Now we can load the persisted database from disk, and use it as normal. 
# Remember to choose the same embedding model as before.
###########################################################################################################
vectorstore = Chroma(persist_directory=persist_directory,
                  embedding_function=OllamaEmbeddings(model=model_type)
                  )

###########################################################################################################
# Now initialize the llm and create a retriever
###########################################################################################################
#llm = OllamaLLM(base_url="http://localhost:11434",
#                                  model=model_type,
#                                  verbose=True,
#                                  callback_manager=CallbackManager(
#                                      [StreamingStdOutCallbackHandler()])
#                                  )

#retriever = vectorstore.as_retriever()

#uploaded_file = st.file_uploader("DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf", type='pdf')

print("Tokenizing PDF")
loader = PyPDFLoader("DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf")
data = loader.load()

print("Vectorizing PDF")
# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    length_function=len
)

print("Splitting Document")
all_splits = text_splitter.split_documents(data)

print("Create VectorStore")

persist_directory = 'jj'

vectorstore = Chroma.from_documents(
    documents=all_splits, embedding=OllamaEmbeddings(model=model_type),persist_directory=persist_directory)

vectorstore.persist()

#//*** Quiting with a Cached Vector...Hopefully
sys.exit()
# Create and persist the vector store
st.session_state.vectorstore = Chroma.from_documents(
    documents=all_splits,
    embedding=OllamaEmbeddings(model="llama3.2")
)

print("VectorStore Persist")
st.session_state.vectorstore.persist()

print("Moving On....")

if 'retriever' not in st.session_state:
	st.session_state.retriever = vectorstore.as_retriever()

###########################################################################################################
# Conversation buffer memory is used to maintain a history of chats so that the LLM can also reffer to the previous chats in the prompt.
# Intializing Conversation buffer memory and prompt template.
###########################################################################################################

template = """
    You are a knowledgeable chatbot, here to help with questions of the user. Your tone should be professional and informative.
    
    Context: {context}
    History: {history}

    User: {question}
    Chatbot:"" 
    """
prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=template,
    )

memory = ConversationBufferMemory(
        memory_key="history",
        return_messages=True,
        input_key="question"
    )

# Initialize the chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'prompt' not in st.session_state:
    st.session_state.prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=template,
    )

# Initialize the memory for conversation history
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="history",
        return_messages=True,
        input_key="question"
    )

# Initialize the vector store for document embeddings
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = Chroma(persist_directory='jj',
                                          embedding_function=OllamaEmbeddings(
                                              model="llama3.2")
                                          )

# Initialize the Ollama large language model (LLM)
if 'llm' not in st.session_state:
    st.session_state.llm = OllamaLLM(base_url="http://localhost:11434",
                                  model="llama3.2",
                                  verbose=True,
                                  callback_manager=CallbackManager(
                                      [StreamingStdOutCallbackHandler()]) )

###########################################################################################################
# Creating a Q&A Chain:
###########################################################################################################

qa_chain = RetrievalQA.from_chain_type(
            llm=st.session_state.llm,
            chain_type='stuff',
            retriever=st.session_state.retriever,
            verbose=True,
            chain_type_kwargs={
                "verbose": True,
                "prompt": prompt,
                "memory": memory,
            }
        )
###########################################################################################################
# Now u can just query the llm directly:
###########################################################################################################
while True:
    query = input("Ask a question: ")
    response = qa_chain(query)

print("Mi Dora!")