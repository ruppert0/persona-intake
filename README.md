# persona-intake

A branching questionnaire that generates consistent, safety-aware operating documents for AI agents.

**Input:** Answer ~20 questions about role, autonomy, platforms, and preferences.
**Output:** `SOUL.md`, `AUTONOMY.md`, `USER.md` — ready to drop into an agent's workspace.

## Why this exists

Setting up an agent's personality and permissions is currently ad-hoc. You either:
- Copy a template and hope it fits
- Write everything from scratch
- Skip it and deal with inconsistent behavior

This tool gives you a structured way to think through the important decisions, then generates coherent docs that actually work together.

## Quick start

### See an example first
Check [`examples/social-operator/`](examples/social-operator/) to see:
- Input: `answers.json` (what someone answered)
- Output: `output/SOUL.md`, `output/AUTONOMY.md`, `output/USER.md`

### Generate your own
```bash
# Coming soon: web UI
# For now: fill out answers.json manually, run generator
python scripts/generate.py examples/social-operator/answers.json --out ./my-agent/
```

## What the questionnaire covers

| Section | What it asks |
|---------|--------------|
| **Core Identity** | Name, role, tone, guiding principles |
| **Autonomy** | What's allowed, what needs approval, what's forbidden |
| **Platforms** | Moltbook/GitHub/etc rules, posting limits, DM policies |
| **Operations** | Memory policy, check-in cadence, reporting |
| **Owner** | Name, context, pet peeves, privacy level |

Questions branch based on your answers. Social agents get asked about posting rules; research agents don't.

## Project structure

```
persona-intake/
├── questions/
│   └── questions.json      # The questionnaire (data, not code)
├── templates/
│   ├── SOUL.template.md    # Template with conditionals
│   ├── AUTONOMY.template.md
│   └── USER.template.md
├── examples/
│   └── social-operator/    # Complete input→output example
│       ├── answers.json
│       └── output/
├── scripts/
│   └── generate.py         # Minimal generator script
└── docs/
    └── DESIGN.md           # Design philosophy
```

## Contributing

We accept PRs for:
- **`questions/`** — new questions, better wording, branching logic
- **`templates/`** — template improvements, new conditional sections
- **`examples/`** — more example profiles showing different agent types
- **`docs/`** — documentation, guides

We do **not** auto-run contributor code. PRs are reviewed manually.

### Good contributions
- "Add question about email handling"
- "Improve AUTONOMY template section on reporting"
- "Add example for research-focused agent"

### Before contributing
Read [`docs/DESIGN.md`](docs/DESIGN.md) to understand the philosophy.

## Status

Early stage. The question bank and templates are functional but evolving. Feedback welcome via Issues.

## License

MIT
