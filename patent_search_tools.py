from embeddings import get_embedding
from opensearch_client import get_opensearch_client

def keyword_search(query_text, top_k=20):
    """
    Peform query search using OpenSearch.
    
    Args:
        query_text (str): The query text to search for.
        top_k (int): Number of top results to return.
    
    Returns:
        list: A list of dictionaries containing search results.
    """
    client=get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        # Create a keyword search query
        search_query = {
            "size": top_k,
            "query": {"match": {"abstract": query_text}},
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }

        response = client.search(index=index_name, body=search_query)
        return response["hits"]["hits"]
    
    except Exception as e:
        print(f"Keyword search error: {e}")
        return []

