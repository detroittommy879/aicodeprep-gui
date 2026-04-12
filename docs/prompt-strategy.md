# Prompt Strategy

The app is not just about file selection.

It is also about giving the model a cleaner, better-shaped request.

## Keep the prompt specific

A good prompt for pasted project context usually includes:

- the concrete problem
- what you want back
- any constraints
- the style of answer you want

Example:

```text
Find the bug causing duplicate saves in this app.
Focus on the endpoint settings dialog and persistence flow.
Do not rewrite everything. Suggest the smallest safe fix first.
```

## Dual prompt placement

One of the best Pro features is dual prompt placement.

That means your prompt can be placed above and below the code context instead of only once.

Why this helps:

- some models lose focus after reading a large block of code
- repeating the task framing at the end helps pull attention back to the actual question
- it often improves answer quality on harder debugging or planning tasks

This is one of the simplest quality boosts in the app.

## Why clean chat prompts matter

A lot of agent systems wrap the real task in too much extra material:

- tool instructions
- edit policies
- MCP/server chatter
- internal loop scaffolding

That extra text is not your code problem.

When you paste a clean prompt and a carefully selected context block into a web chat, the model can spend more of its attention on your actual task.

## Best model usage pattern

A practical pattern many people use:

1. use AICodePrep to generate the context block
2. paste it into multiple web chats
3. compare the best answers
4. bring the winning plan back into your editor or agent tool

This works well when:

- one model is better at planning
- another is better at debugging
- another is cheaper or free
- you want a second opinion before changing code
