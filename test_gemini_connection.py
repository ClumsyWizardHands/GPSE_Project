"""Test Gemini API connection"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Test Gemini connection
try:
    print("Testing Gemini API connection...")
    
    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Test with a simple query
    response = llm.invoke("Say hello and confirm you are Gemini 2.0 Flash")
    print(f"\nSuccess! Gemini responded: {response.content}")
    
except Exception as e:
    print(f"\nError connecting to Gemini: {str(e)}")
    print("\nPossible issues:")
    print("1. Check that your GOOGLE_API_KEY is valid")
    print("2. Ensure the API key has access to Gemini models")
    print("3. The model name might need to be 'gemini-2.0-flash' instead of 'gemini-2.0-flash-exp'")
