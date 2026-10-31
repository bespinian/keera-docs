---
title: Keera
hide:
  - navigation
---

# Keera

![Keera walking through a gateway](assets/images/keera-gateway.webp){ .hero-keera align=right width="240" }

**One endpoint for every AI request.** Keera is an AI stack run in
Switzerland. Its core is **Keera Gateway**, which sits between your tools and
the models they use. Every request passes through it, so you decide who
may use which model, how much they may spend, and what may leave the
gateway's private network.

## What it does

- **One address for every tool.** Claude Code, Codex, OpenCode, notebooks and
  your own apps all use the same URL and their own key.
- **Your models and hosted ones.** Serve open models on your own GPUs, and add
  hosted models from Anthropic, OpenAI, Google, Mistral or Swiss providers next
  to them.
- **Guardrails.** Choose the models, budgets and rate limits for each
  organisation, project and key.
- **Filters.** Remove credentials and personal data from a request before it
  leaves, or stop the request.
- **Routers.** Send small tasks to a private model and hard ones to a large
  hosted model, automatically.
- **A chat for everyone.** [Keera Chat](use/chat.md) at chat.keera.ch, under
  the same guardrails.
- **A full record.** Every request is logged with its cost and outcome. No
  prompt is ever stored.

## Where to start

<!-- prettier-ignore-start -->

<div class="grid cards" markdown>

-   :lucide-rocket: **New to Keera?**

    ---

    Sign in at gateway.keera.ch and send a first request in five minutes.

    [:lucide-arrow-right: Quickstart](get-started/quickstart.md)

-   :lucide-laptop: **Developer?**

    ---

    Sign in and connect Claude Code, Codex or any other tool.

    [:lucide-arrow-right: Connect your tools](use/connect.md)

-   :lucide-shield-check: **Administrator?**

    ---

    Add models, issue keys and set guardrails for your teams.

    [:lucide-arrow-right: Manage your organisation](manage/index.md)

-   :lucide-server: **Running your own?**

    ---

    Install the gateway on your own hardware and set up single sign-on.

    [:lucide-arrow-right: Self-host](operate/index.md)

</div>

<!-- prettier-ignore-end -->

## More of Keera

Besides the gateway and the chat, Keera has **Keera Engine**, which serves
open-weight coding models on your own GPUs or on Swiss ones. Learn more on
[keera.ch](https://keera.ch).
