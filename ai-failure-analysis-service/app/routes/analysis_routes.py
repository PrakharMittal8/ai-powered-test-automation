from fastapi import APIRouter
import json

from app.models.failure_models import FailureRequest
from app.prompts.analysis_prompt import build_failure_analysis_prompt
from app.services.openai_service import OpenAIService
from app.rag.embedding_service import EmbeddingService
from app.rag.preprocessing_service import PreprocessingService
from app.rag.vector_store import VectorStore
from app.rag.retriever import FailureRetriever
from app.agent.failure_agent import run_agent

router = APIRouter()

openai_service = OpenAIService()
embedding_service = EmbeddingService()
preprocessing_service = PreprocessingService()
vector_store = VectorStore()
retriever = FailureRetriever(embedding_service, vector_store)


@router.post("/analyze")
def analyze_failure(data: FailureRequest):

    # Step 1: Clean and embed
    cleaned_text = preprocessing_service.build_failure_text(data)
    embedding = embedding_service.generate_embedding(cleaned_text)

    # Step 2: RAG — retrieve similar failures
    similar_failures = retriever.retrieve_similar_failures(embedding)

    print("\n========= RAG RETRIEVAL =========")
    print("Similar Failures Found:", len(similar_failures))
    print("=================================\n")

    # Step 3: Store only if not duplicate
    is_duplicate = len(similar_failures) > 0

    if not is_duplicate:
        vector_store.store_failure(
            embedding,
            {
                "testName": data.testName,
                "exceptionMessage": data.exceptionMessage,
                "timestamp": str(data.timestamp),
                "environment": data.environment,
                "embedding": embedding
            }
        )
    else:
        print("\n====== DUPLICATE FAILURE DETECTED ======")
        print("Skipping storage because similar failure already exists.")
        print("========================================\n")

    # Step 4: Build prompt and call LLM
    prompt = build_failure_analysis_prompt(data, similar_failures)
    llm_response = openai_service.analyze_failure(prompt)

    try:
        structured_response = json.loads(llm_response)
    except Exception:
        structured_response = {
            "failureType": "UNKNOWN",
            "rootCause": llm_response,
            "confidence": "LOW",
            "recommendedFix": [],
            "frameworkSuggestion": "",
            "isTransient": False,
            "shouldRetry": False
        }

    # Step 5: Run agent
    agent_result = run_agent(
        failure_data=data,
        analysis=structured_response,
        similar_count=len(similar_failures)
    )

    return {
        "analysis": agent_result["dashboardEntry"],
        "similarFailuresFound": len(similar_failures),
        "agentResult": {
            "failureType": agent_result["failureType"],
            "repeatCount": agent_result["repeatCount"],
            "toolsUsed": agent_result["toolsUsed"],
            "toolReasoning": agent_result["toolReasoning"],
            "environmentPattern": agent_result["environmentPattern"],
            "samePageFailures": agent_result["samePageFailures"]
        }
    }