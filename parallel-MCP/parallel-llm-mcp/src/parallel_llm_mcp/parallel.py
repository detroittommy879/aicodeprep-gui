"""Parallel execution utilities."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Any, Tuple


def parallel_call(
    func: Callable,
    args_list: List[Tuple[Any, ...]],
    max_workers: int = 5
) -> List[Any]:
    """Execute a function in parallel with different arguments.

    This is a simplified version of the parallel execution pattern
    extracted from ember-v2, but without the JAX complexity.

    Args:
        func: Function to execute in parallel
        args_list: List of argument tuples for each function call
        max_workers: Maximum number of parallel workers

    Returns:
        List of results in the same order as args_list
    """
    if not args_list:
        return []

    def run_single(args):
        return func(*args)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(run_single, args_list))

    return results


async def parallel_call_async(
    func: Callable,
    args_list: List[Tuple[Any, ...]],
    max_workers: int = 5
) -> List[Any]:
    """Execute a function in parallel with different arguments (async version).

    Args:
        func: Function to execute (can be sync or async)
        args_list: List of argument tuples for each function call
        max_workers: Maximum number of parallel workers

    Returns:
        List of results in the same order as args_list
    """
    if not args_list:
        return []

    async def run_single(args):
        if asyncio.iscoroutinefunction(func):
            return await func(*args)
        else:
            # Run sync function in thread pool
            return await asyncio.to_thread(func, *args)

    # Create semaphore to limit concurrent calls
    semaphore = asyncio.Semaphore(max_workers)

    async def bounded_run(args):
        async with semaphore:
            return await run_single(args)

    tasks = [bounded_run(args) for args in args_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert exceptions to error strings
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            processed_results.append(f"Error: {str(result)}")
        else:
            processed_results.append(result)

    return processed_results