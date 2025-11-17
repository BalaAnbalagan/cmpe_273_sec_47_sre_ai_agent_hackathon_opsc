"""
Cohere AI Integration for Image Intelligence
Provides embedding generation and RAG-based image analysis
"""

import os
from typing import List, Dict, Any, Optional
import cohere
from loguru import logger

# Initialize Cohere client
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL_EMBED = os.getenv("COHERE_MODEL_EMBED", "embed-english-v3.0")
COHERE_MODEL_CHAT = os.getenv("COHERE_MODEL_CHAT", "command-r-plus")

if not COHERE_API_KEY or COHERE_API_KEY == "your-cohere-api-key-here":
    logger.warning("COHERE_API_KEY not set - Cohere features will not work")
    _cohere_client = None
else:
    _cohere_client = cohere.Client(COHERE_API_KEY)


def is_available() -> bool:
    """Check if Cohere service is available"""
    return _cohere_client is not None


async def generate_text_embedding(text: str, input_type: str = "search_query") -> List[float]:
    """
    Generate embedding for text using Cohere embed model

    Args:
        text: Input text to embed
        input_type: Type of input - "search_query", "search_document", or "classification"

    Returns:
        List of floats representing the embedding vector
    """
    if not _cohere_client:
        raise ValueError("Cohere client not initialized - check COHERE_API_KEY")

    try:
        response = _cohere_client.embed(
            texts=[text],
            model=COHERE_MODEL_EMBED,
            input_type=input_type,
            embedding_types=["float"]
        )
        return response.embeddings.float[0]
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def generate_image_description_embedding(
    image_description: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[float]:
    """
    Generate embedding for image description/metadata

    Args:
        image_description: Text description of the image
        metadata: Optional metadata to include (site_id, tags, etc.)

    Returns:
        Embedding vector for the image
    """
    # Combine description with metadata for richer embeddings
    text_parts = [image_description]

    if metadata:
        if "site_id" in metadata:
            text_parts.append(f"Site: {metadata['site_id']}")
        if "tags" in metadata:
            text_parts.append(f"Tags: {', '.join(metadata['tags'])}")
        if "detected_objects" in metadata:
            text_parts.append(f"Objects: {', '.join(metadata['detected_objects'])}")

    combined_text = " | ".join(text_parts)
    return await generate_text_embedding(combined_text, input_type="search_document")


async def chat_with_context(
    query: str,
    context_documents: List[Dict[str, Any]],
    max_tokens: int = 500
) -> Dict[str, Any]:
    """
    Use Cohere's RAG to answer questions about images with context

    Args:
        query: User's natural language query
        context_documents: List of relevant documents (image metadata) for context
        max_tokens: Maximum tokens in response

    Returns:
        Dict with 'answer' and 'citations'
    """
    if not _cohere_client:
        raise ValueError("Cohere client not initialized - check COHERE_API_KEY")

    try:
        # Format documents for Cohere
        documents = []
        for i, doc in enumerate(context_documents):
            doc_text = f"Image ID: {doc.get('image_id', 'unknown')}\n"

            if "metadata" in doc and doc["metadata"]:
                meta = doc["metadata"]
                doc_text += f"Site: {meta.get('site_id', 'N/A')}\n"
                doc_text += f"Description: {meta.get('description', 'N/A')}\n"

                if "tags" in meta:
                    doc_text += f"Tags: {', '.join(meta['tags'])}\n"
                if "detected_objects" in meta:
                    doc_text += f"Objects: {', '.join(meta['detected_objects'])}\n"
                if "safety_violations" in meta:
                    doc_text += f"Safety Issues: {', '.join(meta['safety_violations'])}\n"

            documents.append({"id": f"doc_{i}", "text": doc_text})

        # Call Cohere chat with documents
        response = _cohere_client.chat(
            message=query,
            documents=documents,
            model=COHERE_MODEL_CHAT,
            max_tokens=max_tokens,
            temperature=0.3
        )

        return {
            "answer": response.text,
            "citations": [
                {
                    "document_id": cite.document_ids[0] if cite.document_ids else None,
                    "text": cite.text
                }
                for cite in (response.citations or [])
            ]
        }
    except Exception as e:
        logger.error(f"Error in chat_with_context: {e}")
        raise


async def analyze_safety_compliance(image_descriptions: List[str]) -> Dict[str, Any]:
    """
    Analyze images for safety compliance using Cohere

    Args:
        image_descriptions: List of image descriptions to analyze

    Returns:
        Dict with compliance analysis
    """
    if not _cohere_client:
        raise ValueError("Cohere client not initialized - check COHERE_API_KEY")

    try:
        # Create prompt for safety analysis
        prompt = f"""Analyze the following site images for safety compliance.
Identify any safety violations such as:
- Workers without hard hats
- Missing safety equipment
- Unsafe working conditions
- Equipment hazards

Images:
{chr(10).join(f"{i+1}. {desc}" for i, desc in enumerate(image_descriptions))}

Provide a structured analysis with:
1. Overall compliance score (0-100)
2. Violations found
3. Recommendations
"""

        response = _cohere_client.chat(
            message=prompt,
            model=COHERE_MODEL_CHAT,
            temperature=0.2
        )

        return {
            "analysis": response.text,
            "raw_response": response.text
        }
    except Exception as e:
        logger.error(f"Error in safety analysis: {e}")
        raise


async def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embedding for a user's search query

    Args:
        query: Natural language search query

    Returns:
        Embedding vector for semantic search
    """
    return await generate_text_embedding(query, input_type="search_query")


async def extract_safety_requirements_from_bp(
    bp_documents: List[Dict[str, Any]]
) -> str:
    """
    Extract specific safety requirements from BP documents to create an image search query.

    Args:
        bp_documents: List of BP 10-K document chunks with safety guidelines

    Returns:
        String with specific safety requirements to search for in images
    """
    if not _cohere_client:
        raise ValueError("Cohere client not initialized - check COHERE_API_KEY")

    try:
        # Format BP documents for Cohere RAG
        documents = []
        for i, doc in enumerate(bp_documents):
            doc_text = f"{doc.get('text', '')}"
            documents.append({
                "id": f"bp_doc_{i}",
                "text": doc_text
            })

        # Query BP documents for specific safety requirements
        prompt = """Based on the BP safety documentation provided, extract specific safety requirements and violations to look for in industrial site images.

Focus on:
- Hard hat and PPE requirements
- Protective equipment standards
- Safety barriers and restricted area protocols
- Electrical safety requirements
- Thermal and heat exposure protection
- Oil and gas site safety protocols
- Equipment grounding and lockout/tagout

Generate a concise search query (2-3 sentences) that describes safety violations to look for in images, based on BP's standards."""

        response = _cohere_client.chat(
            message=prompt,
            documents=documents,
            model=COHERE_MODEL_CHAT,
            max_tokens=200,
            temperature=0.2
        )

        return response.text.strip()
    except Exception as e:
        logger.error(f"Error extracting safety requirements from BP docs: {e}")
        # Fallback search query if extraction fails
        return "safety violations workers without hard hats missing PPE protective equipment exposed wiring unauthorized access missing barriers thermal hazards oil gas leaks electrical hazards"


async def analyze_safety_with_bp_rag(
    image_descriptions: List[str],
    bp_documents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze images for safety compliance using RAG with BP 10-K documents.
    Uses BP safety guidelines and compliance standards as context.

    Args:
        image_descriptions: List of image descriptions to analyze
        bp_documents: List of BP 10-K document chunks with safety guidelines

    Returns:
        Dict with compliance analysis based on BP standards
    """
    if not _cohere_client:
        raise ValueError("Cohere client not initialized - check COHERE_API_KEY")

    try:
        # Format BP documents for Cohere RAG
        documents = []
        for i, doc in enumerate(bp_documents):
            doc_text = f"{doc.get('text', '')}"
            documents.append({
                "id": f"bp_doc_{i}",
                "text": doc_text
            })

        # Create prompt for RAG-based safety analysis
        prompt = f"""You are a safety compliance expert analyzing industrial site images based on BP's official safety standards and guidelines.

Using the BP safety documentation provided, analyze the following site images for compliance violations:

Images to analyze:
{chr(10).join(f"{i+1}. {desc}" for i, desc in enumerate(image_descriptions))}

Based on BP's safety standards in the provided documents, identify:
1. Safety violations and non-compliance issues
2. Specific BP safety requirements that are being violated
3. Risk level for each violation (Critical/High/Medium/Low)
4. Recommended corrective actions based on BP standards

Provide a detailed compliance report citing specific BP safety requirements."""

        # Use Cohere chat with RAG
        response = _cohere_client.chat(
            message=prompt,
            documents=documents,
            model=COHERE_MODEL_CHAT,
            max_tokens=800,
            temperature=0.2
        )

        return {
            "analysis": response.text,
            "raw_response": response.text,
            "citations": [
                {
                    "document_id": cite.document_ids[0] if cite.document_ids else None,
                    "text": cite.text
                }
                for cite in (response.citations or [])
            ],
            "bp_documents_used": len(documents)
        }
    except Exception as e:
        logger.error(f"Error in BP RAG safety analysis: {e}")
        raise
