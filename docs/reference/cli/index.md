# The keera CLI

`keera` does everything the panel does, from a terminal. It works with Keera
Gateway, and with the agents and workspaces of Keera Agents.

## Install

Download `keera` for Linux, macOS or Windows from the
[releases page](https://github.com/bespinian/keera-gateway/releases), unpack
it and put it on your `PATH`. Then sign in:

```sh
keera login
```

See [Sign in](../../use/sign-in.md#in-the-terminal).

## Commands

[Commands](commands.md) lists every command and flag. `keera help <command>`
shows the same in the terminal.

| Command                                          | What it is for                                                            |
| ------------------------------------------------ | ------------------------------------------------------------------------- |
| [`keera login`](commands.md#keera-login)         | sign in through the browser                                               |
| [`keera logout`](commands.md#keera-logout)       | sign this machine out                                                     |
| [`keera whoami`](commands.md#keera-whoami)       | who you are signed in as, and on which gateway                            |
| [`keera connect`](commands.md#keera-connect)     | set up a tool, such as Claude Code, for this gateway                      |
| [`keera doctor`](commands.md#keera-doctor)       | check the deployment and say what is missing                              |
| [`keera org`](commands.md#keera-org)             | organisations: list, switch                                               |
| [`keera project`](commands.md#keera-project)     | projects in your organisation                                             |
| [`keera user`](commands.md#keera-user)           | people and their roles                                                    |
| [`keera key`](commands.md#keera-key)             | API keys: create, activate, list, change, rotate, revoke                  |
| [`keera model`](commands.md#keera-model)         | models: add, change, check, turn off, delete, apply a file, the catalogue |
| [`keera mcp`](commands.md#keera-mcp)             | MCP servers and their tool calls                                          |
| [`keera guardrail`](commands.md#keera-guardrail) | what an organisation, project or key may do                               |
| [`keera limit`](commands.md#keera-limit)         | one scope's rate limits                                                   |
| [`keera budget`](commands.md#keera-budget)       | one scope's budgets                                                       |
| [`keera filter`](commands.md#keera-filter)       | filters: add, change, check, try, report, delete                          |
| [`keera router`](commands.md#keera-router)       | routers: add, show, change, check, try, report, delete                    |
| [`keera usage`](commands.md#keera-usage)         | usage and cost, by model, client, project, key, user or day               |
| [`keera billing`](commands.md#keera-billing)     | the bill, credit and recurring charges                                    |
| [`keera failures`](commands.md#keera-failures)   | requests that did not succeed                                             |
| [`keera session`](commands.md#keera-session)     | tasks of coding agents                                                    |
| [`keera audit`](commands.md#keera-audit)         | who changed what                                                          |
| [`keera agent`](commands.md#keera-agent)         | [agents](../../use/agents.md): create, change, ask, start, stop, logs     |
| [`keera task`](commands.md#keera-task)           | the tasks agents were given: list, follow, cancel                         |
| [`keera schedule`](commands.md#keera-schedule)   | tasks on a timetable                                                      |
| [`keera workspace`](commands.md#keera-workspace) | [workspaces](../../use/workspaces.md): create, open, forward, SSH         |
| [`keera version`](commands.md#keera-version)     | the version of the command                                                |

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

`keera agent`, `keera task`, `keera schedule` and `keera workspace` find
Keera Agents through the gateway, and use the same sign-in.

`keera whoami` shows which gateway, organisation and credential are in use.

## Settings it reads

| Variable             | What it is                                                                       |
| -------------------- | -------------------------------------------------------------------------------- |
| `KEERA_CONTROL_URL`  | the gateway to talk to                                                           |
| `KEERA_ORG`          | the organisation to act on                                                       |
| `KEERA_OPERATOR_KEY` | the operator key of a [self-hosted](../../operate/index.md) gateway, for scripts |
| `KEERA_CONFIG_DIR`   | where sign-ins are stored                                                        |
| `CLAUDE_CONFIG_DIR`  | where `keera connect claude-code` writes, instead of `~/.claude`                 |

The operator key wins over a sign-in, but is only sent to a gateway that
`--url` or `KEERA_CONTROL_URL` names.

## In scripts

- Every listing command takes `--json` for machine-readable output.
- Commands that ask for confirmation take `--yes`.
- Secrets can be read from standard input with `@-`, so they stay out of the
  shell history: `keera mcp set github --api-key @-`. `@path` reads a file.
- `--color=never` or `NO_COLOR` turns colours off.
