#https://geniusdatascience.blogspot.com/2024/11/step-by-step-pdf-chatbots-with-langchain-and-ollama.html
#pip install langchain pymupdf huggingface-hub faiss-cpu sentence-transformers

#ollama prompt: using python, how would I generate an ollama chatbot to query a pdf using a RAG
# https://ollama.com/blog/embedding-models
# https://blog.gptdevs.net/creating-advanced-retrieval-augmented-generation-rag-systems-using-ollama-and-embedding-models
# Search: https://duckduckgo.com/?t=ffab&q=ollama+generate+text+embeddings&ia=web
# Search: https://duckduckgo.com/?q=ollama+rag+persistent&t=ffab&ia=web
#https://apidog.com/blog/rag-deepseek-r1-ollama/
#https://medium.com/rahasak/build-rag-application-using-a-llm-running-on-local-computer-with-ollama-and-langchain-e6513853fda0
#https://how.wtf/how-to-use-chroma-db-step-by-step-guide.html


import pdfplumber, os, re, sys
import ollama,chromadb

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker  
from langchain_community.embeddings import HuggingFaceEmbeddings  
from langchain_community.vectorstores import FAISS  
from langchain_community.llms import Ollama  

#//*** Global Settings
g = {
	"path" : {
		"chroma" : "persistent_document_db",
		"pdf" : "./pdf"
	}
}#//*** END global Settings

file_path = "DashBoard_CustomPanel_Development_Guide_(8351DR-007).pdf"
collection_name = file_path.split(".")[0]
print(collection_name)

#//*** Spin up Chroma DB interfcae
#client = chromadb.Client() #<---  Memory only Client
client = chromadb.PersistentClient(path="pdfs") # <--- Save Documents to Disk
#collection = client.create_collection(name="docs")
#collection = client.get_or_create_collection(name="collection_name")

#results = collection.get()

print(client.list_collections())

# Load PDF text  
print("Begin Loader")
loader = PDFPlumberLoader(file_path)  
print("Begin Docs")
docs = loader.load()  

# Split text into semantic chunks  
text_splitter = SemanticChunker(HuggingFaceEmbeddings())  

documents = text_splitter.split_documents(docs)

print(documents)
sys.exit()



text_pages = []
with pdfplumber.open(file_path,unicode_norm="NFC") as pdf:
	for page in pdf.pages:
		print(".")
		encoded_line = page.extract_text().encode(encoding="utf-8", errors="ignore")
		decoded_line = encoded_line.decode(encoding="utf-8")

		decoded_line = re.sub("0x....\\W"," ", decoded_line)
		text_pages.append( decoded_line )

#for page in text_pages:
#	print("===================")
#	print(page)







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