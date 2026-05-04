import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

def ingest_all_pdfs():
    data_dir = "data/"
    
  
    my_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not my_api_key:
        print("❌ ERROR: Could not find your API key in the .env file. Please check your .env file.")
        return

   
    print("Connecting to Gemini...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=my_api_key
    )
    
    index_name = "potatocare"
    print("Connecting to Pinecone...")
    vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)

    # Look for all PDFs in the data folder
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_dir, filename)
            print(f"Processing: {filename}...")
            
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(docs)
            
            vector_store.add_documents(chunks)
            print(f"✅ Ingested {filename}")

if __name__ == "__main__":
    ingest_all_pdfs()