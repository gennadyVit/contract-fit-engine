import os
import numpy as np

# Stub flag — set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env to enable
AZURE_ENABLED = bool(os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"))

if AZURE_ENABLED:
    from openai import AzureOpenAI
    _client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
    )
    EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")


def get_embedding(text: str) -> list[float] | None:
    """Returns embedding vector or None if Azure not configured."""
    if not AZURE_ENABLED:
        return None
    response = _client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    return response.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def compute_capability_similarity(opportunity: dict, profile: dict) -> float | None:
    """
    Returns cosine similarity (0-1) between opportunity text and company profile,
    or None if Azure OpenAI is not configured (fit_score.py will use stub value).
    """
    if not AZURE_ENABLED:
        return None

    opp_text = f"{opportunity.get('TITLE', '')} {opportunity.get('DESCRIPTION', '')}".strip()
    profile_text = (
        profile.get("company_summary", "") + " " +
        " ".join(profile.get("capabilities", [])) + " " +
        " ".join(profile.get("keywords_target", []))
    ).strip()

    if not opp_text or not profile_text:
        return None

    opp_embedding = get_embedding(opp_text)
    profile_embedding = get_embedding(profile_text)

    if opp_embedding and profile_embedding:
        return cosine_similarity(opp_embedding, profile_embedding)
    return None
