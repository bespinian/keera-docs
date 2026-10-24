# The keera CLI

`keera` does everything the panel does, from a terminal. To install it, see
[Sign in](../use/sign-in.md#in-the-terminal).

`keera help <command>` explains each command and its flags. Every listing
command takes `--json`, and every command `--color auto`, `always` or `never`.
`--no-color` is short for `--color never`.

## Commands

| Command           | What it is for                                                            |
| ----------------- | ------------------------------------------------------------------------- |
| `keera login`     | sign in through the browser                                               |
| `keera logout`    | sign this machine out                                                     |
| `keera whoami`    | who you are signed in as, and on which gateway                            |
| `keera connect`   | set up an editor or agent for this gateway                                |
| `keera doctor`    | check the deployment and say what is missing                              |
| `keera org`       | organisations: list, switch, create, set, delete                          |
| `keera project`   | projects in your organisation                                             |
| `keera user`      | people and their roles                                                    |
| `keera key`       | API keys: create, activate, rotate, revoke                                |
| `keera model`     | models: add, change, check, turn off, delete, apply a file, the catalogue |
| `keera guardrail` | what an organisation, project or key may do                               |
| `keera limit`     | one scope's rate limits                                                   |
| `keera budget`    | one scope's budgets                                                       |
| `keera filter`    | filters: add, check, report                                               |
| `keera router`    | routers: add, show, check, report                                         |
| `keera mcp`       | MCP servers and their tool calls                                          |
| `keera sandbox`   | sandboxes and sandbox classes                                             |
| `keera usage`     | usage and cost, by model, client, project, key, user, day or organisation |
| `keera session`   | tasks of coding agents                                                    |
| `keera failures`  | requests that did not succeed, by kind or status, such as `--status 5xx`  |
| `keera billing`   | the bill and credit for the gateway's own provider keys                   |
| `keera version`   | the version of the command                                                |

Some commands are for operators only, such as `keera org delete`,
`keera org set --lift-limit`, `keera billing grant` and `keera billing invoiced`.

## Which gateway and organisation

A command talks to the first of these:

1. `--url`
2. `KEERA_CONTROL_URL`
3. the gateway you last signed in to with `keera login`
4. <https://gateway.keera.ch>

It acts on the organisation chosen with `keera org switch`, or on
`KEERA_ORG` for one shell or pipeline:

```sh
KEERA_ORG="Example Bank" keera usage --by project
```

## Settings it reads

| Variable             | What it is                                                        |
| -------------------- | ----------------------------------------------------------------- |
| `KEERA_CONTROL_URL`  | the gateway to talk to                                            |
| `KEERA_OPERATOR_KEY` | act with the operator key instead of your sign-in, for automation |
| `KEERA_ORG`          | the organisation to act on                                        |
| `KEERA_CONFIG_DIR`   | where sign-ins are stored                                         |
| `NO_COLOR`           | turns colours off; output is coloured only on a terminal anyway   |
| `CLICOLOR_FORCE`     | colours the output even when it is not a terminal                 |
| `CLAUDE_CONFIG_DIR`  | where `keera connect claude-code` writes, instead of `~/.claude`  |

## In scripts

- `--json` gives machine-readable output.
- Commands that ask for confirmation take `--yes`.
- Secrets can be read from standard input with `@-`, so they stay out of the
  shell history: `keera mcp set github --api-key @-`.
- `keera doctor` exits with an error when a check fails.
