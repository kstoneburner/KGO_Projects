#https://geniusdatascience.blogspot.com/2024/11/step-by-step-pdf-chatbots-with-langchain-and-ollama.html
#pip install langchain pymupdf huggingface-hub faiss-cpu sentence-transformers
#pip install --user langchain langchain-openai langchain-community langchain-chroma langchain-ollama streamlit pypdf chromadb pymupdf huggingface-hub faiss-cpu sentence-transformers pdfplumber langchain_experimental
#pip install -U langchain-huggingface
#pip install -U langchain_experimental langchain_openai


#ollama prompt: using python, how would I generate an ollama chatbot to query a pdf using a RAG
# https://ollama.com/blog/embedding-models
# https://blog.gptdevs.net/creating-advanced-retrieval-augmented-generation-rag-systems-using-ollama-and-embedding-models
# Search: https://duckduckgo.com/?t=ffab&q=ollama+generate+text+embeddings&ia=web
# Search: https://duckduckgo.com/?q=ollama+rag+persistent&t=ffab&ia=web
#https://apidog.com/blog/rag-deepseek-r1-ollama/
#https://medium.com/rahasak/build-rag-application-using-a-llm-running-on-local-computer-with-ollama-and-langchain-e6513853fda0
#https://how.wtf/how-to-use-chroma-db-step-by-step-guide.html

#//*** Lanchain Semantic Chunker (vs HuggingFace Chunker)
#//*** https://python.langchain.com/docs/how_to/semantic-chunker/

#semantic Chunker Description and Types
#//*** Semantic Chunking is the ideal form of chunking the data for Embeddings
#//*** That Requires Hugging Face Access or OpenAI Access.
#//*** Going with Recursive Chunking for now. Proper chunking helps to preserve the contextual
#//***
#//*** https://medium.com/the-ai-forum/semantic-chunking-for-rag-f4733025d5f5

#Flask
#https://levelup.gitconnected.com/build-a-complete-opensource-llm-rag-qa-chatbot-flask-server-dc7938239a6b


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
	"model" : "gemma3:1b",
	"model" : "mixtral",
	"model" : "gemma3:27b",
	"model" : "deepseek-r1:70b",
	"model" : "mxbai-embed-large",
}#//*** END global Settings

#//*** Make the embedding model the same as the model, to help with dimensionality
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

results = collection.get()

print(client.list_collections())
#print(results)

#//*** Check if File Exists in Chroma db
print(results.keys())

if "metadatas" in results.keys():
	for item in results["metadatas"]:
		if "source" in item.keys():
			if item["source"] not in db_files:
				db_files.append(item["source"])

print(db_files)
print(file_path)
#//*** Check if file to process already exists in the database. If No, Add PDF for Processing.
if file_path not in db_files:
	process_pdf = True

#//*** process_pdf if needed
if process_pdf:

	############################################################
	# Loads PDF into Plain Text Array. Separated by each page
	############################################################
	# Load PDF text  
	print("Begin Loader")
	loader = PDFPlumberLoader(file_path)  
	print("Begin Docs")
	#//*** Load PDF 
	documents = loader.load()  
	############################################################


	################################################
	# KGO has issue with HuggingFace as a source.
	################################################
	# Split text into semantic chunks  
	# text_splitter = SemanticChunker(HuggingFaceEmbeddings())  

	# OpenAI requires an API Key
	#text_splitter = SemanticChunker(OpenAIEmbeddings())


	#//*** Chunks whole pages with some overlap of previous chunk
	text_splitter = RecursiveCharacterTextSplitter(
	    chunk_size=1000,
	    chunk_overlap=100, 
	    length_function=len,
	    is_separator_regex=False
	)

	naive_chunks = text_splitter.split_documents(documents)


	print(naive_chunks)
	print(len(documents))
	print(len(naive_chunks))
	print("Storing Embeddings")

	for i, d in enumerate(naive_chunks[:10]):
		print("=========================")
		print(f"{i} - {d}")
		print(type(d))

	# store each document in a vector embedding database
	offset = 0;
	for i, d in enumerate(naive_chunks):
		print("=========================")
		print("=========================")
		print("=========================")
		print(f"{i} - {d.page_content}")
		
		if (len(d.page_content)) == 0:
			offset = offset + 1
			continue
		i = i - offset
		#print(str(len(documents)),str(i),str(len(d)),d)
		response = ollama.embeddings(model=g["embedding_model"], prompt=d.page_content)
		#embedding_dimensions = 256
		#response.set_embedding_dimensions(embedding_dimensions)
		#response = ollama.embeddings(model="mixtral", prompt=d.page_content)
		embedding = response["embedding"]
		collection.add(
			ids=[str(i)],
			embeddings=[embedding],
			metadatas=[d.metadata],
			documents=[d.page_content]
			)

#//**** Load AI
print("Load AI")
print("Prompting")

# an example prompt
prompt = "Summarize OGML"
#prompt = "What are the best things in life?"
prompt = "using OG Script Reference How would I configure a rosstalk listener in Dashboard?"

print("Prompt: ", prompt)

# generate an embedding for the prompt and retrieve the most relevant doc
response = ollama.embeddings(
  prompt=prompt,
  model=g["model"]
)

print("=== Response ----")
results = collection.query(
  query_embeddings=[response["embedding"]],
  n_results=1
)

data = results['documents'][0][0]

print(data)
print("Prompting")
#print(results['documents'][0][0])
#print(response)
#print(results)

# generate a response combining the prompt and data we retrieved in step 2
output = ollama.generate(
  model=g["model"],
  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
)

print(output['response'])



#//********************************************************************************
#//********************************************************************************
#//********************************************************************************
#//********************************************************************************

sys.exit()

#//*** Chunk the text. Using Naieve recursion. Semantic Chunking is Preferable.
text_pages = [whole_text]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100, 
    length_function=len,
    is_separator_regex=False
)
naive_chunks = text_splitter.split_documents(text_pages)
for chunk in naive_chunks:
	print("============")
	print(chunk.page_content+ "\n")



sys.exit()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False
)

#documents = text_splitter.split_documents(docs)

naive_chunks = text_splitter.split_documents(documents)

#//*** This Section displays the Text chunks. It kind of keeps the sentences together. It's definitely
#//*** Naive
for chunk in naive_chunks:
	print("============")
	print(chunk.page_content+ "\n")



sys.exit()
#//***********************************************************************
#//*** Load PDF as a Binary to cleanly remove the image references
#//*** Pile all the text into a single String. We'll use the chunker to
#//*** organize for context. Although Splitting by page isn't a bad
#//*** Way to Go
#//***********************************************************************
text_pages = []
with pdfplumber.open(file_path,unicode_norm="NFC") as pdf:
	for page in pdf.pages:
		print(".")
		encoded_line = page.extract_text().encode(encoding="utf-8", errors="ignore")
		decoded_line = encoded_line.decode(encoding="utf-8")

		decoded_line = re.sub("0x....\\W"," ", decoded_line)
		text_pages.append( decoded_line )

for page in text_pages:
	print("===================")
	print(page)








documents = text_pages
print("Storing Embeddings")

# store each document in a vector embedding database
offset = 0;
for i, d in enumerate(documents):
	if (len(d)) == 0:
		offset = offset + 1
		continue
	i = i - offset
	#print(str(len(documents)),str(i),str(len(d)),d)
	response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
	embedding = response["embedding"]
	collection.add(
		ids=[str(i)],
		embeddings=[embedding],
		documents=[d]
		)

print("Prompting")

# an example prompt
prompt = "Summarize OGML"

# generate an embedding for the prompt and retrieve the most relevant doc
response = ollama.embeddings(
  prompt=prompt,
  model="mxbai-embed-large"
)
results = collection.query(
  query_embeddings=[response["embedding"]],
  n_results=1
)
data = results['documents'][0][0]

print("Prompting")
print(results['documents'][0][0])

# generate a response combining the prompt and data we retrieved in step 2
output = ollama.generate(
  model="mixtral",
  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
)

print(output['response'])
sys.exit()