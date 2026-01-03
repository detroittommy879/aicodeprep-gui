"""OpenRouter API client for parallel LLM calls."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Simple OpenRouter API client.

    Handles communication with OpenRouter API for multiple models.
    Supports both sync and async calls.
    """

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        """Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/example/parallel-llm-mcp",
            "X-Title": "Parallel LLM MCP Server",
        }

    async def call_model_async(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Call a single model asynchronously.

        Args:
            model: Model identifier (e.g., "openai/gpt-4")
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Model response text
        """
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        if max_tokens:
            data["max_tokens"] = max_tokens

        # 4-minute timeout for large context windows (240 seconds)
        # These models have large context windows and can handle big prompts
        timeout = httpx.Timeout(240.0, connect=60.0)
        
        import time
        start_time = time.time()
        logger.info(f"🚀 Starting API call to {model}...")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data
                )
                response.raise_for_status()

                elapsed = time.time() - start_time
                logger.info(f"✅ {model} responded in {elapsed:.1f}s")

                result = response.json()
                content = result["choices"][0]["message"]["content"]
                token_count = len(content.split())
                logger.info(f"📊 {model} returned ~{token_count} words")
                return content

            except httpx.HTTPStatusError as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ HTTP error calling {model} after {elapsed:.1f}s: {e.response.status_code} - {e.response.text[:200]}")
                raise
            except httpx.TimeoutException as e:
                elapsed = time.time() - start_time
                logger.error(f"⏱️ Timeout calling {model} after {elapsed:.1f}s (limit: 240s)")
                raise
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ Error calling {model} after {elapsed:.1f}s: {e}")
                raise

    def call_model(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Call a single model synchronously.

        Args:
            model: Model identifier
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Model response text
        """
        return asyncio.run(
            self.call_model_async(model, prompt, temperature, max_tokens)
        )

    async def call_models_parallel(
        self,
        models: List[str],
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Call multiple models in parallel.

        Args:
            models: List of model identifiers
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            List of dictionaries with model and response
        """
        tasks = []
        for model in models:
            task = asyncio.create_task(
                self.call_model_async(model, prompt, temperature, max_tokens)
            )
            tasks.append((model, task))

        results = []
        for model, task in tasks:
            try:
                response = await task
                results.append({"model": model, "response": response})
            except Exception as e:
                logger.error(f"Failed to call {model}: {e}")
                results.append({
                    "model": model,
                    "response": f"Error: {str(e)}"
                })

        return results