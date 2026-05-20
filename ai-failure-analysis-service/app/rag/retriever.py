class FailureRetriever:

    def __init__(
            self,
            embedding_service,
            vector_store
    ):

        self.embedding_service = (
            embedding_service
        )

        self.vector_store = (
            vector_store
        )

    def retrieve_similar_failures(
            self,
            embedding
    ):

        similar_failures = (
            self.vector_store
            .search_similar_failures(
                embedding
            )
        )

        return similar_failures