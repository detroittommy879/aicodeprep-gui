"""Test parallel execution functionality."""

import pytest
import asyncio
from unittest.mock import Mock, patch

from parallel_llm_mcp.parallel import parallel_call, parallel_call_async


def test_parallel_call():
    """Test basic parallel execution."""

    def square(x):
        return x * x

    args_list = [(1,), (2,), (3,), (4,)]
    results = parallel_call(square, args_list)

    assert results == [1, 4, 9, 16]


def test_parallel_call_empty():
    """Test parallel execution with empty list."""

    def dummy_func(x):
        return x

    results = parallel_call(dummy_func, [])
    assert results == []


@pytest.mark.asyncio
async def test_parallel_call_async():
    """Test async parallel execution."""

    async def multiply(a, b):
        await asyncio.sleep(0.01)  # Simulate async work
        return a * b

    args_list = [(2, 3), (4, 5), (6, 7)]
    results = await parallel_call_async(multiply, args_list)

    assert results == [6, 20, 42]


@pytest.mark.asyncio
async def test_parallel_call_async_with_sync_func():
    """Test async parallel execution with sync function."""

    def add(a, b):
        return a + b

    args_list = [(1, 2), (3, 4), (5, 6)]
    results = await parallel_call_async(add, args_list)

    assert results == [3, 7, 11]


@pytest.mark.asyncio
async def test_parallel_call_async_error_handling():
    """Test async parallel execution with errors."""

    async def failing_func(x):
        if x == 2:
            raise ValueError("Test error")
        return x * 2

    args_list = [(1,), (2,), (3,)]
    results = await parallel_call_async(failing_func, args_list)

    assert results[0] == 2
    assert results[1] == "Error: Test error"
    assert results[2] == 6


@pytest.mark.asyncio
async def test_parallel_call_async_max_workers():
    """Test that max_workers limits concurrent execution."""

    execution_count = 0
    max_concurrent = 0

    async def slow_func(x):
        nonlocal execution_count, max_concurrent

        execution_count += 1
        max_concurrent = max(max_concurrent, execution_count)

        await asyncio.sleep(0.1)
        execution_count -= 1

        return x

    args_list = [(i,) for i in range(5)]
    await parallel_call_async(slow_func, args_list, max_workers=2)

    # Should never exceed 2 concurrent executions
    assert max_concurrent <= 2