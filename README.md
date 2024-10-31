# datahub-repo-template

Default template for FSDH repository.

## Commands to Use Prettier

To install and run [Prettier](https://prettier.io/) for code formatting, use the following command:

```bash
npm install --save-dev prettier && npx prettier --write .
```

This will install Prettier as a development dependency and format all files in the current directory.

## Commands to Use Linter

You can use the following alias command to run [Super-Linter](https://github.com/github/super-linter):

```bash
alias sl='docker run -e RUN_LOCAL=true -e LOG_LEVEL=ERROR -e DEFAULT_BRANCH=$(git rev-parse --abbrev-ref HEAD) -v "$(git rev-parse --show-toplevel)":/tmp/lint --rm ghcr.io/super-linter/super-linter:slim-v7.1.0'
```

This alias runs Super-Linter locally, using the current branch as the default branch for comparison.

## Code Formatting and Linting

This repository uses both **Prettier** and **Super-Linter** to enforce code formatting and linting standards:

- **Prettier**: Handles code formatting, ensuring a consistent code style across JavaScript and other supported files. You can format files manually using the Prettier command above.
- **Super-Linter**: Provides comprehensive linting for a variety of file types in this repository. Running `sl` (using the alias provided above) will start the linter and scan files based on the `.linters.yml` configuration file (if available).

Super-Linter and Prettier together help ensure that code in this repository remains clean, consistent, and adheres to project standards.
