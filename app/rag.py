import os
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
TextLoader, PyPDFLoader)

from .config import OPENAI_API_KEY, RAG_DOCS_PATH, VECTOR_STORE_PATH



emb = OpenAIEmbeddings(model="text-embedding-3-large",
                            api_key=OPENAI_API_KEY)

def load_documents():
    docs = []
    for fname in os.listdir(RAG_DOCS_PATH):
        fpath = os.path.join(RAG_DOCS_PATH, fname)
        if fname.endswith('.pdf'):
            docs.extend(PyPDFLoader(fpath).load())
        elif fname.endswith('.txt'):
            docs.extend(TextLoader(fpath).load())
    return docs

def build_vectorstore():
    docs = load_documents()



    vectordb = Chroma(
        collection_name="docs",
        embedding_function=emb,
        persist_directory=VECTOR_STORE_PATH,
    )

    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128)
    splits = text_splitter.split_documents(docs)
    vectordb.add_documents(splits)

    return vectordb

def get_relevant_recipes(query, top_k=3):
    vectordb = Chroma(
        collection_name="docs",
        embedding_function=emb,
        persist_directory=VECTOR_STORE_PATH,
    )
    print("Number of documents in DB:", vectordb._collection.count(), flush=True)
    docs = vectordb.similarity_search(query, k=top_k)
    print("Docs similarity search:", docs, flush=True)
    return docs