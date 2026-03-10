import logging

from tavily import TavilyClient

from atlas.config import settings
from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.orchestrator import register_tool
from atlas.vault.indexer import search_vault

logger = logging.getLogger(__name__)


def _web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Tavily API with DuckDuckGo fallback."""
    # Try Tavily first if configured
    if settings.tavily_api_key and settings.tavily_api_key != "tvly-test":
        try:
            client = TavilyClient(api_key=settings.tavily_api_key)
            response = client.search(query, max_results=max_results)
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:300],
                }
                for r in response.get("results", [])
            ]
        except Exception as e:
            logger.warning("Tavily search failed, trying DuckDuckGo: %s", e)

    # Fallback to DuckDuckGo (free)
    return _duckduckgo_search(query, max_results)


def _duckduckgo_search(query: str, max_results: int = 5) -> list[dict]:
    """Search using DuckDuckGo (free, no API key required)."""
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")[:300],
                }
                for r in results
            ]
    except Exception:
        logger.exception("DuckDuckGo search failed")
        return []


async def handle_search(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle search intent.

    Args:
        intent: IntentResult with parameters

    Returns:
        Tuple of (context_string_for_persona, list_of_actions)
    """
    query = intent.parameters.get("query", "")
    source = intent.parameters.get("source", "both")

    if not query:
        raise ValueError("Query is required for search")

    vault_results = []
    web_results = []

    if source in ("vault", "both"):
        vault_results = search_vault(query, n_results=5)

    if source in ("web", "both"):
        web_results = _web_search(query, max_results=5)

    # Build context for persona
    context_parts = []

    if vault_results:
        context_parts.append("**Resultados do Vault:**")
        for r in vault_results:
            title = r.get("title") or r["path"]
            context_parts.append(f"- [{title}] {r['snippet'][:150]}")

    if web_results:
        context_parts.append("**Resultados da Web:**")
        for r in web_results:
            context_parts.append(f"- [{r['title']}]({r['url']}) — {r['snippet'][:150]}")

    if not context_parts:
        context_parts.append("Nenhum resultado encontrado.")

    context = "\n".join(context_parts)

    action = ActionResult(
        type="search",
        details={
            "query": query,
            "source": source,
            "vault_count": len(vault_results),
            "web_count": len(web_results),
        },
    )

    logger.info("Search '%s' — vault: %d, web: %d", query, len(vault_results), len(web_results))

    return context, [action]


register_tool(IntentType.SEARCH, handle_search)
