# Keera documentation

User documentation for [Keera Gateway](https://github.com/bespinian/keera-gateway)
and Keera Chat, built with [Zensical](https://zensical.org).

```sh
pip install -r requirements.txt
python scripts/api_reference.py   # write the API reference
zensical serve                    # preview at http://localhost:8000
zensical build                    # write the site to site/
```

The pages are in `docs/`, the navigation in `zensical.toml`.
`scripts/api_reference.py` writes `docs/reference/api/` from the gateway's
OpenAPI spec, so those pages are not in Git.
`.github/workflows/docs.yml` builds the site in strict mode on every pull
request and publishes it to <https://docs.keera.ch> on every push to `main`
and once a day.

The writing rules are in [AGENTS.md](AGENTS.md).
