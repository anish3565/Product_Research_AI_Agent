import os
from datetime import datetime
import requests
import logging
from dotenv import load_dotenv

from opensearch_client import get_opensearch_client
from patent_crew import run_patent_analysis, test_model, check_ollama_availability
from patent_search_tools import hybrid_search, iterative_search, semantic_search, keyword_search

# Setup directories
BASE_OUTPUT_DIR = "output"
LOG_DIR = os.path.join(BASE_OUTPUT_DIR, "logs")
RESULTS_DIR = os.path.join(BASE_OUTPUT_DIR, "patent_analysis")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOG_DIR, 'patent_app.log'),
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Utility: Display Main Menu
def display_menu():
    print("\n" + "=" * 60)
    print("  PATENT INNOVATION PREDICTOR - LITHIUM BATTERY TECHNOLOGY")
    print("=" * 60)
    print("1. Run complete patent trend analysis and forecasting")
    print("2. Search for specific patents")
    print("3. Iterative patent exploration")
    print("4. View system status")
    print("5. View available Ollama models")
    print("6. Exit")
    print("-" * 60)
    return input("Select an option (1-6): ")

# Utility: Display formatted search results
def display_patent_results(results, show_score=True):
    print(f"\nFound {len(results)} results:")
    print("-" * 60)
    for i, hit in enumerate(results):
        source = hit.get("_source", {})
        print(f"{i+1}. {source.get('title', 'No Title')}")
        if show_score:
            print(f"   Score: {hit.get('_score', 'N/A')}")
        print(f"   Date: {source.get('publication_date', 'N/A')}")
        print(f"   Patent ID: {source.get('patent_id', 'N/A')}")
        print(f"   Abstract: {source.get('abstract', '')[:150]}...")
        print("-" * 60)

# Option 1: Run Patent Analysis
def run_complete_analysis():
    print("\nRunning comprehensive patent analysis...")
    research_area = input("Enter research area (default: Lithium Battery): ") or "Lithium Battery"
    model_name = input("Enter the Ollama model to use (default: llama2): ") or "llama2"

    print(f"\nAnalyzing patents for: {research_area}")
    print(f"Using Ollama model: {model_name}")

    if not test_model(model_name):
        print(f"❌ Model '{model_name}' failed validation. Please try another.")
        return

    try:
        result = run_patent_analysis(research_area, model_name)
        if not isinstance(result, str):
            result = str(result)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(RESULTS_DIR, f"patent_analysis_{timestamp}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)

        print(f"\n✅ Analysis completed and saved to {filename}")
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("-" * 60)
        print(result[:500] + "...\n")

    except Exception as e:
        logging.exception("Error during patent analysis")
        print(f"❌ Error during analysis: {e}")

# Option 2: Search for Patents
def search_patents():
    print("\nPATENT SEARCH")
    print("-" * 60)
    query = input("Enter search query: ")
    if not query:
        print("Search query cannot be empty.")
        return

    search_type = input("Select search type (1: Keyword, 2: Semantic, 3: Hybrid) [3]: ") or "3"

    try:
        if search_type == "1":
            results = keyword_search(query)
        elif search_type == "2":
            results = semantic_search(query)
        else:
            results = hybrid_search(query)

        display_patent_results(results)

    except Exception as e:
        logging.exception("Search error")
        print(f"❌ Search error: {e}")

# Option 3: Iterative Exploration
def iterative_exploration():
    print("\nITERATIVE PATENT EXPLORATION")
    print("-" * 60)
    query = input("Enter initial exploration query: ")
    if not query:
        print("Query cannot be empty.")
        return

    steps = input("Number of exploration steps (default: 3): ")
    try:
        steps = int(steps) if steps else 3
    except:
        steps = 3

    try:
        results = iterative_search(query, refinement_steps=steps)
        display_patent_results(results, show_score=False)
    except Exception as e:
        logging.exception("Iterative search error")
        print(f"❌ Exploration error: {e}")

# Option 4: System Status
def check_system_status():
    print("\nSYSTEM STATUS")
    print("-" * 60)
    try:
        client = get_opensearch_client("localhost", 9200)
        indices = client.cat.indices(format="json")
        print("✅ OpenSearch connection: OK")
        for index in indices:
            print(f"   - {index['index']}: {index['docs.count']} documents")
    except Exception as e:
        logging.exception("OpenSearch status error")
        print(f"❌ OpenSearch connection: Failed - {e}")

    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama connection: OK")
            print(f"   Models: {', '.join([m.get('name', 'unknown') for m in models])}")
        else:
            print(f"❌ Ollama connection failed: {response.status_code}")
    except Exception as e:
        logging.exception("Ollama status error")
        print(f"❌ Ollama connection: Failed - {e}")

    try:
        from embeddings import get_embedding
        emb = get_embedding("test")
        print(f"✅ Embedding model: OK (dimension: {len(emb)})")
    except Exception as e:
        logging.exception("Embedding model error")
        print(f"❌ Embedding model: Failed - {e}")

    print("\nSystem is ready for operation.")

# Option 5: View Ollama Models
def list_ollama_models():
    print("\nAVAILABLE OLLAMA MODELS")
    print("-" * 60)
    try:
        models = check_ollama_availability()
        if models:
            for i, model in enumerate(models):
                print(f"{i+1}. {model}")
        else:
            print("No models found. Please ensure Ollama is running.")
    except Exception as e:
        logging.exception("Failed to fetch Ollama models")
        print(f"❌ Error fetching models: {e}")

# Main App Entry Point
def main():
    load_dotenv()
    while True:
        choice = display_menu()
        if choice == "1":
            run_complete_analysis()
        elif choice == "2":
            search_patents()
        elif choice == "3":
            iterative_exploration()
        elif choice == "4":
            check_system_status()
        elif choice == "5":
            list_ollama_models()
        elif choice == "6":
            print("\nExiting Patent Innovation Predictor. Goodbye!")
            break
        else:
            print("\nInvalid option. Please select a number between 1 and 6.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()