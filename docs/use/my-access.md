# My access

**My access** is your own page in the panel. It shows each of your keys, and
for each one:

- the project it belongs to, when it was last used and when it expires
- this month's requests and spend
- how much of the budget is used, and when the budget resets
- the models it may call
- the instructions added before your messages, if any
- the filters that check its requests

Below the keys, it lists the requests that were refused or failed in the last
7 days, with the reason.

![My access shows your keys, your budget and why requests were refused.](../assets/images/my-access.webp){ .screenshot }

## Activate a key

An administrator can issue a key for you without seeing its secret. It shows
as **Not activated** until you activate it. Click **Activate** on My access,
and copy the secret: it is shown only once. Or run:

```sh
keera key activate <key>   # its name or id
```

For Claude Code, let `keera connect claude-code` activate the key instead;
see [Connect your tools](connect.md#claude-code).

## Rotate or revoke a key

On the **API keys** screen, or with `keera key rotate` and `keera key revoke`.
My access also has **Revoke**.

- **Rotate** replaces a key with a new one in the same project, with the same
  guardrails and the same lifetime, counted from now. The old key stops
  working at once. Do this when a key may have
  leaked.
- **Revoke** stops a key for good.

Only administrators issue new keys. Ask yours when you need one.

## My clients

**My clients** lists the tools that sent requests with your keys, such as
Claude Code or Codex, and which key each one used. **Connect client** shows
how to set up another one. See [Connect your tools](connect.md).

## When a request is refused

Your tool shows the message the gateway sent. The most common reasons:

| Message says                 | What to do                                                                                                         |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| budget exceeded (402)        | The budget is used up. It resets on the date shown. Ask an administrator for more.                                 |
| credit exhausted (402)       | The organisation's prepaid credit is used up. An administrator [adds credit](../manage/billing.md#pay-in-advance). |
| rate limit (429)             | Too many requests in a short time. Wait a moment; the tool usually retries.                                        |
| refused by a filter (403)    | A filter found something that may not be sent, such as a password. Remove it and try again.                        |
| needs to add credit (403)    | The organisation is [new and limited](../manage/billing.md#new-organisations). An administrator adds credit.       |
| model not found (404)        | The key may not use this model, or the name is wrong. Check the models on My access.                               |
| key expired or revoked (401) | Ask for a new key, or activate the one waiting for you.                                                            |

[Errors](../reference/errors.md) lists every error code.
