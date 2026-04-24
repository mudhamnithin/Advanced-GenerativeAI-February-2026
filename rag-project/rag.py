from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

loader = PyPDFLoader("C:\Desktop\IT-B batch_20.pdf")
docs = loader.load()

split = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = split.split_documents(docs)

print("chunks:", len(chunks))

emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma.from_documents(chunks, emb, persist_directory="db")

print("stored")

ret = db.as_retriever(search_kwargs={"k":3})

while True:
    q = input("ask: ")
    docs =docs = ret.invoke(q)
    print("\nresult:\n")
    for d in docs:
        print(d.page_content)