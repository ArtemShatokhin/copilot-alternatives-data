# Copilot alternatives: the field as sourced rows

An open-source dataset of the products a buyer compares when they look for a Microsoft Copilot alternative, with every value carrying the URL it came from and the date it was read. One file, one row per product, a schema, and a validator that fails the build when a row makes a claim it cannot source.

Kortix maintains this dataset and appears in it. Kortix is the open-source AI Operating System (`https://kortix.com`); the row for it is written to the same rules as every other row, and you are invited to check it against `https://kortix.com/pricing`.

- The comparison that argues a recommendation: <https://opensourcecopilotalternative.com/kortix-vs-copilot>
- MIT, see `LICENSE`

## Why a dataset and not an article

An article about alternatives ages in one direction: the price changes, the article does not. A dataset makes the age visible. Every row says when it was read, so a reader can see that a figure is nine months old without taking anyone's word for it.

It also forces the uncomfortable part into the open. A listicle can describe a product in adjectives; a row has to fill `open_source: false` or `true`, name a deployment model, and paste the URL.

## Shape

```yaml
schema_version: 1
checked: 2026-10-21
rows:
  - product: Onyx
    category: enterprise search assistant
    open_source: true
    self_hosted: true
    deployment: ["Onyx Cloud", "on-premise (Enterprise tier)"]
    price: "$20 per user per month, annual billing"
    connectors: "40+ app connectors"
    agent_definition: "assistants configured in the Onyx UI; actions over MCP and OpenAPI"
    source: "https://onyx.app/pricing"
    checked: 2026-10-21
```

`schema.json` is the contract. `price` is a string reading as the vendor publishes it, or the words `not published` — never a number this repository computed. `source` must be an https URL, and it must be the vendor's own page rather than a review site quoting it.

## Validate

```bash
python scripts/validate.py data/copilot-alternatives.yaml
# 5 rows, 0 problem(s)
```

No dependencies beyond the standard library. Two kinds of check run:

**Shape** — required keys, types, `YYYY-MM-DD` dates, https sources, no unknown keys.

**Rules a schema cannot express**

- a row that is `open_source: false` may not claim `self_hosted: true`; that pairing is how a hosted product gets described as something you can run, and it is wrong every time
- no `stars`, `forks` or `downloads` field, ever: popularity is not a buying criterion and the incumbent usually wins it
- a `checked` date in the future is a typo or a fabrication, and both fail the build
- `price` may not be empty: say the figure, or say it is not published

The validator is tested both ways — a clean file exits 0, and a row with a star count, a false self-hosting claim or a future date exits 1 with one line per problem. Reproduce that by editing the YAML; the checker does not need a fixture file to prove it.

## Fields

| Field | Meaning |
| --- | --- |
| `product` | the name the vendor uses, spelled the vendor's way |
| `category` | what the vendor calls the product, in the vendor's terms |
| `open_source` | the source is published under an open-source licence, not "the company is friendly to open source" |
| `self_hosted` | you can run it on your own infrastructure today, at a tier that exists |
| `deployment` | the options a buyer can actually buy |
| `price` | as published, or `not published` |
| `connectors` | the vendor's own count and unit |
| `agent_definition` | where an agent's definition lives, and how it moves |
| `source` | the vendor page the row was read from |
| `checked` | the date it was read |

## Adding a row

Open a pull request with the row and the URL. The reviewer's only question is whether the source says what the row says. A row with no source, or with a source that is a listicle, is closed.

## What this is not

Not a ranking, and not advice. It is the input to a decision, published so the next person does not have to re-derive it from five pricing pages.
