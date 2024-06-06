import json
import os
from time import sleep
import asyncio
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
import torch
from transformers import AutoTokenizer, AutoModel
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from huggingface_hub import login


def load_unique_references_json(base_path):
    # Load the json the points to all the files that will be in our document store
    files_to_load_json = f"{base_path}/unique_references.json"

    # Read the JSON data from the file
    with open(files_to_load_json, 'r') as file:
        unique_references = json.load(file)

    # Print the loaded data (or process it as needed)
    print(json.dumps(unique_references, indent=4))
    return unique_references

# A simple function to load the text files and add the title as meta data
async def load_doc(doc_meta, base_path):
    if doc_meta['pmcid'] != 0:
        doc_file_nm = f"{base_path}/PMC{doc_meta['pmcid']}.txt"
        url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{doc_meta['pmcid']}/"
    else:
        doc_file_nm = f"{base_path}/PM{doc_meta['pmid']}.txt"
        url = f"https://pubmed.ncbi.nlm.nih.gov/{doc_meta['pmid']}/"
        
    loader = TextLoader(doc_file_nm)
    documents = loader.load()
    document = documents[0] # Expect onlt one doc
    document.metadata['title'] = doc_meta['title']
    document.metadata['url'] = url
    return document


def get_embeddings_model():
    # Load the tokenizer and model from Hugging Face
    model_name = 'mistralai/Mistral-7B-Instruct-v0.2'
    max_length = 2048

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModel.from_pretrained(model_name)

    # Define a function to generate embeddings
    def get_embeddings(texts):
        inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Taking the mean of the hidden states
        return embeddings

    # Create a HuggingFaceEmbeddings class with the custom model
    class CustomHuggingFaceEmbeddings(HuggingFaceEmbeddings):
        def embed_documents(self, texts):
            return get_embeddings(texts).tolist()

        def embed_query(self, text):
            return get_embeddings([text])[0].tolist()

    # Initialize the custom embeddings model
    embedding_model = CustomHuggingFaceEmbeddings()    
    return embedding_model


    
async def main():
    base_path = "/Users/dan/Code/Python/pub_worm/notebooks/output"
    unique_references = load_unique_references_json(base_path)
    documents = await asyncio.gather(*[load_doc(doc_meta, base_path) for doc_meta in unique_references.values()])
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunked_documents = text_splitter.split_documents(documents)


    embedding_model = get_embeddings_model()
    print("Starting load of model")
    db = await FAISS.afrom_documents(chunked_documents, embedding_model)
    print("Finishing load of model")
    db.save_local("./data/faiss_index")

if __name__ == "__main__":
    login(token = os.environ['HUGGINGFACEHUB_API_TOKEN'] )

    asyncio.run(main())