import requests

embedding_url = "http://localhost:8001/embed"

def get_embeddings(texts: list[str]) -> list[list[float]]:
    response = requests.post(
        embedding_url,
        json = {"texts": texts},
        timeout = 30
    )

    response.raise_for_status()

    return response.json()["embeddings"]
    