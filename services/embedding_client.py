import requests
import config

def get_embeddings(texts: list[str]) -> list[list[float]]:
    url = getattr(config, 'EMBEDDING_SERVICE_URL', 'http://localhost:8001/embed')
    response = requests.post(
        url,
        json = {"texts": texts},
        timeout = 60
    )

    response.raise_for_status()

    return response.json()["embeddings"]