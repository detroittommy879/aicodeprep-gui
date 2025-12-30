"""MCP server for parallel LLM calls with synthesis."""

import asyncio
import logging
import os
import sys
from typing import List, Dict, Any

from .client import OpenRouterClient
from .parallel import parallel_call_async

# Configure logging with detailed format
# Log to both console and a file that can be tailed
log_format = '%(asctime)s [%(levelname)s] %(message)s'
log_date_format = '%H:%M:%S'

# Create file handler for live monitoring
file_handler = logging.FileHandler('parallel_llm_progress.log', mode='a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(log_format, log_date_format))

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format, log_date_format))

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)


class ParallelLLMServer:
    """MCP server that calls multiple LLMs in parallel and synthesizes results.

    This server implements exactly what the instructions require:
    1. Accept a text blob from any MCP client
    2. Fire it to 5 OpenRouter models in parallel
    3. Write each response to separate files
    4. Synthesize results with a 6th model
    5. Return final answer and write to file
    """

    def __init__(self):
        """Initialize the MCP server."""
        try:
            from fastmcp import FastMCP
            self.mcp = FastMCP("parallel-llm-server")
        except ImportError:
            raise ImportError(
                "fastmcp is required. Install with: pip install fastmcp"
            )

        # Check for OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required. "
                "Set it with: export OPENROUTER_API_KEY=your_key_here"
            )

        self.client = OpenRouterClient(api_key)

        # The five models to call in parallel (from instructions)
        # These models have large context windows for handling big prompts
        self.parallel_models = [
            "openai/gpt-5-codex",
            "x-ai/grok-4-fast",
            "mistralai/codestral-2508",
            "google/gemini-2.5-pro",
            "z-ai/glm-4.6",
        ]

        # The synthesizer model (from instructions)
        self.synthesizer_model = "google/gemini-2.5-pro"

        # Register MCP tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools."""

        @self.mcp.tool()
        async def process_prompt(prompt: str) -> str:
            """Process a prompt by calling 5 models in parallel and synthesizing results.

            This implements the exact workflow from the instructions:
            1. Fire prompt to 5 models in parallel
            2. Write each response to test_llm_1.txt ... test_llm_5.txt
            3. Send original + 5 answers to synthesizer model
            4. Write final answer to test_final_best.md
            5. Return final answer to client

            Args:
                prompt: The user's question or problem statement

            Returns:
                Final synthesized answer
            """
            try:
                import time
                start_time = time.time()
                prompt_length = len(prompt.split())
                logger.info(f"=" * 80)
                logger.info(f"🎯 NEW REQUEST: Processing prompt ({prompt_length} words)")
                logger.info(f"📋 Models: {', '.join(self.parallel_models)}")
                logger.info(f"=" * 80)

                # Step 1: Call models in parallel (with 4-minute timeout per model)
                logger.info(f"⚡ PHASE 1: Calling {len(self.parallel_models)} models in parallel...")
                logger.info(f"⏱️  Timeout: 4 minutes per model, ~{len(self.parallel_models) * 4} minutes total worst case")
                
                responses = await self._call_models_parallel(prompt)
                
                # Count successful vs failed responses
                successful = sum(1 for r in responses if not str(r).startswith("Error:"))
                failed = len(responses) - successful
                elapsed = time.time() - start_time
                logger.info(f"✅ PHASE 1 COMPLETE in {elapsed:.1f}s: {successful}/{len(responses)} successful, {failed} failed")
                
                if successful == 0:
                    return "Error: All models failed or timed out. Please try again with a shorter prompt or check your API key."

                # Step 2: Write each raw reply to its own local file (async to avoid blocking)
                logger.info(f"💾 PHASE 2: Writing {len(responses)} responses to files...")
                for i, response in enumerate(responses, 1):
                    filename = f"test_llm_{i}.txt"
                    try:
                        # Use asyncio to avoid blocking event loop
                        await asyncio.to_thread(
                            lambda fn, content: open(fn, "w", encoding="utf-8").write(content),
                            filename,
                            str(response)
                        )
                        logger.info(f"  ✓ Wrote response #{i} to {filename}")
                    except Exception as e:
                        logger.error(f"Failed to write {filename}: {e}")
                        # Write error to file
                        try:
                            await asyncio.to_thread(
                                lambda fn, content: open(fn, "w", encoding="utf-8").write(content),
                                filename,
                                f"Error writing response: {e}"
                            )
                        except Exception as write_error:
                            logger.error(f"Could not write error file: {write_error}")

                # Step 3: Send original prompt + answers to synthesizer
                # Filter out failed responses for synthesis
                valid_responses = []
                valid_models = []
                for model, response in zip(self.parallel_models, responses):
                    if not str(response).startswith("Error:"):
                        valid_models.append(model)
                        valid_responses.append(response)
                    else:
                        logger.warning(f"Excluding failed response from {model}: {response[:100]}...")
                
                if not valid_responses:
                    return "Error: No valid responses to synthesize. All models failed or timed out."
                
                synthesis_prompt = self._build_synthesis_prompt(prompt, valid_models, valid_responses)

                logger.info(f"🔄 PHASE 3: Calling synthesizer model...")
                logger.info(f"  Model: {self.synthesizer_model}")
                logger.info(f"  Input: {len(valid_responses)} valid responses to synthesize")
                final_answer = await self.client.call_model_async(
                    self.synthesizer_model,
                    synthesis_prompt
                )
                logger.info(f"✅ PHASE 3 COMPLETE: Synthesizer returned response")

                # Step 4: Write final answer to file (async to avoid blocking)
                logger.info(f"💾 PHASE 4: Writing final answer to file...")
                final_filename = "test_final_best.md"
                try:
                    await asyncio.to_thread(
                        lambda fn, content: open(fn, "w", encoding="utf-8").write(content),
                        final_filename,
                        final_answer
                    )
                    logger.info(f"  ✓ Wrote final answer to {final_filename}")
                except Exception as e:
                    logger.error(f"  ✗ Failed to write {final_filename}: {e}")

                # Step 5: Return final answer to client
                total_elapsed = time.time() - start_time
                logger.info(f"=" * 80)
                logger.info(f"🎉 REQUEST COMPLETE in {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
                logger.info(f"=" * 80)
                return final_answer

            except asyncio.TimeoutError as e:
                logger.error(f"Timeout processing prompt: {e}")
                return f"Error: Request timed out. Large prompts may take several minutes to process."
            except Exception as e:
                logger.error(f"Error processing prompt: {e}", exc_info=True)
                return f"Error processing prompt: {str(e)}"

        @self.mcp.tool()
        async def list_models() -> List[str]:
            """List all available models configured for parallel processing.

            Returns:
                List of model identifiers
            """
            return self.parallel_models

        @self.mcp.tool()
        async def get_config() -> Dict[str, Any]:
            """Get current server configuration.

            Returns:
                Dictionary with configuration details
            """
            return {
                "parallel_models": self.parallel_models,
                "synthesizer_model": self.synthesizer_model,
                "num_parallel_models": len(self.parallel_models),
            }

    def _build_synthesis_prompt(self, original_prompt: str, models: List[str], responses: List[str]) -> str:
        """Build the synthesis prompt for the final model.

        Args:
            original_prompt: The original user prompt
            models: List of model names used (only successful ones)
            responses: List of responses from each model (only successful ones)

        Returns:
            Formatted synthesis prompt
        """
        num_responses = len(responses)
        prompt_parts = [
            "You are an expert synthesiser analyzing multiple AI model responses.",
            f"You have {num_responses} candidate answer{'s' if num_responses != 1 else ''} to review.",
            "",
            f"Original Problem: {original_prompt}",
            "",
            "--- Candidate Answers ---",
            ""
        ]

        for i, (model, response) in enumerate(zip(models, responses), 1):
            prompt_parts.extend([
                f"Model {i} ({model}):",
                str(response),
                "",
                "---",
                ""
            ])

        prompt_parts.extend([
            "",
            "Task: Review all candidate answers above and return only the single best solution to the user's problem.",
            "Synthesize the best elements from multiple responses if needed, but provide ONE clear, actionable answer.",
            "If responses conflict, use your judgment to determine the most accurate and helpful solution."
        ])

        return "\n".join(prompt_parts)

    async def _call_models_parallel(self, prompt: str) -> List[str]:
        """Call multiple models in parallel and return their responses.
        
        Each model has up to 4 minutes to respond. If a model times out or fails,
        it will be excluded from synthesis, but other models will continue.

        Args:
            prompt: The prompt to send to all models

        Returns:
            List of model responses in order (may include error strings)
        """
        logger.info(f"Calling {len(self.parallel_models)} models in parallel:")
        for i, model in enumerate(self.parallel_models, 1):
            logger.info(f"  {i}. {model}")
        
        args_list = [(model, prompt) for model in self.parallel_models]
        responses = await parallel_call_async(
            self.client.call_model_async,
            args_list,
            max_workers=5
        )
        return responses




def main_sync():
    """Synchronous entry point for the server.
    
    FastMCP manages its own event loop internally.
    """
    try:
        server = ParallelLLMServer()
        logger.info("Server initialized, starting stdio transport...")
        # FastMCP.run() handles everything synchronously
        server.mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main_sync()