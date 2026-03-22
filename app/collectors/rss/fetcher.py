import httpx

TIMEOUT_SECONDS = 15


async def fetch(url: str) -> bytes:
    """Fetch raw RSS feed bytes from a URL. Raises on non-200 or timeout."""
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content
