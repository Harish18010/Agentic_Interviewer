import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(temperature=0):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL ERROR: GROQ_API_KEY is missing in .env file.")
    
  
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=temperature,
        groq_api_key=api_key,
        max_retries=3
    )
    return llm