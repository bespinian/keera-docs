# Run Keera Agents

How to run [Keera Agents](../use/agents.md) next to your gateway.

Keera Agents is a separate service with its own Postgres database. It creates
its tables itself, and can run as several replicas. It runs each agent in a
container of its own: on Kubernetes, or on podman for development.

On the gateway, set:

```sh
KEERA_AGENTS_URL=https://agents.example.ch
KEERA_AGENTS_SERVICE_KEY=…   # openssl rand -hex 32
```

The first lets people sign in to Keera Agents, and links to it from the
panel. It must differ from `KEERA_CHAT_URL`. The second lets Keera Agents
issue and revoke keys for agents, look up people, and read the organisation's
projects, models, routers and MCP servers. It must be at least 32 characters,
and differ from the gateway's other secrets.

On Keera Agents:

```sh
KEERA_AGENTS_PUBLIC_URL=https://agents.example.ch   # the gateway's KEERA_AGENTS_URL
KEERA_AGENTS_GATEWAY_URL=https://keera.example.ch
KEERA_AGENTS_SERVICE_KEY=…   # the same value as on the gateway
KEERA_AGENTS_SECRET_KEY=…    # openssl rand -hex 32
KEERA_AGENTS_DATABASE_URL=postgres://…
KEERA_AGENTS_DRIVER=kubernetes
KEERA_AGENTS_IMAGE=registry.example.ch/keera-agent:<version>
KEERA_AGENTS_RUNTIME_URL=http://keera-agents.keera:8070
```

Back up `KEERA_AGENTS_SECRET_KEY` with the database. It encrypts the
connectors' credentials and the agents' keys. Without it, the credentials
cannot be read. Changing it signs everyone out. It must be at least 16
characters.

`KEERA_AGENTS_DRIVER` is `kubernetes` or `podman`. Without it, people can
create agents, but none runs.

## The agent image

Each agent runs `KEERA_AGENTS_IMAGE`. Build it from the keera-agents source
with `make agent-image`, push it to your registry, and upgrade it together
with Keera Agents.

## Publish it

Keera Agents listens on port `8070` (`KEERA_AGENTS_ADDR`):

| Path                  | Who calls it                                          |
| --------------------- | ----------------------------------------------------- |
| `/`, `/api`, `/auth`  | people's browsers                                     |
| `/hooks`              | chat services such as Slack, from the internet        |
| `/runtime`            | the agents' containers, so keep it inside the cluster |
| `/healthz`, `/readyz` | health checks                                         |

## Settings

| Variable                                                            | Default                              | What it is                                                                                                                                         |
| ------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `KEERA_AGENTS_GATEWAY_INTERNAL_URL`                                 | `KEERA_AGENTS_GATEWAY_URL`           | The gateway's address from Keera Agents, if different.                                                                                             |
| `KEERA_AGENTS_RUNTIME_URL`                                          | `KEERA_AGENTS_PUBLIC_URL`            | Keera Agents' address from the agents' containers, usually inside the cluster.                                                                     |
| `KEERA_AGENTS_RUNTIME_GATEWAY_URL`                                  | `KEERA_AGENTS_GATEWAY_INTERNAL_URL`  | The gateway's address from the agents' containers.                                                                                                 |
| `KEERA_AGENTS_IMAGE`                                                | `localhost/keera-agent:latest`       | The [agent image](#the-agent-image).                                                                                                               |
| `KEERA_AGENTS_RUNTIME_STANDARD`, `_RUNTIME_ISOLATED`, `_RUNTIME_VM` | none                                 | The runtime of each isolation tier: a runtime class on Kubernetes, such as gVisor or Kata, or an OCI runtime on podman, such as `runsc` or `krun`. |
| `KEERA_AGENTS_MIN_ISOLATION`                                        | `standard`                           | The weakest isolation an agent may have: `standard`, `isolated` or `vm`.                                                                           |
| `KEERA_AGENTS_MAX_CPU`, `_MAX_MEMORY`, `_MAX_DISK`                  | 8, 32Gi, 100Gi                       | The most an agent's machine may get.                                                                                                               |
| `KEERA_AGENTS_IDLE_SUSPEND`                                         | `15m`                                | How long an agent waits for work before it sleeps. At least `1m`, or `0` for never.                                                                |
| `KEERA_AGENTS_TASK_TIMEOUT`                                         | `30m`                                | The longest a task may run. At least `1m`.                                                                                                         |
| `KEERA_AGENTS_WATCH_INTERVAL`                                       | `5m`                                 | How often watched folders are checked. At least `30s`.                                                                                             |
| `KEERA_AGENTS_UPSTREAM_PRIVATE`                                     | `none`                               | Host names inside your network that connectors may reach, such as a GitLab server, or `all`.                                                       |
| `KEERA_AGENTS_UPSTREAM_DENY`                                        | loopback, link-local, cloud metadata | Addresses no connector may use.                                                                                                                    |
| `KEERA_AGENTS_LOG_LEVEL`, `_LOG_FORMAT`                             | `info`, `text`                       | As on the gateway.                                                                                                                                 |

## On Kubernetes

The Kubernetes driver works only when Keera Agents runs inside the cluster.
Give the agents a namespace of their own (`KEERA_AGENTS_NAMESPACE`), with a
network policy that denies everything by default. Keera Agents needs a Role
there. `KEERA_AGENTS_STORAGE_CLASS`, `_SERVICE_ACCOUNT` and
`_IMAGE_PULL_SECRETS` set what the agents' pods get.

## Keera Chat

When the gateway has both `KEERA_CHAT_URL` and `KEERA_AGENTS_URL`, people can
chat with their agents in Keera Chat. If Keera Chat cannot reach Keera Agents
at `KEERA_AGENTS_URL`, set
[`KEERA_CHAT_AGENTS_INTERNAL_URL`](chat.md) on Keera Chat.
