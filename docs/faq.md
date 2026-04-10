# FAQ

## What is the main point of this app?

To help you quickly bundle the right code files and paste them into AI chats without doing manual copy-paste work.

## Is this mainly an AI chat app?

No. The main job is still fast context prep.

AI Chat and Flow Studio exist, but they are secondary compared to the core generate-and-paste workflow.

## Do I have to use an IDE plugin?

No. That is one of the main benefits.

It works beside your editor, not inside one specific editor.

## How do I open it quickly?

Type `aicp` in a terminal inside your project.

Or install the file explorer / finder integration and open it from a folder directly (either right clicking in the empty space or right on a folder ---> aicodeprep-gui).

## What happens when I generate context?

The app copies all your files with everything organized with XML tags (or whatever option is selected) to your clipboard and also writes it to:

```text
.aicp/context_block.md
```

## Why not just use Cursor, Windsurf, or another agent tool?

Sometimes those are great.

But they often include too much unrelated context or do not send enough of the right files. AICodePrep is useful when you want tighter control and better problem solving. Also, its free to paste your context into a lot of the web chat interfaces: try googling "z.ai glm chat", "kimi ai chat", "gemini ai studio", most still free today!

## Is this good for web chats?

Yes. That is one of the best uses for it.

You can paste the same context into multiple web chats and compare answers.

## Does this help with models that are bad at agent loops?

Yes. Some models are much stronger when they are allowed to just read the full context and answer directly without any tool usage, without MCP servers, etc.

## Is the app free?

Yes. The app is free to use.

Pro features are optional and use a one-time payment model.

## What screenshots should the docs add later?

Good first screenshots would be:

- the main UI with selected files
- a right-click folder launch example
- the prompt box and Generate Context button
- the generated `.aicp/context_block.md` file
