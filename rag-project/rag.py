from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from langgraph.graph import StateGraph

# load pdf
loader = PyPDFLoader("batch_20.pdf")
docs = loader.load()
# chunk
split = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = split.split_documents(docs)

print("chunks:", len(chunks))

# embedding
emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# db
db = Chroma.from_documents(chunks, emb, persist_directory="db")

print("stored")

ret = db.as_retriever(search_kwargs={"k":3})

# process node
def process(s):
    q = s["q"]
    docs = ret.invoke(q)
    ctx = " ".join([d.page_content for d in docs])
    return {"q": q, "ctx": ctx}

# decision
def decide(s):
    if len(s["ctx"]) < 50:
        return "hitl"
    return "answer"

# hitl node
def hitl(s):
    return {"res": "Escalated to human support"}

# output node
def output(s):
    if "res" in s:
        print("\nanswer:", s["res"])
    else:
        print("\nresult:\n", s["ctx"])
    return s

# graph
g = StateGraph(dict)

g.add_node("process", process)
g.add_node("hitl", hitl)
g.add_node("output", output)

g.set_entry_point("process")

g.add_conditional_edges(
    "process",
    decide,
    {
        "answer": "output",
        "hitl": "hitl"
    }
)

g.add_edge("hitl", "output")

app = g.compile()

# run
while True:
    q = input("ask: ")
    app.invoke({"q": q})