# Core Workflow

This is the workflow AICodePrep is built around.

## 1. Open The Project

From a terminal inside the project:

```text
aicp
```

Or open the folder from the right-click integration after you install it.

## 2. Review The File Tree

The app scans the project and checks likely files by default. Review the tree and adjust the selection.

Use this step to remove generated files, unrelated directories, logs, large data files, or anything else the model does not need.

## 3. Add A Prompt

You can type a prompt directly or use a preset.

Good prompts usually say:

- what problem you are trying to solve
- which behavior matters
- what kind of answer you want
- whether you want a small fix, a plan, or an explanation

## 4. Generate Context

Click **Generate Context**.

AICodePrep copies the generated context to your clipboard and writes it to:

```text
.aicp/context_block.md
```

## 5. Paste Once

Paste the context into one or more AI chats.

This is useful when you want to compare answers from different models, or when you want a strong chat model to diagnose the problem before an editor agent makes the actual code changes.

## Repeat As Needed

The app remembers project selections, so the next pass is usually faster:

1. change the file selection
2. update the prompt
3. generate again
4. paste again
