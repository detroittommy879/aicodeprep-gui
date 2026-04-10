# What It Does

The core idea is simple:

you know your project better than an agent does, so you should be able to choose the exact context you want to send.

AICodePrep gives you a fast UI for doing that.

## Main job

The app scans your project, respects sensible ignore rules, remembers your choices, and makes it fast to build a context block from the files that matter.

Instead of doing this by hand:

- open file
- copy
- switch tabs
- paste
- repeat 15 times

you do this:

- open AICodePrep
- review the checked files
- tweak a few selections
- click Generate Context
- paste once

## Best use cases

This app is especially useful for:

- debugging hard bugs where the model needs to see several related files at once
- asking for architecture reviews or refactor plans
- using web chats instead of IDE agents for deeper reasoning
- comparing answers from several AI models using the same project context
- working with models that are better in direct chat than in agent mode

## Why not just use an agentic IDE

Sometimes an agent is the right tool.

But sometimes agents:

- do not include enough relevant files
- include too much unrelated noise
- spend effort on tool use instead of reasoning
- are tied to a model that is good at tool calling but worse at pure thinking

That matters because some models, especially in web chat or direct chat mode, can be much stronger when you simply hand them the full context and a clean prompt.

This is especially true for:

- strong reasoning models like o3 when you want pure analysis
- Chinese models that often perform better when they are not wrapped in heavy agent tooling
- free web chat interfaces where you can test multiple models without paying per request

## What the app is not trying to be

AICodePrep is not trying to replace every editor, every agent, or every workflow.

It is a fast bridge from:

project folder -> selected files -> context block -> AI chat

That is why it stays useful even if you already use Cursor, Windsurf, VS Code, or anything else.
