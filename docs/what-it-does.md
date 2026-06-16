# What It Does

AICodePrep is a desktop app for preparing code context for AI chats.

It does not replace your editor. It does not require a specific IDE. It gives you a fast way to collect the files you want and paste them into a model as one organized block.

## Main Job

Without AICodePrep, a common workflow looks like this:

1. Open a file.
2. Copy the contents.
3. Switch to the browser.
4. Paste into the chat.
5. Repeat for every related file.

With AICodePrep:

1. Open the project.
2. Review the selected files.
3. Click **Generate Context**.
4. Paste once.

## What Gets Generated

The app creates a text context block containing the selected files and optional prompt text. The generated context is copied to your clipboard and written to:

```text
.aicp/context_block.md
```

That makes it useful for:

- pasting into web chats
- comparing several models with the same context
- saving a snapshot of the files you asked about
- handing a plan from a stronger chat model back to an editor or coding agent

## Good Use Cases

AICodePrep is especially useful for:

- debugging bugs that span several files
- asking for architecture or code review
- preparing refactor plans
- comparing answers from different models
- using web chats when an IDE agent is missing context or adding too much unrelated noise

## Optional Features

The app also has prompt presets, right-click integration, Pro options, and other workflow tools. Those are secondary. The core value is still fast context preparation.
