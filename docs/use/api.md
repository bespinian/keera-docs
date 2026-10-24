# The API

Keera Gateway speaks the APIs your tools already know. All of them live under
`/api` on the gateway's address, and all go through the same guardrails and
the same request log.

| API                     | Endpoint                             | Used by                        |
| ----------------------- | ------------------------------------ | ------------------------------ |
| OpenAI Chat Completions | `POST /api/v1/chat/completions`      | most tools and SDKs            |
| OpenAI Completions      | `POST /api/v1/completions`           | older tools, code completion   |
| OpenAI Embeddings       | `POST /api/v1/embeddings`            | search and retrieval           |
| Anthropic Messages      | `POST /api/v1/messages`              | Claude Code, the Anthropic SDK |
| Anthropic token count   | `POST /api/v1/messages/count_tokens` | Claude Code                    |
| OpenAI Responses        | `POST /api/v1/responses`             | Codex                          |
| Model list              | `GET /api/v1/models`                 | any of them                    |
| One model               | `GET /api/v1/models/<alias>`         | any of them                    |
| MCP servers             | `/api/mcp/<alias>`                   | agents that call tools         |

Put the name of a model or router in the `model` field. A chat model works
with Chat Completions, Messages and Responses: the gateway translates between
them. A completion model only works with Completions, and an embedding model
only with Embeddings.

Every endpoint and field is in the [API reference](../reference/api/index.md).

!!! note "Nothing is stored"

    The gateway keeps no conversations. With the Responses API, the client
    sends the whole conversation each time.

## Authentication

Send your key in one of these headers:

- `Authorization: Bearer keera_sk_…`
- `x-api-key: keera_sk_…`
- `X-Keera-Key: keera_sk_…`

## Headers you can send

| Header                | What it does                                                                                                                                                                      |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `X-Keera-Session`     | groups requests into one [session](../monitor/requests-and-sessions.md#how-keera-finds-a-session); `X-Session-Id`, `Helicone-Session-Id` and `X-Claude-Code-Session-Id` also work |
| `X-Keera-Client`      | names your tool in the reports, instead of its `User-Agent`                                                                                                                       |
| `X-Request-Id`        | your own id for the request, kept if it is up to 64 simple characters                                                                                                             |
| `X-Client-Request-Id` | your own id, which you know even if no answer comes back                                                                                                                          |

## Headers you get back

| Header                           | What it tells you                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `X-Keera-Model`                  | the model that answered                                                                                             |
| `X-Keera-Router`                 | the router, and where it sent the request                                                                           |
| `X-Keera-Filters`                | the filters that changed or checked the request                                                                     |
| `X-Keera-Budget-Scope`           | the level of the tightest budget: `org`, `project` or `key`                                                         |
| `X-Keera-Budget-Limit`           | that budget, in CHF                                                                                                 |
| `X-Keera-Budget-Remaining`       | money left in it, in CHF                                                                                            |
| `X-Keera-Budget-Reset`           | when it resets                                                                                                      |
| `X-RateLimit-Limit-Requests`     | the tightest rate limit, in requests per minute                                                                     |
| `X-RateLimit-Remaining-Requests` | requests left this minute                                                                                           |
| `X-Keera-RateLimit-Scope`        | the level of that limit                                                                                             |
| `X-Keera-Removed-Tools`          | tools the provider runs itself, removed on the gateway's keys; see [Billing](../manage/billing.md#the-monthly-bill) |
| `X-Keera-Removed-Fields`         | fields that cost extra, removed on the gateway's keys                                                               |
| `X-Request-Id`                   | the request's id; search for it on the Requests screen                                                              |

## Errors

Errors come in the format of the API you called. A conversation too long for
the model gets `context_length_exceeded`, which Claude Code and other agents
understand: they shorten it and retry. See [Errors](../reference/errors.md)
for every code.
