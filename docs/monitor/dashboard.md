# Dashboard and usage

## Dashboard

The **Dashboard** shows the last 24 hours, 7 days or 30 days at a glance:
requests, tokens, cost and the time to the first token, the traffic over time,
and the projects and models that use the most.

![The dashboard](../assets/images/dashboard.webp){ .screenshot }

## Usage

**Usage** breaks the numbers down by project, model, client, key, user or day.
Pick a breakdown and a time window. **CSV** downloads the table.

![The usage report, by project](../assets/images/usage.webp){ .screenshot }

The same report on the command line:

```sh
keera usage --by project
keera usage --by model --since 30d
keera usage --by client
```

## What a cost means

Costs come from the prices set on each model, in CHF.

- For a hosted model, this is the provider's list price; see
  [Billing](../manage/billing.md).
- For your own models, it is the price
  [set on the model](../manage/models.md#add-your-own-model).
- A request cut off by the client is charged on an estimate, and marked as
  such in the request log.
