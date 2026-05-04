# routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# --- THE FIX: Grab the API key explicitly at the top level ---
my_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not my_api_key:
    print("❌ CRITICAL ERROR: Could not find GOOGLE_API_KEY in your .env file.")

# 1. Initialize Embeddings and connect to Pinecone (FORCE-FEEDING THE KEY)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-2",
    google_api_key=my_api_key,
    output_dimensionality=3072
)
index_name = "potatocare"

try:
    # Connect to the existing Pinecone index
    vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 most relevant chunks
except Exception as e:
    print(f"Warning: Failed to connect to Pinecone. {e}")
    retriever = None

# 2. Initialize Gemini 1.5 Flash (FORCE-FEEDING THE KEY)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.3,
    google_api_key=my_api_key
)

# 3. Create the System Prompt
system_prompt = (
    "You are an expert Agronomist AI for the PotatoCare platform. "
    "Use the following pieces of retrieved scientific context to answer the farmer's question. "
    "If the context does not contain the answer, rely on your general agricultural knowledge, "
    "but state clearly that you are doing so. Keep the answer professional, concise, and actionable.\n\n"
    "important : give output in text not markdown format and avoid using any markdown syntax in the answer and also avoid using any headers or footers in the answer and also avoid using any bullet points or numbered lists in the answer and also avoid using or dont give text more than 50 words\n\n"
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# 4. Build the RAG Chain
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

@router.post("/chat")
async def get_chat_response(req: ChatRequest):
    if not retriever:
        raise HTTPException(status_code=500, detail="Vector database not connected.")
    
    try:
        # Invoke the chain
        response = rag_chain.invoke({"input": req.message})
        return {"reply": response["answer"]}
    except Exception as e:
        # ADD THIS PRINT STATEMENT:
        print(f"❌ CRASH DETAILS: {str(e)}") 
        raise HTTPException(status_code=500, detail=str(e))