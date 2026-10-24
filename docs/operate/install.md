# Install

## Ways to run it

| Shape                 | For                                      | Postgres                 |
| --------------------- | ---------------------------------------- | ------------------------ |
| **Compose**           | one host or a laptop, demos, development | a container              |
| **NixOS**             | one host, declared                       | native                   |
| **Kubernetes** (Helm) | a cluster serving a team, vLLM on GPUs   | in the cluster, or yours |

Kubernetes runs the image `ghcr.io/bespinian/keera-gateway:<version>`, and
compose builds the same image from the source. NixOS runs the binary
natively. All read the same [settings](settings.md). The compose files are in the
[keera-gateway repository](https://github.com/bespinian/keera-gateway/tree/main/compose).

## What you need

- **Postgres 14 or later.** The gateway creates and updates its tables itself
  when it starts.
- **Two secrets**, each at least 16 characters:

  ```sh
  openssl rand -hex 32   # KEERA_OPERATOR_KEY: the operator's credential
  openssl rand -hex 32   # KEERA_SECRET_KEY: encrypts stored provider keys
  ```

- **A TLS terminator** in front, such as an ingress or a reverse proxy.

## One host with compose

This runs the gateway, Postgres and a model on one machine, such as your
laptop. You need [Podman](https://podman.io) with `podman compose`, and about
4 GB of free disk space.

```sh
git clone https://github.com/bespinian/keera-gateway.git
cd keera-gateway/compose
cp .env.example .env    # set KEERA_OPERATOR_KEY and KEERA_SECRET_KEY
podman compose up -d --build
```

This starts the gateway, Postgres, a small coding model on the CPU (Keera
Engine on llama.cpp) and Keera Decider, a small model that helps routers
decide. The model downloads on the first start; watch it with
`podman compose logs -f keera-engine`. Every setting in `.env` reaches the
gateway.

Open <http://localhost:8080> and sign in with the operator key. Then continue
with [First run](#first-run).

!!! note "The CPU model cannot make tool calls"

    It can chat, but coding agents need tool calls to edit files. For those,
    use a GPU.

On a host with an NVIDIA GPU, use vLLM instead:

```sh
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml   # once
podman compose -f compose.yaml -f compose.gpu.yaml up -d --build
```

The default GPU model is Qwen2.5-Coder-7B, about 5.6 GB, which fits a 24 GB
card.

## Publish it

One port, `8080`, carries everything. Paths tell the parts apart:

| Path       | What it is                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------ |
| `/api`     | the inference API and MCP servers, for API keys                                            |
| `/control` | the control API, for the panel and `keera`                                                 |
| `/sandbox` | connections to sandboxes                                                                   |
| `/`        | the control panel, and `/metrics`, `/healthz`, `/readyz`, `/openapi.json`, `/openapi.yaml` |

When you put it on the network:

- **Terminate TLS in front.** The gateway does not do it.
- **Turn off response buffering** in the proxy, and set a read timeout longer
  than the longest answer. Otherwise streaming arrives all at once.
- **Allow large request bodies.** Coding agents send long conversations; the
  gateway accepts up to 32 MiB by default.
- **Set `KEERA_PUBLIC_URL`** to the public address.
- **Set up [single sign-on or passkeys](sign-on.md)** before anyone else can
  reach the panel.
- To offer only the API, without the panel, publish only `/api`.

!!! warning "Keep the model servers private"

    vLLM and llama.cpp have no authentication. Anything that reaches them
    directly gets a model with no key, no budget and no log. Publish only the
    gateway.

## First run

Point the command line at the gateway and create an organisation:

```sh
export KEERA_CONTROL_URL=https://keera.example.ch
export KEERA_OPERATOR_KEY=…

keera org create "Example Bank" --domain example.ch
keera project create "Payments Platform"
keera key create --project "Payments Platform" --name "first key"
```

Or sign in to the panel with the operator key: on an empty gateway, the first
sign-in creates an organisation and **Getting started** guides you.

The `--domain` decides where people land when they first sign in with single
sign-on. See [Single sign-on](sign-on.md#organisations-and-domains).

Then check the models and the whole deployment:

```sh
keera model check keera-speed
keera doctor
```

## Models every organisation starts with

`KEERA_MODELS_FILE` names a YAML file with the models each new organisation
gets a copy of:

```yaml
models:
  - alias: keera-speed
    backends: [http://keera-engine:8000/v1]
    backend_model: keera-speed
    max_context_tokens: 16384
    description: Fast and local. Short edits and everyday work.

  - alias: keera-frontier
    provider: anthropic
    backend_model: claude-opus-5-5
    description: Hosted and expensive. Design and hard reasoning.
```

The file holds no API keys. Each organisation's administrator stores the key
for a hosted model, unless the gateway holds the provider's key itself (see
[Billing](../manage/billing.md)). Changing the file later does not change
existing organisations.

## Backups and upgrades

- **Back up Postgres.** It holds everything: organisations, keys, guardrails,
  the request log and the audit log.
- **To upgrade**, run the new image and restart. The gateway updates the
  database on start. Read the release notes first, and run
  `keera model check <alias>` afterwards if anything changed on the model side.
- **Retention.** By default the request log and the audit log are kept for
  ever. Set `KEERA_USAGE_RETENTION` and `KEERA_AUDIT_RETENTION` to delete old
  rows; see [Settings](settings.md#retention).
