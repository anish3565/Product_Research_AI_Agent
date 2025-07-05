import os
import requests
from crewai import Agent, Crew, Task, Process
from crewai.tools import BaseTool

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from opensearch_client import get_opensearch_client

# Check Ollama model availability
def check_ollama_availability():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model.get("name") for model in models if model.get("name")]
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return []

# Test the model with a simple prompt
def test_model(model_name):
    try:
        llm = OllamaLLM(model=model_name, temperature=0.2)
        prompt = ChatPromptTemplate.from_template("Say Hello!")
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({})
        return bool(result)
    except Exception as e:
        if "404" in str(e):
            print(f"\n❌ Model '{model_name}' not found in Ollama. Attempting to pull it now...")
            pull_status = os.system(f"ollama pull {model_name}")
            if pull_status == 0:
                print(f"✅ Successfully pulled '{model_name}'. Retesting...")
                return test_model(model_name)
            else:
                print(f"❌ Failed to pull model '{model_name}'. Please pull it manually.")
        else:
            print(f"⚠️ Error testing model '{model_name}': {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Ollama model availability...\n")
    available_models = check_ollama_availability()

    if not available_models:
        print("❌ No models found. Please ensure Ollama is running and models are installed.")
        exit(1)

    print("✅ Available Ollama models:")
    for idx, model in enumerate(available_models, start=1):
        print(f" {idx}. {model}")

    selected_model = None
    while True:
        try:
            choice = input(f"\nEnter the model number to use [1-{len(available_models)}] or press Enter for default (1): ").strip()
            selected_model = available_models[0] if not choice else available_models[int(choice) - 1]

            print(f"\n🧠 Selected model: {selected_model}")

            if test_model(selected_model):
                print(f"\n✅ Model '{selected_model}' is working fine!")
                break
            else:
                print("❌ Try choosing another model.\n")
        except (ValueError, IndexError):
            print("⚠️ Invalid input. Please enter a valid number.")