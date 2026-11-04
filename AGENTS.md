# Contributor and agent guidance

This is a public fork. Keep all committed code, tests, and documentation safe for public release.

## Public-data boundary

- Never commit or paste credentials, tokens, keys, `.env` files, private configuration, nonpublic URLs, internal repository inventories, internal Jira tickets, customer data, sensitive logs, or private planning and review metadata.
- Use generic example owners, project names, and tokens in documentation and tests. Do not copy private SDK identifiers, paths, or internal service details into this repository.
- Preserve the MIT license and upstream attribution. Do not claim that the inherited code has had a security audit unless one has been performed and documented.

## Tests and publishing

- Mock Git commands, GitHub API calls, and file writes in tests. Do not publish from tests.
- Never use live SDK or Homebrew tap credentials in public-fork CI.
- Obtain runtime credentials only from the caller through the intended workflow inputs or secrets. Never hardcode, commit, or log them.
- Review the complete diff, including staged and untracked files, before publishing changes.
