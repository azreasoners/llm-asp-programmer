from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai


from keys import CORPUS_NAME, PROJECT_ID

if CORPUS_NAME:
    vertexai.init(project=PROJECT_ID, location="us-central1")
    
    rag_corpus = rag.get_corpus(CORPUS_NAME)
    
    
    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=5,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    
    # Enhance generation
    # Create a RAG retrieval tool

    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=rag_corpus.name,
                    )
                ],
                rag_retrieval_config=rag_retrieval_config,
            ),
        )
    )
else:
    rag_retrieval_tool = None