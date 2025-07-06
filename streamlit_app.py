import streamlit as st
from datetime import datetime
import os
import logging
import requests
from dotenv import load_dotenv

from patent_crew import run_patent_analysis, test_model
from patent_search_tools import keyword_search, semantic_search, hybrid_search, iterative_search
from opensearch_client import get_opensearch_client
from embeddings import get_embedding

# Setup directories
os.makedirs("outputs/patent_analysis", exist_ok=True)
os.makedirs("outputs/logs", exist_ok=True)

# Setup logging
logging.basicConfig(
    filename='outputs/logs/patent_app_streamlit.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

load_dotenv()
st.set_page_config(page_title="Patent Innovation Predictor", page_icon="🔬", layout="centered")

# Fetch Ollama models for dropdowns
def get_ollama_models():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m.get("name") for m in models if m.get("name")]
    except:
        pass
    return []

ollama_models = get_ollama_models() or ["llama2", "llama3"]

# Title
st.markdown("""
    <style>
    .main {
        background-color: #f6f1ee;
    }
    </style>
    <h1 style='text-align: center; color: #005b96;'>🔋 Patent Innovation Predictor - Lithium Battery Tech</h1>
""", unsafe_allow_html=True)

# Sidebar Navigation
page = st.sidebar.selectbox("Choose Operation", [
    "Patent Trend Analysis",
    "Search Patents",
    "Iterative Exploration",
    "System Status",
    "Ollama Models"
])

if page == "Patent Trend Analysis":
    st.subheader("📊 Comprehensive Patent Trend Analysis")
    research_area = st.text_input("Enter research area:", "Lithium Battery")
    model_name = st.selectbox("Select Ollama model:", ollama_models)
    if st.button("Run Analysis"):
        if not test_model(model_name):
            st.error(f"Model '{model_name}' failed validation. Please try another.")
        else:
            with st.spinner("Analyzing patents..."):
                result = run_patent_analysis(research_area, model_name)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"outputs/patent_analysis/patent_analysis_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result)
                st.success("Analysis completed!")
                st.download_button("📄 Download Analysis Report", data=result, file_name=os.path.basename(filename))
                st.text_area("Analysis Summary", result[:1000] + ("..." if len(result) > 1000 else ""), height=300)

elif page == "Search Patents":
    st.subheader("🔍 Search Patents")
    query = st.text_input("Enter search query:")
    search_type = st.selectbox("Search type", ["Keyword", "Semantic", "Hybrid"])
    if st.button("Search") and query:
        try:
            if search_type == "Keyword":
                results = keyword_search(query)
            elif search_type == "Semantic":
                results = semantic_search(query)
            else:
                results = hybrid_search(query)

            st.success(f"Found {len(results)} results")
            for r in results:
                src = r.get("_source", {})
                st.markdown(f"**{src.get('title', 'No Title')}**")
                st.markdown(f"- 📅 Date: {src.get('publication_date', 'N/A')}\n- 🆔 ID: {src.get('patent_id', 'N/A')}\n- 📄 Abstract: {src.get('abstract', '')[:300]}...")
                st.markdown("---")
        except Exception as e:
            logging.exception("Search error")
            st.error(f"Search error: {e}")

elif page == "Iterative Exploration":
    st.subheader("🔁 Iterative Patent Exploration")
    query = st.text_input("Enter initial query:")
    steps = st.number_input("Number of refinement steps", min_value=1, max_value=10, value=3)
    if st.button("Explore") and query:
        with st.spinner("Running iterative search..."):
            try:
                results = iterative_search(query, refinement_steps=steps)
                st.success(f"Found {len(results)} results")
                for r in results:
                    src = r.get("_source", {})
                    st.markdown(f"**{src.get('title', 'No Title')}**")
                    st.markdown(f"- 📅 Date: {src.get('publication_date', 'N/A')}\n- 🆔 ID: {src.get('patent_id', 'N/A')}\n- 📄 Abstract: {src.get('abstract', '')[:300]}...")
                    st.markdown("---")
            except Exception as e:
                logging.exception("Iterative exploration error")
                st.error(f"Exploration error: {e}")

elif page == "System Status":
    st.subheader("🛠 System Status")
    try:
        client = get_opensearch_client("localhost", 9200)
        indices = client.cat.indices(format="json")
        st.success("OpenSearch Connection: OK")
        for index in indices:
            st.markdown(f"- **{index['index']}**: {index['docs.count']} documents")
    except Exception as e:
        logging.exception("OpenSearch error")
        st.error(f"OpenSearch Connection Failed: {e}")

    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            st.success("Ollama Connection: OK")
            st.markdown("**Available Models:**")
            for m in models:
                st.markdown(f"- {m.get('name', 'unknown')}")
        else:
            st.error(f"Ollama connection failed: {response.status_code}")
    except Exception as e:
        logging.exception("Ollama error")
        st.error(f"Ollama Connection Failed: {e}")

    try:
        emb = get_embedding("test")
        st.success(f"Embedding Model: OK (dimension: {len(emb)})")
    except Exception as e:
        logging.exception("Embedding error")
        st.error(f"Embedding Model Failed: {e}")

elif page == "Ollama Models":
    st.subheader("📦 Available Ollama Models")
    models = get_ollama_models()
    if models:
        st.markdown("**Models available in Ollama:**")
        st.selectbox("Choose a model to preview", models)
        for model in models:
            st.markdown(f"- **{model}**")
    else:
        st.warning("No models available or Ollama is not reachable.")
