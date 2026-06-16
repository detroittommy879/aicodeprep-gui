# FAQ

## What is the main point of AICodePrep?

It helps you bundle selected code files into one context block so you can paste them into an AI chat without copying files one by one.

## Is this an IDE plugin?

No. It is a standalone desktop app. You can use it beside VS Code, Cursor, Windsurf, PyCharm, Zed, a terminal, or any other editor.

## Is this an AI agent?

No. The main workflow is context preparation. You choose files, generate the context, and paste it where you want.

## What happens when I click Generate Context?

AICodePrep combines the selected files and optional prompt text, copies the result to your clipboard, and writes it to:

```text
.aicp/context_block.md
```

## Why would I use this if I already use Cursor, Windsurf, or another agent?

Agents are useful for editing and running tools. AICodePrep is useful when you want to control the exact context and ask one or more chat models for a diagnosis, review, or plan.

Many people use both: AICodePrep for clean analysis, then an editor agent for code changes.

## Does it work with web chats?

Yes. That is one of the main use cases.

You can paste the generated context into ChatGPT, Claude, Gemini, OpenRouter, or another chat interface.

## Does it use Rust now?

The current app can use a bundled Rust worker for faster folder scanning and context generation. If the Rust worker is unavailable, it falls back to Python.

See [Performance](performance.md).

## How do I know whether Rust was used?

Launch from a terminal and check the log output. Rust usage and Python fallback are both logged.

The settings window also shows whether the worker is available.

## Is the app free?

The core app is free to use. Pro features are optional.

## Where is the generated file?

The generated context file is saved inside the project:

```text
.aicp/context_block.md
```
