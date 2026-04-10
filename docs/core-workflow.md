# Core Workflow

This is the workflow the app is built around.

## 1. Open the project

Either:

- type `aicp` in a terminal inside the project
- or open it from the folder context menu integration

## 2. Let the app pre-select files

The app is meant to save time right away.

It auto-selects likely files so you do not start from zero every time.

Then you just review the list and make fast corrections.

## 3. Add your question or prompt

You can type your own prompt or use a preset for repeated prompts. Presets is just text you type often, you can set that text to a button, and press the button to just paste the text in the prompt box.

Typical examples:

- Can you figure out why xxxx happens in my web app, and then write the solution/fix in a style for an AI coding agent? Assume the agent is dumb and uses a cheap model but is good and efficient at editing files. Write the solution in one single big code block for easy copy and paste. The agent loves find and replace style instructions.
- find the bug in this code
- explain the architecture and weak points
- plan a refactor with minimal behavioral changes. Write your refactor instructions for my AI coding agent.
- compare two implementation options

## 4. Generate context

Click Generate Context.

The app writes the output to the clipboard and also stores it in:

```text
.aicp/context_block.md
```

That means you can:

- paste immediately into an AI chat
- keep the file around for reuse
- regenerate quickly after adjusting files or prompt text

## 5. Paste into one or more AI chats

This is where the app earns its keep.

You can paste the same project context into:

- ChatGPT
- Claude
- Gemini
- GLM
- Qwen
- DeepSeek
- OpenRouter models
- other web chats or direct chat interfaces

That makes it easy to compare answers instead of trusting the first model or first agent you try. Even in these times where we have coding agents and great models, it is still stuck on one AI model, and sometimes the agent harness does not give the model enough context. Too little context is sometimes not enough to fix a bug. With this tool you can add much more. You can get the full intelligence from the models - since every tool or MCP server that is given to a model the dumber it gets for problem solving.

## Why this beats manual copy-paste

Without the app, getting good context into AI chats is repetitive and annoying.

With the app, it becomes a fast loop:

1. tweak selection
2. regenerate
3. paste
4. compare answers
5. iterate

## Why this beats some agent flows

Many agentic tools are strongest when you want autonomous edits.

But for hard reasoning, debugging, planning, and architecture work, a clean direct-chat prompt with full context is often better.

That is especially useful when you want to use models that are strong in chat but not especially strong as tool-using agents.

## Screenshot placeholders

Suggested screenshots to add later:

- main file tree with auto-selected files
- prompt box with a real example prompt
- Generate Context button and output result
- `.aicp/context_block.md` opened beside the app
