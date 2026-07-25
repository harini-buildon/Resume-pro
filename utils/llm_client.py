"""
utils/llm_client.py – Google GenAI Client Initialization
======================================================
Provides a centralized client for interacting with the Google Gemini API.
"""

import os
import json
from google import genai
from google.genai import types

def get_gemini_client():
    """
    Returns a configured Gemini client if the API key is present, otherwise None.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return None

def generate_json(prompt, system_instruction=None):
    """
    Helper function to generate structured JSON using Gemini 2.5 Flash.
    """
    client = get_gemini_client()
    if not client:
        return None

    try:
        config_kwargs = {
            "response_mime_type": "application/json",
            "temperature": 0.7
        }
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs)
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API Error (JSON): {e}")
        return None

def generate_text(prompt, system_instruction=None):
    """
    Helper function to generate raw text using Gemini 2.5 Flash.
    """
    client = get_gemini_client()
    if not client:
        return None

    try:
        config_kwargs = {
            "temperature": 0.7
        }
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs)
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error (Text): {e}")
        return None
