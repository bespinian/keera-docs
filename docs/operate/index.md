# Self-host

This part is for **operators**: whoever runs a Keera Gateway of their own. To
use the public instance at <https://gateway.keera.ch>, you can skip it.

The gateway is one static program, and Postgres is all it needs. Optional:
Redis to share rate limits between replicas, an identity provider for single
sign-on, and Kubernetes for sandboxes.

1. [Install](install.md) the gateway, put TLS in front, and create the first
   organisation. To try it on your laptop, start with
   [compose](install.md#one-host-with-compose).
2. Set up [single sign-on or passkeys](sign-on.md), so people sign in as
   themselves.
3. To give everyone a chat in the browser, [run Keera Chat](chat.md).
   To let a Claude plan pay for Claude Code, set up
   [Claude plans](claude-plans.md).
4. Look up any setting in [Settings](settings.md).
5. When something does not work, start with
   [Troubleshooting](troubleshooting.md).

Operators work in every organisation. The role comes only from the gateway's
settings, never from the panel; see [Roles](sign-on.md#roles). Before single
sign-on is set up, the operator key is the way in.

The panel's **Organisations** screen is for operators. It lists every
organisation, and creates, edits and deletes them. It also lifts the limit of
an organisation that [signed up](sign-on.md#organisations-and-domains) on its
own, as `keera org set --lift-limit` does.
