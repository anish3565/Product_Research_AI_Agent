from opensearchpy import OpenSearch

def get_openseach_client(host, port):
    client=OpenSearch(
        hosts=[{"host": host, "port":port}],
        http_compress=True,
        timeout=30,
        max_reties=3,
        retry_on_timeout=True
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






if __name__=="__main__":
    host="localhost"
    port=9200
    client=get_openseach_client(host, port)

    # List all indices
    indices=client.cat.indices(format="json")
    print("Available indices:")
    for index in indices:
        print(f" - {index['index']}")