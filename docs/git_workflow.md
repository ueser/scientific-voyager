# Git Workflow

This document outlines the Git workflow and conventions used in the Scientific Voyager project.

## Branching Strategy

We follow a simplified Git Flow approach with the following branches:

### Main Branches

- **main**: The production-ready code. All code in this branch should be stable and deployable.
- **develop**: The main development branch. Feature branches are merged into this branch.

### Supporting Branches

- **feature/\***: Feature branches are used to develop new features. They branch off from `develop` and are merged back into `develop`.
- **bugfix/\***: Bugfix branches are used to fix bugs. They branch off from `develop` and are merged back into `develop`.
- **hotfix/\***: Hotfix branches are used to fix critical bugs in production. They branch off from `main` and are merged back into both `main` and `develop`.
- **release/\***: Release branches are used to prepare for a new production release. They branch off from `develop` and are merged into both `main` and `develop`.

## Branch Naming Convention

- Feature branches: `feature/short-description`
- Bugfix branches: `bugfix/short-description` or `bugfix/issue-number`
- Hotfix branches: `hotfix/short-description` or `hotfix/issue-number`
- Release branches: `release/version-number`

Examples:
- `feature/cross-level-integration`
- `bugfix/issue-42`
- `hotfix/critical-api-fix`
- `release/1.0.0`

## Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages. This leads to more readable messages that are easy to follow when looking through the project history.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries

### Scope

The scope is optional and should be the name of the module affected (as perceived by the person reading the changelog).

### Subject

The subject contains a succinct description of the change:
- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No dot (.) at the end

### Body

The body should include the motivation for the change and contrast this with previous behavior.

### Footer

The footer should contain any information about Breaking Changes and is also the place to reference GitHub issues that this commit closes.

### Examples

```
feat(llm): add support for GPT-4o model

Implement integration with OpenAI's GPT-4o model for improved insight generation.

Closes #123
```

```
fix(config): resolve environment variable loading issue

Fix bug where environment variables were not being properly loaded from .env file.

Fixes #456
```

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Update the documentation with details of changes if appropriate
3. The PR should work in all environments (development, testing, production)
4. PRs require at least one approval from a code owner
5. PRs should be linked to an issue when applicable

## Code Review Guidelines

1. **Be respectful and constructive**: Focus on the code, not the person
2. **Be specific**: Point to specific lines of code rather than general statements
3. **Explain why**: Explain the reasoning behind your suggestions
4. **Prioritize feedback**: Distinguish between must-fix issues and nice-to-have improvements
5. **Consider the context**: Take into account the scope and purpose of the PR

## Branch Protection Rules

The following branch protection rules are in place:

### For `main` and `develop` branches:

- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators in these restrictions
- Do not allow force pushes
- Do not allow deletion

## Git Best Practices

1. **Keep branches short-lived**: Long-lived branches lead to merge conflicts and integration problems
2. **Commit early and often**: Small, focused commits are easier to review and understand
3. **Keep commits atomic**: Each commit should represent a single logical change
4. **Rebase feature branches**: Keep your feature branches up to date with the latest changes from the develop branch
5. **Squash commits before merging**: Squash multiple commits into a single, coherent commit before merging
6. **Write meaningful commit messages**: Follow the commit message format described above
7. **Never commit sensitive data**: API keys, passwords, and other sensitive data should never be committed
