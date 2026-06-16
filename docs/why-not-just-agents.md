# Why Use This With Agents

AICodePrep is not an agent replacement.

It is useful because some tasks work better when you give a model a clean bundle of files and ask for analysis before anything edits the project.

## Where Agents Are Strong

Agent tools are often the right choice when you want:

- file edits
- terminal commands
- test runs
- repeated code changes
- integration inside your editor

Use them for that.

## Where AICodePrep Helps

AICodePrep is useful when you want:

- tighter control over which files the model sees
- the same context sent to several models
- a clean prompt without tool instructions mixed in
- a diagnosis or plan before edits begin
- to use a model that is stronger in direct chat than in an agent loop

## A Practical Hybrid Workflow

One common workflow is:

1. Use AICodePrep to package the relevant files.
2. Paste the context into one or more chat models.
3. Pick the best diagnosis or plan.
4. Give that plan to your editor agent for the mechanical changes.

That lets each tool do the part it is good at.
