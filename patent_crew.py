import os
import requests
from datetime import datetime, timedelta

# CrewAI and imports from crewai.tools
from crewai import Agent, Crew, Task, Process
from crewai.tools import BaseTool

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from opensearch_client import get_opensearch_client

# Check Ollama model availability
def check_ollama_availability():
    # Check if the Ollama model is available and return the model name
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models=response.json().get("models", [])
        return [model.get("name") for model in models if model.get("name")]
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Checking Ollama model availability...\n")
    available_models = check_ollama_availability()
    
    if available_models:
        print("✅ Ollama models available:")
        for model in available_models:
            print(f" - {model}")
    else:
        print("❌ No Ollama models found or Ollama is not running.")