# Run Keera Agents

How to run [Keera Agents](../use/agents.md) and
[workspaces](../use/workspaces.md) next to your gateway.

Keera Agents is a separate service with its own Postgres. It can run as
several replicas. It runs each agent and workspace on a machine of its own: a
StatefulSet on Kubernetes, or a podman container for development. It runs no
model itself: every model call goes through the gateway.

On Kubernetes, install it with the [Helm chart](kubernetes.md#keera-agents).
This page explains the settings behind it.

## Connect it to the gateway

On the gateway, set:

```sh
KEERA_AGENTS_URL=https://agents.example.ch
KEERA_AGENTS_SERVICE_KEY=…   # openssl rand -hex 32
```

The first lets people sign in to Keera Agents, and links to it from the
panel and from Keera Chat. It must differ from `KEERA_CHAT_URL`. The second
lets Keera Agents issue and revoke keys for agents, look up people, read the
organisation's projects, models, routers and MCP servers, and
[bill machines](#bill-machines). It must be at least 32 characters, and
differ from the gateway's other secrets.

On Keera Agents:

```sh
KEERA_AGENTS_PUBLIC_URL=https://agents.example.ch   # the gateway's KEERA_AGENTS_URL
KEERA_AGENTS_GATEWAY_URL=https://keera.example.ch
KEERA_AGENTS_SERVICE_KEY=…   # the same value as on the gateway
KEERA_AGENTS_SECRET_KEY=…    # openssl rand -hex 32
KEERA_AGENTS_DATABASE_URL=postgres://…
KEERA_AGENTS_DRIVER=kubernetes
KEERA_AGENTS_NAMESPACE=keera-agents-sandbox
KEERA_AGENTS_RUNTIME_URL=http://keera-agents.keera-agents.svc
```

`KEERA_AGENTS_SECRET_KEY` encrypts the connectors' credentials and the agents'
keys. Changing it signs everyone out, and connectors must be entered again.
It must be at least 16 characters.

Without `KEERA_AGENTS_DRIVER`, people can create agents, but none runs.

## On one host

For development, run Keera Agents from its source, with Postgres in a
container and agents as podman containers next to it. The
[keera-agents repository](https://github.com/bespinian/keera-agents) explains
it in `docs/run-locally.md`. Its image cannot run agents in a container:
podman cannot run inside it.

## The agent image

Each agent runs `KEERA_AGENTS_IMAGE`, and each workspace
`KEERA_AGENTS_WORKSPACE_IMAGE`. Each release publishes both, at
`ghcr.io/bespinian/keera-agent:<tag>` and
`ghcr.io/bespinian/keera-workspace:<tag>`.

- The agent image is Alpine with bash, git, curl, Python, jq and ripgrep.
- The workspace image is Debian with pi, VS Code (code-server), Cline, tmux,
  sshd, git, Node, Python and a C toolchain.

Their root file system is read-only. To give agents more tools, build your own
image `FROM` one of them. Upgrade them together with Keera Agents.

## Bill machines

To bill organisations for their agents' and workspaces' machines, set prices
in CHF on Keera Agents:

```sh
KEERA_AGENTS_PRICE_CPU_HOUR=0.05          # one CPU, while it runs
KEERA_AGENTS_PRICE_MEMORY_GIB_HOUR=0.006  # one GiB of memory, while it runs
KEERA_AGENTS_PRICE_DISK_GIB_MONTH=0.12    # one GiB of disk, while it exists
```

Any price above 0 turns billing on. The gateway needs nothing more than the
service key. Machines then appear on the gateway's
[bill](../manage/billing.md#agents-and-workspaces) and take from its credit.
An organisation the gateway would refuse starts no machine, and its running
ones are suspended once idle. If the gateway cannot be reached, Keera Agents
keeps the time and sends it later.

## Publish it

Keera Agents listens on port `8070` (`KEERA_AGENTS_ADDR`):

| Path                 | Who calls it                                        |
| -------------------- | --------------------------------------------------- |
| `/`, `/api`, `/auth` | people's browsers, Keera Chat and `keera`           |
| `/hooks`             | chat services such as Slack, from the internet      |
| `/runtime`           | the agents' machines, so keep it inside the cluster |
| `/healthz`           | liveness, answers before the schema migrates        |
| `/readyz`            | readiness, answers 503 until ready                  |
| `/metrics`           | Prometheus, with `KEERA_AGENTS_METRICS_TOKEN`       |

`keera workspace` reaches workspaces through Upgrade requests. The proxy in
front must pass them on over HTTP/1.1, and not cut idle connections short.

## Settings

Required: `KEERA_AGENTS_GATEWAY_URL`, `KEERA_AGENTS_SERVICE_KEY`,
`KEERA_AGENTS_SECRET_KEY` and `KEERA_AGENTS_DATABASE_URL`. Keera Agents
refuses to start with a missing or wrong setting, and names it.

| Variable                                                            | Default                              | What it is                                                                                                                |
| ------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| `KEERA_AGENTS_PUBLIC_URL`                                           | `http://127.0.0.1:<port>`            | Keera Agents' address, as browsers and chat services reach it.                                                            |
| `KEERA_AGENTS_ADDR`                                                 | `:8070`                              | The address and port to listen on.                                                                                        |
| `KEERA_AGENTS_GATEWAY_INTERNAL_URL`                                 | `KEERA_AGENTS_GATEWAY_URL`           | The gateway's address from Keera Agents, if different.                                                                    |
| `KEERA_AGENTS_DRIVER`                                               | none                                 | `kubernetes` or `podman`.                                                                                                 |
| `KEERA_AGENTS_RUNTIME_URL`                                          | `KEERA_AGENTS_PUBLIC_URL`            | Keera Agents' address from the agents' machines, usually inside the cluster.                                              |
| `KEERA_AGENTS_RUNTIME_GATEWAY_URL`                                  | `KEERA_AGENTS_GATEWAY_INTERNAL_URL`  | The gateway's address from the agents' machines.                                                                          |
| `KEERA_AGENTS_IMAGE`, `_WORKSPACE_IMAGE`                            | local builds                         | The [images](#the-agent-image) of agents and workspaces.                                                                  |
| `KEERA_AGENTS_RUNTIME_STANDARD`, `_RUNTIME_ISOLATED`, `_RUNTIME_VM` | none                                 | The runtime of each isolation tier: a RuntimeClass on Kubernetes, such as gVisor or Kata, or `runsc` or `krun` on podman. |
| `KEERA_AGENTS_MIN_ISOLATION`                                        | `standard`                           | The weakest tier an agent may have: `standard`, `isolated` or `vm`.                                                       |
| `KEERA_AGENTS_MAX_CPU`, `_MAX_MEMORY`, `_MAX_DISK`                  | 8, 32Gi, 100Gi                       | The largest machine.                                                                                                      |
| `KEERA_AGENTS_IDLE_SUSPEND`                                         | `15m`                                | How long an agent waits for work before it sleeps. `0` for never.                                                         |
| `KEERA_AGENTS_WORKSPACE_IDLE_SUSPEND`                               | `2h`                                 | How long a workspace nobody is connected to stays awake. `0` for never.                                                   |
| `KEERA_AGENTS_TASK_TIMEOUT`                                         | `30m`                                | The longest a task may run.                                                                                               |
| `KEERA_AGENTS_WATCH_INTERVAL`                                       | `5m`                                 | How often watched folders are checked. At least `30s`.                                                                    |
| `KEERA_AGENTS_UPSTREAM_PRIVATE`                                     | `none`                               | Host names inside your network that connectors may reach, such as a GitLab server, or `all`.                              |
| `KEERA_AGENTS_UPSTREAM_DENY`                                        | loopback, link-local, cloud metadata | Addresses no connector may reach. `none` turns it off.                                                                    |
| `KEERA_AGENTS_PRICE_*`                                              | unset: machines are free             | What machine time costs. See [Bill machines](#bill-machines).                                                             |
| `KEERA_AGENTS_METRICS_TOKEN`                                        | unset: `/metrics` is off             | The bearer token that reads `/metrics`. At least 16 characters.                                                           |
| `KEERA_AGENTS_SECURE_COOKIES`                                       | on for https                         | Marks the sign-in cookie `Secure`.                                                                                        |
| `KEERA_AGENTS_LOG_LEVEL`, `_LOG_FORMAT`                             | `info`, `text`                       | As on the gateway.                                                                                                        |

### On Kubernetes

Keera Agents must run inside the cluster. Give the agents a namespace of their
own (`KEERA_AGENTS_NAMESPACE`), with a NetworkPolicy that denies everything by
default. Keera Agents needs a Role there. The
[Helm chart](kubernetes.md#where-agents-run) sets all of this up.

| Variable                          | Default         | What it is                                                          |
| --------------------------------- | --------------- | ------------------------------------------------------------------- |
| `KEERA_AGENTS_NAMESPACE`          | required        | Where agents and workspaces run.                                    |
| `KEERA_AGENTS_STORAGE_CLASS`      | the cluster's   | What the agents' disks are made from.                               |
| `KEERA_AGENTS_SERVICE_ACCOUNT`    | the namespace's | What agents run as. Its token is never mounted.                     |
| `KEERA_AGENTS_IMAGE_PULL_SECRETS` | none            | Secrets to pull the images with, comma-separated.                   |
| `KEERA_AGENTS_USER_NAMESPACES`    | `false`         | Runs standard-tier pods in a user namespace. Needs Kubernetes 1.33. |

### On podman

| Variable                      | Default          | What it is               |
| ----------------------------- | ---------------- | ------------------------ |
| `KEERA_AGENTS_PODMAN_BINARY`  | `podman`         | The command to run.      |
| `KEERA_AGENTS_PODMAN_NETWORK` | podman's default | The network agents join. |

## Back up and upgrade

Back up three things on the same schedule:

- **The database**, with `pg_dump`.
- **`KEERA_AGENTS_SECRET_KEY`**, apart from it, in your secret store. Without
  it, connectors must be entered again.
- **The workspaces' volumes**: on Kubernetes, the PVCs labelled
  `app.kubernetes.io/managed-by=keera-agents`; on podman, the volumes named
  `keera-agent-…-workspace`. They hold agents' memory, chats and unpushed work.

The schema migrates at start. Take a backup before you upgrade: a release
refuses to start against a database a newer one migrated, so going back means
restoring it.

Images built `FROM` the agent or workspace image keep working across
upgrades. One that names `/usr/local/bin/keera-agents` itself must change to
`keera-agents-runtime`.
