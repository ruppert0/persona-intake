# Contributing to persona-intake

Thanks for your interest in contributing!

## What we accept

- **Questions** (`questions/questions.json`) — new questions, wording improvements, branching logic
- **Templates** (`templates/`) — structure improvements, new conditional sections, better defaults
- **Examples** (`examples/`) — new persona profiles showing different agent types
- **Documentation** (`docs/`, `README.md`) — guides, explanations, clarifications
- **Generator improvements** (`scripts/`) — bug fixes, new features (reviewed carefully)

## Before contributing

1. Read [`docs/DESIGN.md`](docs/DESIGN.md) to understand the philosophy
2. Check existing issues to see if your idea is already being discussed
3. For significant changes, open an issue first to discuss

## How to contribute

1. Fork the repo
2. Create a branch (`git checkout -b my-feature`)
3. Make your changes
4. Test locally if applicable (`python scripts/generate.py examples/social-operator/answers.json`)
5. Commit with a clear message
6. Push and open a PR

## PR guidelines

- Keep PRs focused (one feature/fix per PR)
- Include context for why the change is needed
- For new questions: explain what agent behavior it improves
- For templates: show example output difference

## Code of conduct

Be respectful. We're all here to make agent setup better.
