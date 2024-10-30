# datahub-repo-template

Default teamplate for fsdh repository


Commands to use Linter
alias sl='docker run -e RUN_LOCAL=true -e LOG_LEVEL=ERROR -e DEFAULT_BRANCH=$(git rev-parse --abbrev-ref HEAD) -v "$(pwd)":/tmp/lint --rm ghcr.io/super-linter/super-linter:slim-v7.1.0'