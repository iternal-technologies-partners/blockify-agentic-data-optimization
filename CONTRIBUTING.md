# Contributing to Blockify Agentic Data Optimization

Thank you for your interest in contributing! This guide will help you get started.

## Before You Contribute

> **Important:** This project is governed by the [Blockify Community License](./LICENSE). By submitting a pull request, you agree that your contributions will be subject to these terms, including the Contribution License in Section 2.4 which grants Iternal a perpetual, royalty-free license to use your contributions in all Blockify products (including proprietary and commercial offerings). You represent that you are the original author of your contribution or have sufficient rights to grant this license.

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization/issues) to avoid duplicates
2. Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include steps to reproduce, expected behavior, and actual behavior
4. Add environment details (OS, Python version, Docker version)

### Suggesting Features

1. Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
2. Describe the problem your feature would solve
3. Propose a solution and any alternatives you've considered

### Submitting Code

1. Fork the repository
2. Create a feature branch from `main`: `git checkout -b feat/your-feature`
3. Make your changes
4. Ensure tests pass (see below)
5. Submit a pull request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## Development Setup

### Distillation Service

```bash
cd blockify-distillation-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run linting
ruff check app/
black --check app/
mypy app/
```

### Claude Code Skill

```bash
cd blockify-skill-for-claude-code/skills/blockify-integration
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Code Style

- **Formatter:** [Black](https://github.com/psf/black) (default settings)
- **Linter:** [Ruff](https://github.com/astral-sh/ruff)
- **Type checking:** [mypy](https://mypy-lang.org/) (strict mode)
- Run all three before submitting a PR

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Include tests for new functionality
- Update documentation if behavior changes
- Ensure all existing tests pass
- Write clear commit messages describing *why*, not just *what*

## Questions?

- **Technical Support:** support@iternal.ai
- **GitHub Issues:** [Open an issue](https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization/issues)
