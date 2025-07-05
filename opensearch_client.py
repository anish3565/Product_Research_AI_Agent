from opensearchpy import OpenSearch

def get_openseach_client(host, port):
    client=OpenSearch(
        hosts=[{"host": host, "port":port}],
        http_compress=True,
        timeout=30,
        max_retries=3,
        retry_on_timeout=True,
    )

    if client.ping():
        print("Connect to OpenSearch!")
        info=client.info()
        print(f"Cluster name: {info['cluster_name']}")
        print(f"OpenSearch version: {info['version']['number']}")
    else:
        print("Connection failed!")
        raise ConnectionError("Failed to connect to OpenSearch")
    return client


def create_index_if_not_exists(client, index_name):
    """
    Create an OpenSearch index with proper mapping for vector search if it doesn't exist.
    
    Args:
        client: Opensearch client instance
        index_name: Name of the index to create
    """

    # Delete the index if it exists (to ensure proper mapping)
    if client.indices.exists(index=index_name):
        print(f"Deleting existing index: '{index_name}' to recreate it.")

        client.indices.delete(index=index_name)

    # Get dimension from a sample embedding
    from embeddings import get_embedding

    sample_embedding = get_embedding("Sample text for dimension detection")
    dimension = len(sample_embedding)
    print(f"Using embedding dimension: {dimension}")

    # Define the index mapping with vector field for embeddings
    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "abstract": {"type": "text"},
                "publication_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd||yyyy||epoch_millis||strict_date_optional_time||strict_date_time||epoch_second",
                },
                "patent_id": {"type": "keyword"},
                "pdf": {"type": "keyword"},
                "token_count": {"type": "integer"},
                "embedding":{"type":"knn_vector", "dimension": dimension},
            }
        },
        "settings": {
            "index": {
                "knn": True,
                "knn.space_type": "cosinesimil", # Use cosine similarity for embeddings
            }
        },
    }


if __name__=="__main__":
    host="localhost"
    port=9200
    client=get_openseach_client(host, port)

    # List all indices
    indices=client.cat.indices(format="json")
    print("Available indices:")
    for index in indices:
        print(f" - {index['index']}")