"""Module with async functions and methods."""
import asyncio


async def async_hello():
    """Async hello function."""
    await asyncio.sleep(0.1)
    return "Hello!"


async def fetch_data(url: str) -> str:
    """Async function with type hints."""
    await asyncio.sleep(0.1)
    return f"Data from {url}"


def sync_function():
    """Regular synchronous function."""
    return "Sync"


class AsyncService:
    """Service with async methods."""

    async def start(self):
        """Start the service."""
        await asyncio.sleep(0.1)

    async def stop(self):
        """Stop the service."""
        await asyncio.sleep(0.1)

    def sync_method(self):
        """Synchronous method."""
        return "sync"
