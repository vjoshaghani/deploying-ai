def search_attractions(collection, query, setting=None, limit=3):
    """Search attraction descriptions with an optional setting filter."""
    if not query.strip():
        raise ValueError("The search question cannot be empty.")

    if setting not in {None, "indoor", "outdoor", "mixed"}:
        raise ValueError("Setting must be indoor, outdoor, mixed, or None.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    options = {
        "query_texts": [query],
        "n_results": limit,
    }

    if setting is not None:
        options["where"] = {"setting": setting}

    results = collection.query(**options)

    matches = []

    for place_id, document, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        matches.append({
            "place_id": place_id,
            "name": metadata["name"],
            "description": document,
            "setting": metadata["setting"],
            "source_url": metadata["source_url"],
            "distance": distance,
        })

    return matches