class RAGResponseParser:
    """
    Normalizes RAG API responses.
    """

    def parse(self, api_response: dict) -> dict:
        if not isinstance(api_response, dict):
            return {
                "answer": "",
                "sources": [],
                "retrieved_context": "",
                "raw_response": api_response
            }

        answer = (
            api_response.get("answer")
            or api_response.get("response")
            or api_response.get("result")
            or api_response.get("output")
            or ""
        )

        sources = (
            api_response.get("sources")
            or api_response.get("source_documents")
            or api_response.get("citations")
            or []
        )

        context = (
            api_response.get("context")
            or api_response.get("retrieved_context")
            or api_response.get("source_context")
            or ""
        )

        if isinstance(sources, str):
            sources = [sources]

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_context": context,
            "raw_response": api_response
        }