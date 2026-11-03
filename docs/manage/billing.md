# Billing

On <https://gateway.keera.ch>, the gateway holds **its own key** for each
hosted provider. Every organisation uses it, and Keera bills each one for what
it used, at the provider's list price. Models of those providers take no API
key of your own. Only administrators see **Billing**.

## The monthly bill

**Billing** shows one row per provider model, with calls, tokens and the
amount in CHF. Prices a provider lists in USD are converted at a fixed rate.
Rows marked **gateway fee** are for [your own models](#the-gateway-fee).
**CSV** downloads it.

```sh
keera billing                  # this month
keera billing --month 2026-09
```

## What is fixed or turned off

On the gateway's own keys, the model's address and prices are fixed. Tools
that the provider runs itself, such as web search, are removed. Faster or
dearer modes are turned off.

## The gateway fee

A model that does not use the gateway's keys, such as a
[self-hosted one](models.md#add-your-own-model), can cost a **gateway fee**:
a fixed price per million tokens, for passing through the gateway. Keera sets
it. Every token costs the same: input, output or cached. The model form shows
the fee under **Advanced options**.

## Pay in advance

Your organisation buys credit before it uses the gateway's keys. Each call
takes its price from the credit, and so does the gateway fee. When the credit
is used up, calls that cost money are refused with `402 credit_exhausted`.

**Add credit** in **Billing**, or:

```sh
keera billing topup --amount 100
```

You pay on PostFinance's page, by card, TWINT or PostFinance Pay. Keera never
sees the card. A payment is from CHF 1 to CHF 10,000; VAT and a small
transaction fee are added on top, and the panel shows both before you pay.

### Top up automatically

With a saved card, the organisation can top up by itself:

```sh
keera billing topup --amount 100 --save-card
keera billing auto-topup --below 50 --amount 200
```

When the credit falls below CHF 50, the card is charged CHF 200.

| Command                          | What it does                            |
| -------------------------------- | --------------------------------------- |
| `keera billing credit`           | balance, saved card and latest payments |
| `keera billing payments`         | the latest payments                     |
| `keera billing receipt <id>`     | downloads a payment's receipt as a PDF  |
| `keera billing auto-topup --off` | turns automatic top-up off              |
| `keera billing forget-card`      | removes the saved card                  |

## Recurring charges

A dedicated or enterprise plan may come with a fixed fee every month or year,
such as for a dedicated model. Keera sets it up. It shows under **Recurring
charges** in **Billing**, and is charged to the saved card when each period
starts. VAT and the transaction fee are added on top. It is not added to your
credit.

Such a plan needs a saved card. While a period is due and no saved card can
pay it, because there is none or it was declined, **every call** of the
organisation is refused with `402 charge_due`, your own models too.

**Pay now** in **Billing** pays the period and saves the card for the periods
after. Do it before the first period starts, and nothing stops.

```sh
keera billing charges                  # the charges and when each is next due
keera billing pay-charge <charge>      # prints the payment page
```

A card that pays recurring charges cannot be forgotten. To use another card,
pay with it and save it: it replaces the old one.

## New organisations

An organisation that signed itself up starts **limited**, with no credit.
Until its first payment, it can use only
[its own models](models.md#add-your-own-model) and MCP servers on public
addresses, nothing inside the gateway's private network. Calls that cost
money, the gateway fee too, also need credit.

The first payment lifts the limit. Credit that Keera grants
can be used, but does not lift the limit. A banner in the panel says what is
still waiting.
