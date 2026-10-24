# Billing

On <https://gateway.keera.ch>, the gateway holds **its own key** for each
hosted provider. Every organisation uses it, and Keera bills each one for what
it used, at the provider's list price. Only administrators see **Billing**.

Models of those providers take no API key of your own.

## The monthly bill

**Billing** shows one row per provider model, with calls, tokens and the
amount in CHF. **CSV** downloads it.

```sh
keera billing                  # this month
keera billing --month 2026-09
```

On the gateway's own keys, the model's address and prices are fixed, tools
that the provider runs itself (such as web search) are removed, and faster or
dearer modes are turned off.

## Pay in advance

Your organisation buys credit before it uses the gateway's keys. Each call
takes its price from the credit. When the credit is used up, calls to those
models are refused with `402 credit_exhausted`. Your own models keep working.

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

## New organisations

An organisation that signed itself up starts **limited**: it can use models
on the gateway's keys and models on public addresses, but not models or MCP
servers inside the gateway's network, nor sandboxes. The limit lifts with the
first payment. A banner in the panel says what is still waiting.
