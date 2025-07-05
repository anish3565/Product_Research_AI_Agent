from opensearchpy import OpenSearch

def get_opensearch_client(host, port):
    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_compress=True,
        timeout=30,
        max_retries=3,
        retry_on_timeout=True,
    )

    if client.ping():
        print("✅ Connected to OpenSearch!")
        info = client.info()
        print(f"Cluster name: {info['cluster_name']}")
        print(f"OpenSearch version: {info['version']['number']}")
    else:
        print("❌ Connection failed!")
        raise ConnectionError("Failed to connect to OpenSearch")

    return client


def create_index_if_not_exists(client, index_name):
    """
    Create an OpenSearch index with proper mapping for vector search if it doesn't exist.
    
    Args:
        client: Opensearch client instance
        index_name: Name of the index to create
    """
    from embeddings import get_embedding

    # Delete the index if it exists (for clean re-creation)
    if client.indices.exists(index=index_name):
        print(f"⚠️ Deleting existing index: '{index_name}' to recreate it.")
        client.indices.delete(index=index_name)

    # Get embedding dimension dynamically
    sample_embedding = get_embedding("Sample text for dimension detection")
    dimension = len(sample_embedding)
    print(f"📏 Using embedding dimension: {dimension}")

    # Define mapping with knn_vector field
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
                "embedding": {
                    "type": "knn_vector",
                    "dimension": dimension,
                },
            }
        },
        "settings": {
            "index": {
                "knn": True,
                "knn.space_type": "cosinesimil",
            }
        },
    }

    client.indices.create(index=index_name, body=mapping)
    print(f"✅ Index '{index_name}' created with vector support!")


if __name__ == "__main__":
    host = "localhost"
    port = 9200
    client = get_opensearch_client(host, port)

    # List all indices
    indices = client.cat.indices(format="json")
    print("📂 Available indices:")
    for index in indices:
        print(f" - {index['index']}")