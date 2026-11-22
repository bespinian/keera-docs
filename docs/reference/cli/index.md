# The keera CLI

`keera` does everything the panel does, from a terminal. To install it, see
[Sign in](../use/sign-in.md#in-the-terminal).

`keera help <command>` explains each command and its flags.

## Commands

| Command           | What it is for                                                            |
| ----------------- | ------------------------------------------------------------------------- |
| `keera login`     | sign in through the browser                                               |
| `keera logout`    | sign this machine out                                                     |
| `keera whoami`    | who you are signed in as, and on which gateway                            |
| `keera connect`   | set up a tool, such as Claude Code, for this gateway                      |
| `keera doctor`    | check the deployment and say what is missing                              |
| `keera org`       | organisations: list, switch                                               |
| `keera project`   | projects in your organisation                                             |
| `keera user`      | people and their roles                                                    |
| `keera key`       | API keys: create, activate, list, change, rotate, revoke                  |
| `keera model`     | models: add, change, check, turn off, delete, apply a file, the catalogue |
| `keera guardrail` | what an organisation, project or key may do                               |
| `keera limit`     | one scope's rate limits                                                   |
| `keera budget`    | one scope's budgets                                                       |
| `keera filter`    | filters: add, change, check, try, report, delete                          |
| `keera router`    | routers: add, show, change, check, try, report, delete                    |
| `keera mcp`       | MCP servers and their tool calls                                          |
| `keera usage`     | usage and cost, by model, client, project, key, user or day               |
| `keera session`   | tasks of coding agents                                                    |
| `keera failures`  | requests that did not succeed, by kind or status, such as `--status 5xx`  |
| `keera audit`     | who changed what, by action, person or period                             |
| `keera billing`   | the bill, credit and recurring charges                                    |
| `keera agent`     | [agents](../use/agents.md): create, change, ask, start, stop, logs, cost  |
| `keera task`      | the tasks agents were given: list, follow, cancel                         |
| `keera schedule`  | tasks on a timetable: create, change, run now, preview                    |
| `keera workspace` | [workspaces](../use/workspaces.md): create, open, forward, SSH, logs      |
| `keera version`   | the version of the command                                                |

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

| Variable            | What it is                                                       |
| ------------------- | ---------------------------------------------------------------- |
| `KEERA_CONTROL_URL` | the gateway to talk to                                           |
| `KEERA_ORG`         | the organisation to act on                                       |
| `KEERA_CONFIG_DIR`  | where sign-ins are stored                                        |
| `CLAUDE_CONFIG_DIR` | where `keera connect claude-code` writes, instead of `~/.claude` |

## In scripts

- Every listing command takes `--json` for machine-readable output.
- Commands that ask for confirmation take `--yes`.
- Secrets can be read from standard input with `@-`, so they stay out of the
  shell history: `keera mcp set github --api-key @-`.
