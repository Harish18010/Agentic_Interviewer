import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm(temperature=0):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL ERROR: GOOGLE_API_KEY is missing in .env file.")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=temperature, 
        google_api_key=api_key
    )
    return llm