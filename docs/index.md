# AICodePrep

AICodePrep turns a project folder into one clean context block you can paste into an AI chat.

That is the main job: choose the files once, generate one bundle, paste once.

## The Problem

AI chats are useful for debugging, planning, reviewing, and understanding code, but getting the right files into the chat is tedious. You open a file, copy it, switch tabs, paste it, repeat, and then hope you did not miss something important.

AICodePrep removes manual steps. It scans the folder, pre-checks likely code files (skips things like node_modules, python build files, you can control this) lets you check the files you want, and writes the selected code into a single context block with xml tags to separate files.

## The Short Workflow

1. Open a project with `aicp` or from the folder context menu.
2. Review the files the app selected.
3. Check or uncheck anything you want to change.
4. Add a prompt if you want one.
5. Click **Generate Context**.
6. Paste the result into ChatGPT, Claude, Gemini, OpenRouter, or another chat.

The output is copied to your clipboard and also saved at:

```text
.aicp/context_block.md
```

## Why People Use It

- It is faster than attaching or pasting many files by hand.
- It works with any editor and any AI chat.
- It keeps you in control of which files are included.
- It makes it easy to send the same context to several models and compare answers.
- It is useful alongside agent tools when you want a cleaner, more focused prompt.
- It allows you to plan or bug fix with expensive frontier models, then implement with cheap models.

## Current Performance Work

The current app includes a Rust worker for faster folder scanning and context generation when the bundled worker is available for your platform. If the worker is missing or fails, AICodePrep falls back to the Python path instead of blocking the workflow.

The Rust worker is an implementation detail for speed. The product goal is still the same simple workflow: pick files, generate context, paste once.

## Where To Start

- New users: [Install And Launch](install-and-launch.md)
- Understand the app: [What It Does](what-it-does.md)
- Daily use: [Core Workflow](core-workflow.md)
- Speed/fallback details: [Performance](performance.md)
