# Claude plans

On your own gateway, people on a **Claude Team or Enterprise plan** can use
Claude Code through Keera Gateway, and their plan pays. Keera still applies the
guardrails, records every request and shows how much of the plan each person
uses.

This works for Claude Code only. Claude.ai in the browser and the desktop app
do not go through Keera.

It is off by default. Turn it on with `KEERA_CLAUDE_SUBSCRIPTIONS=true`. The
public instance at <https://gateway.keera.ch> does not offer it.

## How it works

Claude Code is signed in to the person's Claude plan, and pointed at the
gateway. Each request carries two credentials:

- the person's **Keera key**, in the `X-Keera-Key` header. Keera uses it to
  know who is asking and to apply their guardrails.
- the person's **Claude sign-in**. Keera passes it to Anthropic unchanged, and
  never stores or logs it.

## Set it up

**1. Add a subscription model** for each Claude model the plan should reach.
In the panel: **Models → Add model**, click **Add** on an Anthropic model, and
tick **Paid by each person's Claude subscription**. Or:

```sh
keera model add claude-opus --provider anthropic \
  --backend-model claude-opus-5-5 --subscription
```

**2. Point everyone's Claude Code at Keera.** An owner of the Claude
organisation sets this in the claude.ai admin console, under **Admin Settings
→ Claude Code → Managed settings**:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://keera.example.ch/api"
  }
}
```

**3. Issue each person a subscription key**, for them to activate:

```sh
keera key create --subscription --pending --user ada@example.ch --name "Ada's Claude Code"
```

**4. Each person, once per machine,** signs in to Claude Code with `/login`,
then runs:

```sh
keera login --url https://keera.example.ch
keera connect claude-code --subscription
```

## What it costs

- **Your spend is 0.** The plan pays. Budgets are not charged, except for
  filters, which still run on your own models.
- **"Covered by Claude plans"** on the dashboard shows what the same requests
  would have cost on Anthropic's API. It tells you whether the plan is worth
  it.
- **Plan use** shows on the **API keys** screen, such as
  `plan 5h 40% · 7d 12%`: the share of the plan's limit used in the last five
  hours and the last seven days.

## Limits

A subscription key reaches only subscription models. It cannot call routers,
MCP servers or the playground, and a subscription model cannot be used by a
filter or a router.
