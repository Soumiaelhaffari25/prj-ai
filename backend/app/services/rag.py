"""Service RAG """
from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings as LlamaSettings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url

from app.core.config import settings


KB_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"

embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)
LlamaSettings.embed_model = embed_model
LlamaSettings.llm = None

_url = make_url(settings.database_url)


def _make_vector_store() -> PGVectorStore:
    """Construit le connecteur vers la table de vecteurs dans pgvector."""
    return PGVectorStore.from_params(
        database=_url.database,
        host=_url.host,
        port=_url.port,
        user=_url.username,
        password=_url.password,
        table_name="kb_embeddings",
        embed_dim=settings.embedding_dim,
    )


def build_index() -> int:
    """Indexe (ou réindexe) les documents de la base de connaissance.
    Vide d'abord l'index existant pour éviter les doublons.
    Retourne le nombre de documents lus.
    """
    if not KB_DIR.exists():
        raise FileNotFoundError(f"Dossier knowledge_base introuvable : {KB_DIR}")

    vector_store = _make_vector_store()

    # On vide l'index existant avant de reconstruire (évite les doublons)
    try:
        vector_store.clear()
    except Exception:
        pass  # table pas encore créée au tout premier appel : rien à vider

    documents = SimpleDirectoryReader(str(KB_DIR)).load_data()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return len(documents)


def retrieve_context(query: str, top_k: int = 3) -> str:
    """Récupère les passages les plus pertinents pour une requête donnée.

    query : texte décrivant le lead (secteur, poste, taille, signaux…).
    top_k : nombre de passages à ramener.
    Retourne les passages concaténés, ou une chaîne vide si l'index est vide.
    """
    vector_store = _make_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)
    if not nodes:
        return ""
    return "\n\n---\n\n".join(n.node.get_content() for n in nodes)