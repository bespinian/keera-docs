# Troubleshooting

## Start with `keera doctor`

```sh
keera doctor            # settings, models, organisations, filters, routers
keera doctor --probe    # and send a real request to every model
```

It reports what is set, what is missing and what does not work, each with a
fix. It changes nothing, so it is safe on a live gateway. It exits with an
error when a check fails, so it can end an install script.

## Common problems

| Symptom                                                  | Cause and fix                                                                                                                               |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| The gateway stops at once with a message about a setting | A required setting is missing or too short. The message names it.                                                                           |
| Every request to a model returns 404                     | The model's **backend model** does not match the name the server uses (vLLM's `--served-model-name`).                                       |
| Long prompts fail with a 400 from the model              | The model's context window in Keera is larger than the server's. Make them match.                                                           |
| The agent answers in prose and never edits a file        | The model returns no tool calls. Run `keera model check <alias>`. The CPU demo model cannot do tool calls.                                  |
| Streaming arrives all at once                            | A proxy in front buffers the answer. Turn buffering off.                                                                                    |
| A rate limit lets through more than it should            | With several replicas, each counts on its own. Set `KEERA_REDIS_URL`.                                                                       |
| The panel shows no sign-in button                        | Neither `KEERA_OIDC_PROVIDERS` nor `KEERA_PASSKEYS` is set. A provider the gateway cannot reach stops the start instead; see the log.       |
| `redirect_uri_mismatch` when signing in                  | The address registered with the provider differs from `KEERA_PUBLIC_URL` + `/control/auth/callback`. Often `127.0.0.1` against `localhost`. |
| Signed in, but everything is read-only                   | You are a member. Ask an administrator for `keera user role <you> admin`.                                                                   |
| "no organisation matches" at sign-in                     | No organisation has your email domain. Set it with `keera org set <org> --domain <domain>`.                                                 |

## Logs and metrics

- The gateway logs to standard output. `KEERA_LOG_LEVEL=debug` shows more.
- `/healthz` checks the process, `/readyz` also checks Postgres.
- `/metrics` serves Prometheus metrics: requests, tokens, latency, errors,
  filter and router decisions. It needs the operator key or
  `KEERA_METRICS_TOKEN`.
