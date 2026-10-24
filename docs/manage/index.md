# Manage your organisation

This part is for **administrators**. An administrator runs one organisation:
its people, projects, keys, models and guardrails.

Everything here works in the panel and with the `keera` CLI. Commands act
on the organisation you work in; see `keera org switch`.

A good order to set up a new organisation:

1. [Add credit](billing.md#pay-in-advance). A new organisation is limited
   until its first payment.
2. [Add models](models.md) beyond the ones you start with.
3. [Create projects](projects-and-keys.md) for your teams.
4. [Add people](users.md) and give them keys.
5. [Set guardrails](guardrails.md): which models each project may use, and
   how much it may spend.
6. Add [filters](filters.md) before any prompt goes to a hosted model.

Then, if you need them:

- [Routers](routers.md) pick a model for each request.
- [MCP servers](mcp.md) give agents tools, under the same controls.
- [Sandboxes](sandboxes.md) lend machines for coding agents.

!!! info "Routers, filters, MCP and sandboxes are folded away"

    Until your organisation uses them, these screens are folded into one entry
    at the bottom of the sidebar's Organisation group, named after them. Click
    it to show them all. A screen you use stays in the sidebar.
