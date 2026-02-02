# Design Philosophy

## Core insight

The templates shouldn't be "fill in the blank." They should be **complete, opinionated documents with conditional sections**.

The questions select which sections appear and customize specific values, but the structure and content are pre-written by people who've thought carefully about what makes agents work well.

Think of it as **configuration**, not generation from scratch.

## Why this matters

An agent with a half-baked AUTONOMY.md will:
- Do things it shouldn't (unclear permissions)
- Ask permission for everything (unclear what's allowed)
- Behave inconsistently (no principles to fall back on)

A well-structured AUTONOMY.md gives the agent clear rails to operate within, which paradoxically enables *more* useful autonomy because boundaries are explicit.

## Question design principles

### 1. Ask about decisions, not implementation
❌ "What regex should filter posts?"
✅ "What types of posts should be forbidden?"

### 2. Provide opinionated defaults
Most people don't know what they want. Good defaults (with the option to change) beat blank slates.

### 3. Branch to reduce noise
A researcher agent doesn't need questions about Moltbook posting rules. Use conditions to show only relevant questions.

### 4. Multiple choice > free text (usually)
Free text is hard to template. Multiple choice lets us generate consistent output. Use free text only for truly variable things (names, specific context).

### 5. Group related questions
Sections help users build a mental model. "Autonomy" questions together, "Platform" questions together.

## Template design principles

### 1. Complete documents, not skeletons
The template should be a valid, useful document even with minimal answers. Conditionals add/remove sections; they don't create content from nothing.

### 2. Opinionated structure
We have opinions about what makes a good AUTONOMY.md. The template encodes those opinions. Users can fork if they disagree.

### 3. Conditional sections for modularity
```
{{#if platforms_moltbook}}
## Moltbook Policy
...
{{/if}}
```

### 4. Sensible fallbacks
If a question isn't answered, the template should still work (omit the section or use a default).

## What we're NOT building

- A general-purpose template engine
- An LLM that writes custom docs from scratch
- A "personality quiz" with no practical output

## What we ARE building

A structured way to make good decisions about agent behavior, encoded in documents that agents can actually use.
