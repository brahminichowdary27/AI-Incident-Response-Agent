import chromadb


client = chromadb.PersistentClient(
    path="memory/chroma"
)


collection = client.get_or_create_collection(
    name="incident_memory"
)


def add_incident(
    incident_id,
    title,
    description,
    severity,
    root_cause,
    resolution,
    outcome
):
    collection.add(
        ids=[str(incident_id)],
        documents=[description],
        metadatas=[{
            "title": title,
            "severity": severity,
            "root_cause": root_cause,
            "resolution": resolution,
            "outcome": outcome
        }]
    )


def search_similar_incidents(query, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results


def update_incident(
    incident_id,
    title,
    description,
    severity,
    root_cause,
    resolution,
    outcome
):
    collection.update(
        ids=[str(incident_id)],
        documents=[description],
        metadatas=[{
            "title": title,
            "severity": severity,
            "root_cause": root_cause,
            "resolution": resolution,
            "outcome": outcome
        }]
    )