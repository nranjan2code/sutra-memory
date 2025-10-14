# Contributing

Coding standards and workflow for contributions.

## Code Style

- Black for formatting (line length 79)
- isort for import ordering
- flake8 for linting (aim for 0 errors)
- Type hints required on public APIs

## Commit Messages

- Use imperative mood (e.g., "Add", "Fix", "Refactor")
- Reference issues when applicable

## Pull Request Checklist

- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] `black` and `isort` run
- [ ] `flake8` clean
- [ ] Documentation updated

## Branching

- `main`: stable
- feature branches: `feature/...`
- bugfix branches: `fix/...`

## Review Guidelines

- Focus on correctness and clarity first
- Match existing patterns and idioms
- Ensure errors are handled with the custom exception hierarchy where appropriate
