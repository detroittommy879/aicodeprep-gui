# Prompt Strategy

AICodePrep gives the model two things:

- the files you selected
- the prompt you wrote

The files matter, but the prompt still decides what kind of answer you get.

## Write The Task Clearly

A good prompt usually includes:

- the bug, question, or goal
- the part of the project to focus on
- constraints the model should respect
- the format you want back

Example:

```text
Find why duplicate saves happen in this app.
Focus on the endpoint settings dialog and persistence flow.
Do not rewrite the whole feature.
Suggest the smallest fix first, then mention any follow-up cleanup.
```

## Ask For The Right Output

Different tasks need different answers.

For debugging:

```text
Find the most likely bug and explain the exact code path.
```

For planning:

```text
Write a step-by-step implementation plan for an AI coding agent.
Keep the plan scoped to the files included here.
```

For review:

```text
Review this code for correctness risks and missing tests.
Prioritize concrete bugs over style feedback.
```

## Prompt Presets

Presets are saved prompt snippets. They are useful for prompts you use repeatedly, such as debugging, review, refactor planning, or writing instructions for another coding tool.

## Dual Prompt Placement

Pro can place the prompt both before and after the context block.

This can help large-context prompts because the model sees the task again after reading the files. It is a practical quality-of-life feature, not a requirement for using the app.
