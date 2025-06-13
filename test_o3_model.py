#!/usr/bin/env python3
"""
Test script to verify OpenAI o3 model is working
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

def test_o3_model():
    """Test the o3 model with a simple query"""
    print("Testing OpenAI o3 model...")
    
    # Use the o3-specific API key
    o3_api_key = os.getenv('OPENAI_API_KEY_O3')
    if not o3_api_key:
        print("Error: OPENAI_API_KEY_O3 not found in .env file")
        return False
        
    print(f"Using o3 API Key: {o3_api_key[:20]}...")
    
    try:
        # Initialize o3 model with the verified API key
        # Note: o3 only supports default temperature (1.0)
        llm = ChatOpenAI(
            model="o3",
            temperature=1.0,  # o3 requires default temperature
            max_tokens=100,
            openai_api_key=o3_api_key
        )
        
        # Simple test query
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Please respond with 'o3 model is working!' if you can process this message.")
        ]
        
        # Get response
        response = llm.invoke(messages)
        
        print("\nSuccess! Response from o3:")
        print(response.content)
        
        return True
        
    except Exception as e:
        print(f"\nError testing o3 model: {str(e)}")
        print("\nThis might mean:")
        print("1. The model name might be different (e.g., 'gpt-o3' or 'o3-preview')")
        print("2. The API key might not have access to this model")
        print("3. The model might require different parameters")
        
        return False

if __name__ == "__main__":
    test_o3_model()
