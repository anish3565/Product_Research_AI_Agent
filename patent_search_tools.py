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
        # Creating a keyword search query
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
    
def semantic_search(query_text, top_k=20):
    """
    Peform semantic search using vector embeddings.

    Args:
        query_text (str): The query text to search for.
        top_k (int): Number of results to return.
    
    Returns:
        list: A list of dictionaries containing search results.
    """
    client=get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        # Get the embedding for the query text
        query_embedding = get_embedding(query_text)

        # Creating a semantic search query
        search_query = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": top_k,
                    }
                }
            },
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }

        response = client.search(index=index_name, body=search_query)
        return response["hits"]["hits"]
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []


def hybrid_search(query_text, top_k=20):
    """
    Perform hybrid search using both keyword and semantic search.

    Args:
        query_text (str): The query text to search for.
        top_k (int): Number of results to return.
    
    Returns:
        list: A list of dictionaries containing search results.
    """
    client=get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        # Get the embedding for the query text
        query_embedding = get_embedding(query_text)

        # Creating a hybrid search query
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {"knn": {"embedding": {"vector": query_embedding, "k": top_k}}},
                        {"match": {"abstract": query_text}},
                    ]
                }
            },
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }
    except Exception as e:
        print(f"Hybrid search error: {e}")
        # Fall back to keyword search
        try:
            fallback_query = {
                "size": top_k,
                "query": {"match": {"abstract": query_text}},
                "_source": ["title", "abstract", "publication_date", "patent_id"],
            }
            response = client.search(index=index_name, body=fallback_query)
            return response["hits"]["hits"]
        except Exception as e2:
            print(f"Fallback search error: {e2}")
            return []



if __name__ == "__main__":
    query = "lithum battery"

    # # Perform keyword search
    # print("Keyword Search Results:")
    # keyword_results = keyword_search(query)
    # for result in keyword_results:
    #     print(result, end="\n\n")

    
    # # Perform semantic search
    # print("Semantic Search Results:")
    # semantic_results=semantic_search(query)
    # for result in semantic_results:
    #     print(result, end="\n\n")

    # Perform Hybrid Search
    print("Hybird Search Results:")
    hybrid_results = semantic_search(query)
    for result in hybrid_results:
        print(result, end="\n\n") 