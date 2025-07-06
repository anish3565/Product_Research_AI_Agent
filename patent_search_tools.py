from embeddings import get_embedding
from opensearch_client import get_opensearch_client

def keyword_search(query_text, top_k=20):
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        search_query = {
            "size": top_k,
            "query": {"match": {"abstract": query_text}},
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }

        response = client.search(index=index_name, body=search_query)
        return response["hits"]["hits"] or []
    except Exception as e:
        print(f"Keyword search error: {e}")
        return []

def semantic_search(query_text, top_k=20):
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        query_embedding = get_embedding(query_text)

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
        return response["hits"]["hits"] or []
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []

def hybrid_search(query_text, top_k=20):
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        query_embedding = get_embedding(query_text)

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

        response = client.search(index=index_name, body=search_query)
        return response["hits"]["hits"] or []

    except Exception as e:
        print(f"Hybrid search error: {e}")
        # Fallback to keyword search
        try:
            fallback_query = {
                "size": top_k,
                "query": {"match": {"abstract": query_text}},
                "_source": ["title", "abstract", "publication_date", "patent_id"],
            }
            response = client.search(index=index_name, body=fallback_query)
            return response["hits"]["hits"] or []
        except Exception as e2:
            print(f"Fallback search error: {e2}")
            return []

def iterative_search(query_text, refinement_steps=3, top_k=20):
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    all_results = []
    current_query = query_text

    for i in range(refinement_steps):
        try:
            search_query = {
                "size": top_k,
                "query": {"match": {"abstract": current_query}},
                "_source": ["title", "abstract", "publication_date", "patent_id"],
            }

            response = client.search(index=index_name, body=search_query)
            results = response["hits"]["hits"] or []

            for result in results:
                if result not in all_results:
                    all_results.append(result)

            if not results:
                break

            # Refine query based on top result
            top_result = results[0]
            current_query += f" {top_result['_source'].get('title', '')}"

        except Exception as e:
            print(f"Iterative search error at step {i}: {e}")
            break

    return all_results or []

if __name__ == "__main__":
    query = "lithium battery"

    print("Hybrid Search Results:")
    hybrid_results = hybrid_search(query)
    for result in hybrid_results:
        print(result, end="\n\n")