from vector_store import search_similar_incidents


query = (
    "The payment service is returning many 503 errors. "
    "CPU is high and the database connection limit is nearly exhausted."
)

results = search_similar_incidents(query, n_results=3)

print("\nSimilar incidents:\n")

for i in range(len(results["ids"][0])):
    print("ID:", results["ids"][0][i])
    print("Title:", results["metadatas"][0][i]["title"])
    print("Root Cause:", results["metadatas"][0][i]["root_cause"])
    print("Resolution:", results["metadatas"][0][i]["resolution"])
    print("Outcome:", results["metadatas"][0][i]["outcome"])
    print("-" * 60)