# Settings

The gateway reads every setting from environment variables. Durations take
`h`, `m` and `s`, such as `720h`. Lists are separated by commas; group lists
of an LDAP directory by `;`, because its names hold commas.

Most numbers, durations and on/off values the gateway cannot read, such as
`365d`, are ignored without a warning, and the default applies. Other values
that cannot work, such as a wrong sign-on setup, stop the start with a message
that names the setting.

## Required

| Variable             | What it is                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `KEERA_DATABASE_URL` | The Postgres connection string.                                                                                           |
| `KEERA_OPERATOR_KEY` | The operator's credential, for the first sign-in and for automation. 16+ characters.                                      |
| `KEERA_SECRET_KEY`   | Encrypts stored provider keys and directory tokens. 16+ characters. Keep it safe: without it, stored keys cannot be read. |

To change `KEERA_SECRET_KEY`, set the old one as `KEERA_SECRET_KEY_PREVIOUS`
and restart. The gateway encrypts everything again with the new key. Once
every replica runs with it, restart once more, then remove
`KEERA_SECRET_KEY_PREVIOUS`.

## Recommended

| Variable                 | Default                              | What it is                                                                                                       |
| ------------------------ | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `KEERA_PUBLIC_URL`       | the request's host                   | The address people open, such as `https://keera.example.ch`. Required for single sign-on, passkeys and payments. |
| `KEERA_MODELS_FILE`      | none                                 | The models each new organisation starts with. See [Install](install.md#models-every-organisation-starts-with).   |
| `KEERA_METRICS_TOKEN`    | none                                 | A token that may read `/metrics` and nothing else. 16+ characters, and not the operator key.                     |
| `KEERA_USAGE_RETENTION`  | for ever                             | How long the request log is kept. See [Retention](#retention).                                                   |
| `KEERA_AUDIT_RETENTION`  | for ever                             | How long the audit log is kept.                                                                                  |
| `KEERA_UPSTREAM_PRIVATE` | `all`                                | The host names inside your network that organisations may reach, such as `keera-engine,keera-decider`.           |
| `KEERA_UPSTREAM_DENY`    | loopback, link-local, cloud metadata | Addresses no model or MCP server may use. A backend on `127.0.0.1` needs `none` or a shorter list.               |

## Sign-in

| Variable                                                                 | What it is                                                               |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `KEERA_OIDC_PROVIDERS`                                                   | The names of the identity providers.                                     |
| `KEERA_OIDC_<NAME>_LABEL`                                                | The text on the provider's sign-in button.                               |
| `KEERA_OIDC_<NAME>_ISSUER`                                               | The provider's address, or an `ldaps://` or `ldap://` directory.         |
| `KEERA_OIDC_<NAME>_CLIENT_ID`, `_CLIENT_SECRET`                          | The client registered with the provider.                                 |
| `KEERA_OIDC_<NAME>_SCOPES`                                               | What Keera asks the provider for. See [Roles](sign-on.md#roles).         |
| `KEERA_OIDC_<NAME>_LDAP_BIND_DN`, `_LDAP_BIND_PASSWORD`, `_LDAP_BASE_DN` | The service account and search base for a directory.                     |
| `KEERA_OIDC_<NAME>_LDAP_CA_FILE`                                         | A PEM file of the CAs to trust for a directory, instead of the system's. |
| `KEERA_OIDC_<NAME>_LDAP_USER_FILTER`                                     | Who in the directory may sign in. The default depends on the directory.  |
| `KEERA_OIDC_<NAME>_LDAP_LOGIN_ATTRIBUTES`                                | What a person may type as their username, such as `sAMAccountName,mail`. |
| `KEERA_OIDC_<NAME>_DOMAINS`                                              | The email domains this provider may sign people in with.                 |
| `KEERA_OIDC_<NAME>_GROUPS_CLAIM`                                         | The claim that holds the groups, such as `roles`.                        |
| `KEERA_OIDC_<NAME>_ADMIN_GROUPS`                                         | Groups whose members are administrators.                                 |
| `KEERA_OIDC_<NAME>_OPERATOR_GROUPS`                                      | Groups whose members are operators.                                      |
| `KEERA_OIDC_<NAME>_DEFAULT_ROLE`                                         | The role of people in no admin or operator group.                        |
| `KEERA_OIDC_<NAME>_SIGNUP`                                               | Lets people create their own organisation.                               |
| `KEERA_OPERATORS`                                                        | Email addresses that are operators.                                      |
| `KEERA_PASSKEYS`                                                         | Turns on passkeys.                                                       |
| `KEERA_CHAT_URL`                                                         | Lets people sign in to [Keera Chat](chat.md) at this address.            |

See [Single sign-on and passkeys](sign-on.md).

## Traffic

| Variable                                | Default        | What it is                                                                                            |
| --------------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------- |
| `KEERA_ADDR`                            | `:8080`        | The address and port to listen on.                                                                    |
| `KEERA_MAX_BODY_BYTES`                  | 32 MiB         | The largest request, in bytes.                                                                        |
| `KEERA_MAX_RESPONSE_BYTES`              | 64 MiB         | The largest answer the gateway reads in one piece, and the largest streamed event.                    |
| `KEERA_UPSTREAM_HEADER_TIMEOUT`         | `2m`           | How long a model may take to start answering.                                                         |
| `KEERA_REDIS_URL`                       | none           | Shares per-minute rate limits between several gateway replicas.                                       |
| `KEERA_REDIS_PREFIX`                    | `keera`        | The prefix of Keera's Redis keys, so two deployments can share one Redis.                             |
| `KEERA_CACHE_TTL`                       | `30s`          | How long a checked API key is reused before the gateway checks it again.                              |
| `KEERA_SPEND_REFRESH`                   | `10s`          | How often each replica reads spend again, so how stale a budget may be.                               |
| `KEERA_MAX_DB_CONNS`                    | `16`           | Postgres connections per replica. At least `4`.                                                       |
| `KEERA_TRUSTED_PROXIES`                 | private ranges | The proxies in front whose `X-Forwarded-For` is trusted.                                              |
| `HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY` | none           | A proxy for requests to models and MCP servers. The proxy then has to block private addresses itself. |
| `KEERA_SESSION_GAP`                     | `30m`          | The pause that ends one task and starts the next. At least `1m`.                                      |
| `KEERA_UI`                              | `true`         | Serves the control panel. Turn off to offer only the API.                                             |
| `KEERA_SECURE_COOKIES`                  | on for https   | Marks the panel's sign-in cookie `Secure`.                                                            |
| `KEERA_LOG_LEVEL`                       | `info`         | `debug`, `info`, `warn` or `error`.                                                                   |
| `KEERA_LOG_FORMAT`                      | `text`         | `text` or `json`.                                                                                     |

## Hosted providers and billing

| Variable                                                      | What it is                                                                                                                                                                                                                       |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `KEERA_PROVIDER_<NAME>_API_KEY`                               | The gateway's own key for a provider, such as `KEERA_PROVIDER_ANTHROPIC_API_KEY`. Every organisation then uses it, at list price, and the panel shows **Billing**. Infomaniak also needs `KEERA_PROVIDER_INFOMANIAK_PRODUCT_ID`. |
| `KEERA_BILLING_POSTFINANCE_SPACE_ID`, `_USER_ID`, `_AUTH_KEY` | Turns on card payments through PostFinance Checkout.                                                                                                                                                                             |
| `KEERA_BILLING_POSTFINANCE_URL`                               | PostFinance Checkout's address. The default, `https://checkout.postfinance.ch`, serves test spaces too.                                                                                                                          |
| `KEERA_BILLING_VAT`                                           | VAT added to each payment, in percent.                                                                                                                                                                                           |
| `KEERA_CLAUDE_SUBSCRIPTIONS`                                  | Lets Claude Code on a Claude plan through. See [Claude plans](claude-plans.md).                                                                                                                                                  |

## Sandboxes

Sandboxes are off unless `KEERA_SANDBOX_DRIVER` is set.

| Variable                                    | What it is                                                                                                             |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `KEERA_SANDBOX_DRIVER`                      | `kubernetes` for real use, `podman` for local development.                                                             |
| `KEERA_SANDBOXES_FILE`                      | The sandbox classes each new organisation starts with.                                                                 |
| `KEERA_SANDBOX_NAMESPACE`                   | The Kubernetes namespace for sandboxes. Use one of their own.                                                          |
| `KEERA_SANDBOX_PUBLIC_URL`                  | The gateway as a sandbox reaches it, usually the in-cluster service.                                                   |
| `KEERA_SANDBOX_RUNTIME_ISOLATED`, `_VM`     | The runtime classes for gVisor and Kata.                                                                               |
| `KEERA_SANDBOX_GIT_FORGE`                   | `github` or `gitlab`, for repository access.                                                                           |
| `KEERA_SANDBOX_GIT_APP_ID`, `_APP_KEY_FILE` | The GitHub App, required for `github`.                                                                                 |
| `KEERA_SANDBOX_GIT_TOKEN_FILE`              | The access token, required for `gitlab`.                                                                               |
| `KEERA_SANDBOX_GIT_URL`                     | GitHub Enterprise's API (`https://<host>/api/v3`), or your GitLab instance.                                            |
| `KEERA_SANDBOX_IMAGES`                      | Image prefixes administrators may give a class, such as `registry.internal/keera/`.                                    |
| `KEERA_SANDBOX_IDLE_SUSPEND`                | Suspends an engineer's sandbox after this long without a connection. At least `5m`.                                    |
| `KEERA_SANDBOX_STORAGE_CLASS`               | On Kubernetes, the storage class of a sandbox's disk.                                                                  |
| `KEERA_SANDBOX_SERVICE_ACCOUNT`             | On Kubernetes, the service account a sandbox runs as. Its token is never mounted.                                      |
| `KEERA_SANDBOX_IMAGE_PULL_SECRETS`          | On Kubernetes, the pull secrets for images in a private registry.                                                      |
| `KEERA_SANDBOX_WARM`                        | On Kubernetes, keeps machines started, so a new sandbox is ready at once. Needs the agent-sandbox warm-pool extension. |
| `KEERA_SANDBOX_PODMAN_BINARY`, `_NETWORK`   | With `podman`, the command to run and the network sandboxes join.                                                      |

An administrator can give a class the image of a class from
`KEERA_SANDBOXES_FILE`, an image under `KEERA_SANDBOX_IMAGES`, or the image the
class already has. Any other image needs an operator, because sandboxes pull
with the deployment's credentials.

## Retention

By default, Keera deletes nothing: reports read the request log, and
compliance reads the audit log.

```sh
KEERA_USAGE_RETENTION=720h      # keep 30 days of the request log
KEERA_AUDIT_RETENTION=17520h    # keep two years of the audit log
```

Values below `24h` are refused. Daily totals are always kept, so usage charts
over long periods still work after old requests are deleted. A request log row
is about 1 KB with its indexes.
