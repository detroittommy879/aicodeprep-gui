---
hide:
  - navigation
  - toc
---

# AICodePrep { .aicp-sr-only }

<div class="aicp-hero" markdown>

![AICodePrep](assets/logo-wide.webp)

<p class="aicp-tagline">Turn a project folder into one clean context block you can paste into any AI chat.</p>

[Get started](install-and-launch.md){ .md-button .md-button--primary }
[See the workflow](core-workflow.md){ .md-button }

</div>

## Why it exists

When a bug or design question spans many files, copying them into an AI chat one by one is slow and easy to get wrong. AICodePrep scans the folder, pre-checks the files that matter, and writes everything into one organized block with XML tags between files. Choose once, paste once.

<div class="grid cards" markdown>

-   :material-cursor-default-click:{ .lg .middle } **You pick the files**

    ---

    Smart defaults skip `node_modules`, build output and other noise. You check or uncheck the rest.

-   :material-chat-processing:{ .lg .middle } **Works with any chat**

    ---

    ChatGPT, Claude, Gemini, AI Studio, OpenRouter. Use free web chats instead of paying per token.

-   :material-brain:{ .lg .middle } **Smarter answers**

    ---

    Models often reason better without tools and agent scaffolding. Give them clean context and let them think.

-   :material-lightning-bolt:{ .lg .middle } **Fast**

    ---

    A bundled Rust worker scans and builds context quickly, with an automatic Python fallback.

-   :material-monitor:{ .lg .middle } **Any editor, any OS**

    ---

    A standalone desktop app for Windows, macOS and Linux. Use it beside VS Code, Cursor, Zed or a terminal.

-   :material-compare-horizontal:{ .lg .middle } **Plan with big models**

    ---

    Plan or debug with a frontier model, then hand the fix to a cheaper model or your editor's agent.

</div>

## The short workflow

<div class="aicp-steps" markdown>

1. Open a project with `aicp` or from the folder right-click menu.
2. Review the files the app selected.
3. Check or uncheck anything you want to change.
4. Add a prompt, or use a saved preset.
5. Click **Generate Context**.
6. Paste the result into your AI chat.

</div>

The output is copied to your clipboard and saved at `.aicp/context_block.md`.

## Install in one line

=== "uv"

    ```bash
    uv tool install aicodeprep-gui
    ```

=== "pipx"

    ```bash
    pipx install aicodeprep-gui
    ```

Then run `aicp` inside any project folder. More options are in [Install And Launch](install-and-launch.md).

## Where to go next

<div class="grid cards" markdown>

-   [:material-download: **Install And Launch**](install-and-launch.md)

    New here? Start with this.

-   [:material-information-outline: **What It Does**](what-it-does.md)

    The app in a bit more detail.

-   [:material-lightbulb-on-outline: **Prompt Strategy**](prompt-strategy.md)

    Get better answers out of the context.

-   [:material-help-circle-outline: **FAQ**](faq.md)

    Common questions.

</div>
