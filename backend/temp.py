import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from vectorstore import load_vector_store

vs = load_vector_store()

results = vs._collection.get(
    include=["documents", "metadatas"]
)

for i, (doc, metadata) in enumerate(
    zip(results["documents"], results["metadatas"])
):
    print(f"\n{'='*60}")
    print(f"CHUNK {i}")
    print(metadata)
    print(doc)