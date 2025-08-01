import os
import requests
from datetime import datetime
from crewai import Agent, Crew, Task, Process
from crewai.tools import BaseTool

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from opensearch_client import get_opensearch_client

# Checking Ollama model availability
def check_ollama_availability():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model.get("name") for model in models if model.get("name")]
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return []

# Testing the model with a simple prompt
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

# Custom tools by extending BaseTool from CrewAI
class SearchPatentsTool(BaseTool):
    name: str = "search_patents"
    description: str = "Search for patents matching a query"

    def _run(self, query: str = None, top_k: int = 20) -> str:
        if not query:
            return "Error: No query provided to SearchPatentsTool."
        client = get_opensearch_client("localhost", 9200)
        index_name = "patents"
        search_query = {
            "size": top_k,
            "query": {"bool": {"must": [{"match": {"abstract": query}}]}},
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }
        try:
            response = client.search(index=index_name, body=search_query)
            results = response["hits"]["hits"]
            formatted_results = []
            for i, hit in enumerate(results):
                source = hit["_source"]
                formatted_results.append(
                    f"{i+1}. Title: {source.get('title', 'N/A')}\n"
                    f"   Date: {source.get('publication_date', 'N/A')}\n"
                    f"   Patent ID: {source.get('patent_id', 'N/A')}\n"
                    f"   Abstract: {source.get('abstract', 'N/A')[:200]}...\n"
                )
            return "\n".join(formatted_results)
        except Exception as e:
            return f"Error searching patents: {str(e)}"

class SearchPatentsByDateRangeTool(BaseTool):
    name: str = "search_patents_by_date_range"
    description: str = "Search for patents in a specific date range"

    def _run(self, query: str = None, start_date: str = None, end_date: str = None, top_k: int = 30) -> str:
        if not query or not start_date or not end_date:
            return "Error: query, start_date, and end_date are required for SearchPatentsByDateRangeTool."
        client = get_opensearch_client("localhost", 9200)
        index_name = "patents"
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": [{"match": {"abstract": query}}],
                    "filter": [
                        {
                            "range": {
                                "publication_date": {"gte": start_date, "lte": end_date}
                            }
                        }
                    ],
                }
            },
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }
        try:
            response = client.search(index=index_name, body=search_query)
            results = response["hits"]["hits"]
            formatted_results = []
            for i, hit in enumerate(results):
                source = hit["_source"]
                formatted_results.append(
                    f"{i+1}. Title: {source.get('title', 'N/A')}\n"
                    f"   Date: {source.get('publication_date', 'N/A')}\n"
                    f"   Patent ID: {source.get('patent_id', 'N/A')}\n"
                    f"   Abstract: {source.get('abstract', 'N/A')[:200]}...\n"
                )
            return "\n".join(formatted_results)
        except Exception as e:
            return f"Error searching patents: {str(e)}"

class AnalyzePatentTrendsTool(BaseTool):
    name: str = "analyze_patent_trends"
    description: str = "Analyze patent trends in patent data"

    def _run(self, patents_data: str = None) -> str:
        if not patents_data:
            return "Error: No patent data provided to AnalyzePatentTrendsTool."
        return f"Analysis of patent trends: {patents_data}"


# Agent setup
def create_patent_analysis_crew(model_name="llama2:latest", research_area="Lithium Battery"):
    """
    Create a CrewAI crew for patent analysis using Ollama.

    Args:
        model_name (str): name of the ollama model to be used
        research_area (str): research area for analysis
    
    Returns:
        Crew: A CrewAI crew instance configured for patent analysis
    """

    # Checking if the model exists in Ollama
    available_models = check_ollama_availability()
    if not available_models:
        raise ValueError("No available models found in Ollama. Please ensure Ollama is running and models are installed.")

    # Testing model
    if not test_model(model_name):
        raise ValueError(f"Model '{model_name}' is not working. Please check the model or pull it manually.")

    print("Model found and tested successfully.")

    # Fixing the model format by adding the 'ollama/' prefix
    if not model_name.startswith("ollama/"):
        model_name = f"ollama/{model_name}"

    llm = OllamaLLM(model=model_name, temperature=0.2)

    # Creating tools using CrewAI's BaseTool subclasses
    tools = [
        SearchPatentsTool(),
        SearchPatentsByDateRangeTool(),
        AnalyzePatentTrendsTool()
    ]

    # Create agents
    research_director = Agent(
        role="Research Director",
        goal=f"Coordinate research efforts and define the scope of patent analysis for {research_area}",
        backstory="You are an experienced research director who specializes in technological innovation analysis.",
        verbose=True,
        allow_delegation=True,
        llm=llm,
        tools=tools
    )

    patent_retriever = Agent(
        role="Patent Retriever",
        goal=f"Find and retrieve the most relevant patents related to the research area: {research_area}",
        backstory="You are a specialized patent researcher with expertise in information retrieval systems.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=tools,
    )

    data_analyst = Agent(
        role="Patent Data Analyst",
        goal=f"Analyze patent data to identify trends, patterns, and emerging technologies in {research_area}",
        backstory="You are a data scientist specializing in patent analysis with years of experience in technology forecasting.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=tools,
    )

    innovation_forecaster = Agent(
        role="Innovation Forecaster",
        goal=f"Predict future innovations and technologies based on patent trends in {research_area}",
        backstory="You are an expert in technological forecasting with a track record of accurate predictions in emerging technologies.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=tools,
    )

    # Creating tasks with research_area injected
    task1 = Task(
        description=f"""
        Define a research plan for the patents area: {research_area}
        1. Key technology areas to focus on
        2. Time periods for analysis (focus on last 3 years)
        3. Specific technological aspects to analyze
        """,
        expected_output=f"A research plan for {research_area} with focus areas, time periods, and key technological aspects.",
        agent=research_director,
    )

    task2 = Task(
        description=f"""
        Using the research plan, retrieve patents related to {research_area} from the last 3 years.
        Use the search_patents and search_patents_by_date_range tools to gather comprehensive data.
        Focus on the most relevant and innovative patents.
        Group patents by sub-technologies within {research_area}.
        Provide a summary of the retrieved patents, including:
        - Total number of patents found
        - Key companies/assignees
        - Main technological categories
        """,
        expected_output=f"""A comprehensive patent retrieval report for {research_area} containing:
        - Summary of total patents found
        - List of key patents grouped by sub-technology
        - Analysis of top companies/assignees
        - Overview of main technological categories
        - List of the most innovative patents with summaries
        """,
        agent=patent_retriever,
        dependencies=[task1],
    )

    task3 = Task(
        description=f"""
        Analyze the retrieved patent data for {research_area} to identify trends and patterns:
        1. Identify growing vs. declining areas of innovation
        2. Analyze technology evolution over time
        3. Identify key companies and their focus areas
        4. Determine emerging sub-technologies within {research_area}
        5. Analyze patent claims to understand technological improvements
        
        Create a comprehensive analysis with specific trends, supported by data.
        """,
        expected_output=f"""A trend analysis report for {research_area} containing:
        - Identification of growing vs. declining technology areas
        - Timeline of technology evolution
        - Company focus analysis
        - Emerging sub-technologies list
        - Technical improvement trends
        - Data-backed conclusions on innovation patterns
        """,
        agent=data_analyst,
        dependencies=[task2],
    )

    task4 = Task(
        description=f"""
        Based on the patent analysis, predict future innovations in {research_area}:
        1. Identify technologies likely to see breakthroughs in the next 2-3 years
        2. Recommend specific areas for R&D investment
        3. Predict which companies are positioned to lead innovation
        4. Identify potential disruptive technologies
        5. Outline specific technical improvements likely to emerge
        
        Create a detailed forecast with specific technology predictions and justification.
        """,
        expected_output=f"""A future innovation forecast for {research_area} containing:
        - Predicted breakthrough technologies for next 2-3 years
        - Prioritized list of R&D investment areas
        - Companies likely to lead future innovation
        - Potential disruptive technologies and their impact
        - Timeline of expected technical improvements
        - Justification for all predictions based on patent data
        """,
        agent=innovation_forecaster,
        dependencies=[task3],
    )

    # Create the crew and enabling debugging
    crew = Crew(
        agents=[
            research_director,
            patent_retriever,
            data_analyst,
            innovation_forecaster,
        ],
        tasks=[task1, task2, task3, task4],
        verbose=True,
        process=Process.sequential,
        cache=False,
    )

    return crew


def run_patent_analysis(research_area, model_name="llama2:latest"):
    """
    Run the patent analysis crew for the specified research area.

    Args:
        research_area (str): The research area to analyze
        model_name (str): Ollama model to use

    Returns:
        str: Analysis results
    """
    try:
        crew = create_patent_analysis_crew(model_name, research_area)
        result = crew.kickoff(inputs={"research_area": research_area})

        # Extract the string output from the CrewOutput object
        if hasattr(result, "output"):
            # CrewAI storing results in the 'output' attribute
            return result.output
        elif hasattr(result, "result"):
            # Some versions might are using 'result'
            return result.result
        else:
            # Converting to string
            return str(result)
    except Exception as e:
        return (
            f"Analysis failed: {str(e)}\n\nTroubleshooting tips:\n"
            + "1. Make sure Ollama is running: 'ollama serve'\n"
            + "2. Pull a compatible model: 'ollama pull llama2:latest' or 'ollama pull mistral'\n"
            + "3. Check Ollama logs for errors\n"
            + "4. Try a simpler model or reduce task complexity"
        )

if __name__ == "__main__":
    print("\n============================")
    print("  PATENT ANALYSIS TOOL")
    print("============================\n")

    # 1. Research area input
    research_area = input("Enter the research area to analyze: ").strip()
    if not research_area:
        research_area = "Lithium Battery"

    # 2. Fetch available models dynamically
    models = check_ollama_availability()
    if not models:
        print("❌ No models found in Ollama. Make sure 'ollama serve' is running and models are pulled.")
        exit()

    print("\n📦 Available Ollama Models:")
    for idx, model in enumerate(models):
        print(f"  {idx + 1}. {model}")

    # 3. Prompt user to select one
    selected_index = input(f"\nSelect a model (1-{len(models)}): ").strip()
    if not selected_index.isdigit() or int(selected_index) not in range(1, len(models) + 1):
        print("❌ Invalid selection. Using default model: llama2")
        model_name = "llama2"
    else:
        model_name = models[int(selected_index) - 1]

    # 4. Run the crew-based analysis
    result = run_patent_analysis(research_area, model_name)

    # 5. Save results in organized folder
    from pathlib import Path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = Path("outputs/patent_analysis")
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / f"patent_analysis_{timestamp}.txt"

    # Ensure result is string before writing
    if not isinstance(result, str):
        result = str(result)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"\n✅ Analysis completed and saved to {file_path.resolve()}")