import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, List, Optional
import httpx

# 1. Production Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("DocumentPipeline")


# 2. Domain Exceptions with Root Cause Preservation
class PipelineError(Exception):
    """Base exception for all pipeline errors."""

class APIFetchError(PipelineError):
    """Raised when an external API fails to return valid data."""
    def __init__(self, doc_id: int, message: str):
        self.doc_id = doc_id
        super().__init__(f"[Doc ID: {doc_id}] {message}")


# 3. Production Service Architecture
class ProductionDocumentIngester:
    
    def __init__(
        self,
        base_url: str,
        max_concurrency: int = 3,
        request_timeout: float = 5.0
    ):
        self.base_url = base_url
        self.max_concurrency = max_concurrency
        self.timeout = request_timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Initializes connection pool with explicit enterprise limits."""
        limits = httpx.Limits(
            max_connections=20,
            max_keepalive_connections=10,
            keepalive_expiry=30.0
        )
        timeout_config = httpx.Timeout(
            connect=3.0,
            read=self.timeout,
            write=3.0,
            pool=5.0
        )
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            limits=limits,
            timeout=timeout_config
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Guarantees connection pool drain during teardown."""
        if self._client:
            await self._client.aclose()
            logger.info("HTTP connection pool successfully drained and closed.")

    async def _fetch_single_payload(self, doc_id: int) -> Dict[str, Any]:
        """Fetches and parses a single API record."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context.")

        endpoint = f"/posts/{doc_id}"
        try:
            response = await self._client.get(endpoint)
            response.raise_for_status()
            payload = response.json()
            
            return {
                "id": payload["id"],
                "title": payload["title"],
                "body": payload["body"]
            }

        except httpx.HTTPStatusError as exc:
            raise APIFetchError(doc_id, f"HTTP status error: {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise APIFetchError(doc_id, f"Network transport failure: {str(exc)}") from exc
        except asyncio.CancelledError:
            logger.warning(f"In-flight request for doc #{doc_id} was cancelled.")
            raise

    async def _worker(
        self,
        queue: asyncio.Queue[Optional[int]],
        result_queue: asyncio.Queue[Optional[Dict[str, Any]]]
    ) -> None:
        """Consumer worker: pulls doc_ids from queue up to max_concurrency limit."""
        while True:
            doc_id = await queue.get()
            if doc_id is None:  # Sentinel value indicating work is finished
                queue.task_done()
                break

            try:
                data = await self._fetch_single_payload(doc_id)
                await result_queue.put(data)
                logger.info(f"Ingested doc #{doc_id}")
            except APIFetchError as err:
                logger.error(str(err))
            except asyncio.CancelledError:
                queue.task_done()
                raise
            except Exception as unhandled:
                logger.critical(f"Unexpected error processing doc #{doc_id}: {unhandled}")
            finally:
                queue.task_done()

    async def stream_documents(
        self, 
        doc_ids: List[int]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream items as they finish without unbounded task creation.
        Uses a bounded worker-pool pattern.
        """
        input_queue: asyncio.Queue[Optional[int]] = asyncio.Queue()
        result_queue: asyncio.Queue[Optional[Dict[str, Any]]] = asyncio.Queue()

        # Enqueue items to fetch
        for doc_id in doc_ids:
            await input_queue.put(doc_id)

        # Append sentinel tokens to shut down workers cleanly
        for _ in range(self.max_concurrency):
            await input_queue.put(None)

        # Spawn bounded pool of workers
        workers = [
            asyncio.create_task(self._worker(input_queue, result_queue))
            for _ in range(self.max_concurrency)
        ]

        # Monitor worker completion in background
        async def monitor():
            await input_queue.join()
            await asyncio.gather(*workers)
            # Signal end of results
            await result_queue.put(None)

        monitor_task = asyncio.create_task(monitor())

        try:
            while True:
                item = await result_queue.get()
                if item is None:
                    result_queue.task_done()
                    break
                yield item
                result_queue.task_done()
        finally:
            # If the caller terminates early (e.g. break from loop), cancel tasks cleanly
            if not monitor_task.done():
                monitor_task.cancel()
            for w in workers:
                if not w.done():
                    w.cancel()
            await asyncio.gather(*workers, monitor_task, return_exceptions=True)

    @staticmethod
    def _write_file_blocking(records: List[Dict[str, Any]], target_file: Path) -> None:
        """Internal synchronous helper for thread execution."""
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    @classmethod
    async def save_results_async(
        cls, 
        records: List[Dict[str, Any]], 
        output_path: Path
    ) -> None:
        """
        Non-blocking disk write.
        Offloads synchronous file I/O to a background thread pool.
        """
        logger.info(f"Persisting {len(records)} records to disk asynchronously...")
        await asyncio.to_thread(cls._write_file_blocking, records, output_path)
        logger.info(f"File successfully written at: {output_path.resolve()}")


# 4. Production Pipeline Execution
async def main():
    api_url = "https://jsonplaceholder.typicode.com"
    target_ids = list(range(1, 11))
    storage_destination = Path("data") / "production_documents.json"
    downloaded_records: List[Dict[str, Any]] = []

    logger.info("Initializing production ingestion pipeline...")

    # Using proper async lifecycle context
    async with ProductionDocumentIngester(
        base_url=api_url, 
        max_concurrency=3, 
        request_timeout=5.0
    ) as ingester:
        
        async for document in ingester.stream_documents(target_ids):
            downloaded_records.append(document)

    # Offload disk operations without freezing the event loop
    await ProductionDocumentIngester.save_results_async(
        downloaded_records, 
        storage_destination
    )
    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user. System shutdown initiated.")