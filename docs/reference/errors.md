# Errors

Errors come in the format of the API you called. The OpenAI APIs carry a
`code`, listed below. The Anthropic Messages API has no field for a code, so
its errors carry a type that follows the status, such as `billing_error` for
402, and the message says the rest.

| Status | Code                                                     | What it means                                                                    |
| ------ | -------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 400    | `context_length_exceeded`                                | The conversation is too long for the model. Agents shorten it and retry.         |
| 400    | `missing_model`, `invalid_body`, `unsupported_parameter` | The request is not valid.                                                        |
| 400    | `subscription_model`                                     | A Claude plan model only answers the Anthropic Messages API.                     |
| 400    | `router_undecided`                                       | A header step got no value it knows. The message lists the values.               |
| 401    | `missing_api_key`, `invalid_api_key`                     | No key, or a key the gateway does not know.                                      |
| 401    | `expired_api_key`, `revoked_api_key`                     | The key has expired or was revoked. Get a new one.                               |
| 401    | `subscription_key`, `missing_claude_sign_in`             | A [Claude plan](../operate/claude-plans.md) request is set up wrong.             |
| 402    | `budget_exceeded`                                        | A budget is used up. The message says when it resets.                            |
| 402    | `credit_exhausted`                                       | The prepaid credit is used up. See [Billing](../manage/billing.md).              |
| 403    | `filter_refused`                                         | A filter stopped the request. The message gives its reason.                      |
| 403    | `org_limited`                                            | The organisation must pay once before it can use this.                           |
| 403    | `subscriptions_off`                                      | The gateway does not take Claude plans.                                          |
| 404    | `model_not_found`                                        | No such model, or the key may not use it.                                        |
| 404    | `not_found`                                              | No such path under `/api`.                                                       |
| 404    | `wrong_base_url`                                         | The client's base URL is missing `/api`.                                         |
| 404    | `mcp_server_not_found`                                   | No such MCP server, or the key may not use it.                                   |
| 413    | `request_too_large`                                      | The request is larger than the gateway accepts.                                  |
| 413    | `filter_input_too_large`                                 | The request is too long for a filter's model.                                    |
| 415    | `unsupported_encoding`                                   | The body is compressed other than with gzip or deflate.                          |
| 429    | `rate_limit_exceeded`, `token_rate_limit_exceeded`       | Too many requests or tokens this minute. Wait for `Retry-After`.                 |
| 429    | `requests_quota_exceeded`, `tokens_quota_exceeded`       | The daily or monthly limit is used up.                                           |
| 502    | `upstream_unavailable`, `upstream_error`                 | The model could not be reached, or failed.                                       |
| 502    | `filter_failed`                                          | A filter's model failed, so the request was stopped.                             |
| 502    | `mcp_unavailable`                                        | The MCP server could not be reached, or its answer could not be read.            |
| 502    | `mcp_credential_refused`                                 | The MCP server refused the gateway's credential. An administrator sets it again. |
| 503    | `no_backend`, `filter_unavailable`                       | A model or filter cannot run right now.                                          |
| 503    | `router_undecided`                                       | A route step could not choose, and it has no fallback.                           |
| 503    | `router_destination_unavailable`                         | None of the router's models can take the request.                                |
| 503    | `router_unavailable`                                     | A router names something it can no longer use. An administrator fixes it.        |
| 503    | `control_plane_unavailable`                              | The gateway lost its database for longer than its cache lasts.                   |
