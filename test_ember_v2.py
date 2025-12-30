"""
Test script for Ember v2 integration with parallel LLM execution.

This is a standalone test to evaluate Ember v2's capabilities before
integrating it into the main application.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# First, check if ember-ai is installed
try:
    import ember
    from ember.api import models
    from ember.models.providers import register_provider, ProviderInfo
    print("✓ Ember v2 is installed")
except ImportError:
    print("✗ Ember v2 is not installed")
    print("\nInstallation instructions:")
    print("  pip install ember-ai")
    print("  # or with MCP support:")
    print("  pip install ember-ai[mcp]")
    sys.exit(1)

# Try to import MCP server support
try:
    from ember.integrations.mcp import EmberMCPServer
    HAS_MCP = True
    print("✓ Ember MCP server support available")
except ImportError:
    HAS_MCP = False
    print("⚠ Ember MCP server support not available (optional)")


def load_config():
    """Load API configuration from config file."""
    try:
        import tomli
    except ImportError:
        import tomllib as tomli

    config_path = Path.home() / ".config" / "aicodeprep-gui" / "api-keys.toml"
    if not config_path.exists():
        print(f"⚠ Config file not found: {config_path}")
        return {}

    with open(config_path, "rb") as f:
        return tomli.load(f)


def configure_providers(config: Dict[str, Any]):
    """Register custom providers with Ember."""

    # Register OpenRouter if configured
    if "openrouter" in config:
        openrouter_config = config["openrouter"]
        api_key = openrouter_config.get("api_key", "")

        if api_key:
            try:
                register_provider(ProviderInfo(
                    name="openrouter",
                    default_api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                ))
                print("✓ Registered OpenRouter provider")
            except Exception as e:
                print(f"⚠ Failed to register OpenRouter: {e}")

    # Register other custom providers
    if "compatible" in config:
        for name, provider_config in config["compatible"].items():
            api_key = provider_config.get("api_key", "")
            base_url = provider_config.get("base_url", "")

            if api_key and base_url:
                try:
                    register_provider(ProviderInfo(
                        name=name,
                        default_api_key=api_key,
                        base_url=base_url
                    ))
                    print(f"✓ Registered custom provider: {name}")
                except Exception as e:
                    print(f"⚠ Failed to register {name}: {e}")


async def test_parallel_execution():
    """Test parallel execution of multiple LLMs."""

    print("\n" + "="*60)
    print("TEST 1: Parallel LLM Execution")
    print("="*60)

    # Test prompt
    prompt = "What is the capital of France? Answer in one sentence."

    # Define models to test
    test_models = [
        "openrouter/openai/gpt-3.5-turbo",
        "openrouter/google/gemini-flash-1.5",
        "openrouter/anthropic/claude-instant-1",
        "openrouter/meta-llama/llama-3-8b-instruct:free",
        "openrouter/mistralai/mistral-7b-instruct:free"
    ]

    print(f"\nPrompt: {prompt}")
    print(f"Models: {len(test_models)}")
    print("\nExecuting in parallel...")

    # Execute all models in parallel using asyncio
    tasks = []
    for model in test_models:
        # Create async task for each model
        async def call_model(m):
            try:
                result = await models(m, prompt)
                return {"model": m, "result": result, "error": None}
            except Exception as e:
                return {"model": m, "result": None, "error": str(e)}

        tasks.append(call_model(model))

    # Wait for all to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Display results
    print("\n" + "-"*60)
    print("Results:")
    print("-"*60)

    successful = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"\n[{i+1}] Model: {test_models[i]}")
            print(f"    Status: ✗ Error")
            print(f"    Error: {str(result)}")
        elif result.get("error"):
            print(f"\n[{i+1}] Model: {result['model']}")
            print(f"    Status: ✗ Error")
            print(f"    Error: {result['error']}")
        else:
            print(f"\n[{i+1}] Model: {result['model']}")
            print(f"    Status: ✓ Success")
            print(f"    Response: {result['result'][:100]}...")
            successful += 1

            # Write to file
            output_file = Path(f"ember_test_llm{i+1}.md")
            output_file.write_text(result['result'], encoding="utf-8")
            print(f"    Saved to: {output_file}")

    print("\n" + "="*60)
    print(f"Summary: {successful}/{len(test_models)} models succeeded")
    print("="*60)

    return results


async def test_ensemble_method():
    """Test ensemble method for combining multiple model outputs."""

    print("\n" + "="*60)
    print("TEST 2: Ensemble Method (Best-of-N)")
    print("="*60)

    # This would use Ember's built-in ensemble capabilities
    print("\n⚠ This test requires ember.operators.ensemble")
    print("   Skipping for now - will be tested once basic parallel works")

    # Pseudocode for future implementation:
    # from ember.operators import ensemble
    # result = ensemble(
    #     models=["gpt-4", "claude-3", "gemini-pro"],
    #     prompt="Your question here",
    #     strategy="voting"  # or "quality", "consensus"
    # )


async def test_mcp_server():
    """Test Ember MCP server capabilities."""

    if not HAS_MCP:
        print("\n⚠ MCP server support not available - skipping test")
        return

    print("\n" + "="*60)
    print("TEST 3: MCP Server Integration")
    print("="*60)

    print("\n✓ MCP server class available: EmberMCPServer")
    print("  To run MCP server:")
    print("    python -m ember.integrations.mcp.server")
    print("\n  Available tools:")
    print("    - ember_generate: Single model text generation")
    print("    - ember_ensemble: Multi-model ensemble")
    print("    - ember_verify: Output verification")
    print("    - ember_compare_models: Model comparison")
    print("    - ember_stream: Streaming generation")


async def main():
    """Main test runner."""

    print("\n" + "="*60)
    print("Ember v2 Integration Test Suite")
    print("="*60)

    # Load configuration
    print("\nLoading configuration...")
    config = load_config()

    if not config:
        print("⚠ No configuration found - using environment variables")
    else:
        print("✓ Configuration loaded")

    # Configure providers
    print("\nConfiguring providers...")
    configure_providers(config)

    # Run tests
    try:
        # Test 1: Parallel execution
        await test_parallel_execution()

        # Test 2: Ensemble (future)
        await test_ensemble_method()

        # Test 3: MCP server
        await test_mcp_server()

    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("Test suite completed")
    print("="*60)


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
