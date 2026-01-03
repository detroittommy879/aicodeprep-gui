# MCP Server & Library Documentation

## FastMCP (MCP Specification & Framework)

### Installation & Setup

```bash
uv add fastmcp
uv pip install fastmcp
pip install fastmcp
```

#### Pin exact version for production:

```
fastmcp==2.11.0  # Good
fastmcp>=2.11.0  # Bad - may install breaking changes
```

### Running a FastMCP Server

```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

#### CLI Examples

```bash
fastmcp run my_server.py:mcp
fastmcp run my_server.py:mcp --transport http --port 8000
fastmcp install claude-desktop server.py
fastmcp dev server.py --python 3.11
```

### Configuration Example (`fastmcp.json`)

```json
{
  "$schema": "https://gofastmcp.com/public/schemas/fastmcp.json/v1.json",
  "source": {
    "type": "filesystem",
    "path": "server.py",
    "entrypoint": "mcp"
  },
  "environment": {
    "type": "uv",
    "python": ">=3.10",
    "dependencies": ["pandas", "numpy"]
  },
  "deployment": {
    "transport": "stdio",
    "log_level": "INFO"
  }
}
```

### Best Practices

- Place `mcp.run()` inside `if __name__ == "__main__":` block.
- Pin FastMCP version for production.
- Use `uv` for environment management.
- Document all tools and configuration in README.
- Use structured error handling, not string-based exceptions.
- Avoid global logging configuration at import time.

---

## httpx (Python HTTP Client)

### Basic Usage

```python
import httpx

r = httpx.get('https://httpbin.org/get')
print(r.status_code)
print(r.json())
```

### Other HTTP Methods

```python
r = httpx.put('https://httpbin.org/put', data={'key': 'value'})
r = httpx.delete('https://httpbin.org/delete')
r = httpx.head('https://httpbin.org/get')
r = httpx.options('https://httpbin.org/get')
```

### URL Parameters

```python
params = {'key1': 'value1', 'key2': 'value2'}
r = httpx.get('https://httpbin.org/get', params=params)
print(r.url)
```

### POST Request

```python
r = httpx.post('https://httpbin.org/post', data={'key': 'value'})
```

### Authentication

```python
httpx.get("https://example.com", auth=("my_user", "password123"))
auth = httpx.DigestAuth("my_user", "password123")
httpx.get("https://example.com", auth=auth)
```

### Custom Headers

```python
headers = {'user-agent': 'my-app/0.0.1'}
r = httpx.get('https://httpbin.org/headers', headers=headers)
```

### Error Handling

```python
try:
    response = httpx.get("https://www.example.com/")
    response.raise_for_status()
except httpx.RequestError as exc:
    print(f"An error occurred while requesting {exc.request.url!r}.")
except httpx.HTTPStatusError as exc:
    print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
```

### Streaming & Multipart

```python
with httpx.stream("GET", "https://www.example.com") as r:
    for line in r.iter_lines():
        print(line)

with open('report.xls', 'rb') as report_file:
    files = {'upload-file': report_file}
    r = httpx.post("https://httpbin.org/post", files=files)
```

### Async Example (Trio)

```python
import httpx
import trio

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://www.example.com/')
        print(response)

trio.run(main)
```

---

## Project-Specific Best Practices

- Remove unused dependencies (e.g., pydantic if not used).
- Move logging configuration into main entrypoint.
- Use structured exception handling for robust error management.
- Document all MCP tools and configuration.
- Limit prompt length in process_prompt tool to avoid DoS.
- Audit dependencies for vulnerabilities.
