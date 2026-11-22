# Install the gateway

## What you need

- **Postgres 14 or later.** The gateway creates and updates its tables itself
  when it starts. Several replicas can start at once.
- **Two secrets**, each at least 16 characters:

  ```sh
  openssl rand -hex 32   # KEERA_OPERATOR_KEY: the operator's credential
  openssl rand -hex 32   # KEERA_SECRET_KEY: encrypts stored provider keys
  ```

- **A TLS terminator** in front, such as an ingress or a reverse proxy.
- **The [`keera` CLI](../reference/cli/index.md)**, to set it up.

The image is `ghcr.io/bespinian/keera-gateway:<version>`. Every setting is an
environment variable; see [Settings](settings.md).

On Kubernetes, use the [Helm chart](kubernetes.md#keera-gateway). On one
host, use compose.

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

This starts four containers:

| Container       | What it is                                                                           |
| --------------- | ------------------------------------------------------------------------------------ |
| `keera-gateway` | the gateway, at <http://localhost:8080>                                              |
| `keera-db`      | Postgres                                                                             |
| `keera-engine`  | a small coding model on the CPU, `keera-speed`: Keera Engine on llama.cpp            |
| `keera-decider` | Keera Decider, a small [decision model](../manage/models.md#model-kinds) for routers |

The model downloads on the first start; watch it with
`podman compose logs -f keera-engine`. Every other setting in `.env` reaches
the gateway, except the database, the models file and the port, which compose
sets itself.

Open <http://localhost:8080> and sign in with the operator key. Then continue
with [First run](#first-run). The port listens on `127.0.0.1` only. To reach
it from other machines, set `KEERA_BIND=0.0.0.0` in `.env`, behind TLS.

!!! note "The CPU model cannot make tool calls"

    It can chat, but coding agents need tool calls to edit files. For those,
    use a GPU.

On a host with an NVIDIA GPU, use vLLM instead:

```sh
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml   # once
podman compose -f compose.yaml -f compose.gpu.yaml up -d --build
```

Every later `podman compose` command needs the same two `-f` flags. The
default GPU model is Qwen2.5-Coder-7B, about 5.6 GB, which fits a 24 GB card.

Settings only compose reads:

| Variable                                | What it is                                                        |
| --------------------------------------- | ----------------------------------------------------------------- |
| `KEERA_BIND`                            | the interface port 8080 listens on, `127.0.0.1` by default        |
| `KEERA_LLAMA_MODEL`, `KEERA_GPU_MODEL`  | the model on the CPU and on the GPU, as a Hugging Face repository |
| `KEERA_LLAMA_IMAGE`, `KEERA_VLLM_IMAGE` | the images of llama.cpp and vLLM                                  |
| `KEERA_SHM_SIZE`                        | `/dev/shm` for vLLM, `8gb` by default                             |

`podman compose down` stops it. Add `-v` to delete the database and the
downloaded models too.

## Publish it

One port, `8080`, carries everything. Paths tell the parts apart:

| Path       | What it is                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------ |
| `/api`     | the inference API and MCP servers, for API keys                                            |
| `/control` | the control API, for the panel and `keera`                                                 |
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

Point the CLI at the gateway and create an organisation:

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
keera model check <alias>   # each model
keera doctor
```

## Models every organisation starts with

`KEERA_MODELS_FILE` names a YAML file with the models each new organisation
gets a copy of. The format is in
[Models](../manage/models.md#add-models-from-a-file). Compose uses
`compose/models.yaml`.

The file holds no API keys. Each organisation's administrator stores the key
for a hosted model, under **Provider key** or with
`keera model set <alias> --api-key @-`. That is not needed when the gateway
holds the provider's key itself; see
[Hosted providers and billing](settings.md#hosted-providers-and-billing).
Changing the file later does not change existing organisations;
`keera model apply` adds its models to one.

## Back up

Back up Postgres. It holds everything: organisations, keys, guardrails, the
request log, the audit log and the bill. Keep `KEERA_SECRET_KEY` apart from it,
in your secret store: without it, stored provider keys cannot be read.

By default the request log and the audit log are kept for ever. Set
`KEERA_USAGE_RETENTION` and `KEERA_AUDIT_RETENTION` to delete old rows; see
[Retention](settings.md#retention).

## Upgrade

Run the new image and restart. The gateway updates the database as it starts.
Then run `keera model check <alias>` if anything changed on the model side.

Read the release notes first. Releases that need more than a restart:

| Release | What to do                                                                                                                                                                                   |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| v0.14.0 | A rewrite filter can no longer refuse. One whose instruction tells it to refuse fails with `502`. Move that part into a [gate](../manage/filters.md#three-kinds-of-filter) placed before it. |
| v0.13.0 | Sandboxes are gone; [Keera Agents](agents.md) replaces them. Remove leftover sandbox pods or containers yourself. `KEERA_SANDBOX_*` and `keera sandbox` are gone.                            |
| v0.11.0 | Routers are replaced: write them again. `keera guardrail set` takes `--requests` and `--tokens` with `--per`, instead of `--rpm` and `--tpm`. The output-token guardrail is gone.            |
| v0.10.0 | `max_context` is now `max_context_tokens`, in model files, the API and the CLI. Upgrade to v0.10.0 before you shorten `KEERA_USAGE_RETENTION`.                                               |
| v0.4.0  | A database created before v0.4.0 cannot be upgraded. Start from an empty one.                                                                                                                |
