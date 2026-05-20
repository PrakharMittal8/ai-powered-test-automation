import faiss
import numpy as np
import json
import os


class VectorStore:

    def __init__(self):

        self.dimension = 384

        # COSINE SIMILARITY
        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        self.memory_file = "data/failure_memory.json"

        self.failure_memory = []

        self.load_existing_memory()

    def load_existing_memory(self):

        if os.path.exists(self.memory_file):

            try:

                with open(
                        self.memory_file,
                        "r",
                        encoding="utf-8"
                ) as file:

                    content = file.read().strip()

                    if not content:

                        self.failure_memory = []

                    else:

                        self.failure_memory = json.loads(
                            content
                        )

                        for failure in self.failure_memory:

                            if "embedding" in failure:

                                vector = np.array(
                                    [failure["embedding"]],
                                    dtype="float32"
                                )

                                self.index.add(vector)

            except Exception as e:

                print(
                    "\nERROR LOADING MEMORY:",
                    str(e)
                )

                self.failure_memory = []

        print("\n======= MEMORY LOADED =======")

        print(
            "Existing Failures:",
            len(self.failure_memory)
        )

        print(
            "FAISS Index Size:",
            self.index.ntotal
        )

        print("=============================\n")

    def store_failure(
            self,
            embedding,
            failure_data
    ):

        vector = np.array(
            [embedding],
            dtype="float32"
        )

        self.index.add(vector)

        self.failure_memory.append(
            failure_data
        )

        self.persist_memory()

        print("\n=========== VECTOR STORED ===========")

        print(
            "Total Stored Failures:",
            len(self.failure_memory)
        )

        print(
            "FAISS Total Vectors:",
            self.index.ntotal
        )

        print("=====================================\n")

    def persist_memory(self):

        os.makedirs(
            "data",
            exist_ok=True
        )

        with open(
                self.memory_file,
                "w",
                encoding="utf-8"
        ) as file:

            json.dump(
                self.failure_memory,
                file,
                indent=4
            )

    def search_similar_failures(
            self,
            embedding,
            top_k=3
    ):

        if self.index.ntotal == 0:

            return []

        query_vector = np.array(
            [embedding],
            dtype="float32"
        )

        distances, indices = self.index.search(
            query_vector,
            top_k
        )

        print("\n========= VECTOR SEARCH =========")

        print(
            "Similarity Scores:",
            distances
        )

        print(
            "Indices:",
            indices
        )

        print("=================================\n")

        results = []

        SIMILARITY_THRESHOLD = 0.75

        seen_failures = set()

        for score, idx in zip(
                distances[0],
                indices[0]
        ):

            if idx == -1:
                continue

            if score < SIMILARITY_THRESHOLD:

                print(
                    f"Rejected Match | Score: {score}"
                )

                continue

            if idx >= len(self.failure_memory):
                continue

            failure = self.failure_memory[idx]

            unique_key = (
                failure["exceptionMessage"]
            )

            if unique_key in seen_failures:
                continue

            seen_failures.add(unique_key)

            print(
                f"Accepted Match | Score: {score}"
            )

            results.append(
                failure
            )

        return results