"""Write the API reference pages from the gateway's OpenAPI spec.

    python scripts/api_reference.py [URL or file]

It writes docs/reference/api/index.md (the endpoints) and
docs/reference/api/schemas.md (the shared schemas). Both are generated, so
they are not in Git.
"""

import json
import sys
import urllib.request
from pathlib import Path

SPEC = "https://gateway.keera.ch/openapi.json"
OUT = Path(__file__).resolve().parent.parent / "docs" / "reference" / "api"
METHODS = ["get", "post", "put", "patch", "delete", "head"]
ACRONYMS = {"mcp": "MCP", "api": "API"}


def load(source):
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as response:
            return json.load(response)
    return json.loads(Path(source).read_text())


def resolve(spec, node):
    """Follow a $ref to its target, keeping a description given beside it."""
    if "$ref" not in node:
        return node
    target = spec
    for part in node["$ref"].removeprefix("#/").split("/"):
        target = target[part]
    if "description" in node:
        target = {**target, "description": node["description"]}
    return target


def ref_name(node):
    return node["$ref"].rsplit("/", 1)[-1]


def cell(text):
    """Text that fits in one table cell."""
    return " ".join(text.split()).replace("|", "\\|")


def collapsed(summary, lines):
    """A block that starts closed, with lines inside it."""
    body = [f"    {line}" if line else "" for line in lines]
    return [f'??? note "{summary}"', ""] + body + [""]


def title(tag):
    words = tag.replace("-", " ").split()
    words = [ACRONYMS.get(word, word) for word in words]
    return " ".join(words)[:1].upper() + " ".join(words)[1:]


class Writer:
    def __init__(self, spec, schemas_link):
        self.spec = spec
        self.schemas_link = schemas_link

    def link(self, node):
        name = ref_name(node)
        return f"[`{name}`]({self.schemas_link}#{name.lower()})"

    def type_of(self, schema):
        if "$ref" in schema:
            return self.link(schema)
        for key, word in (("allOf", " and "), ("oneOf", " or "), ("anyOf", " or ")):
            if key in schema:
                return word.join(self.type_of(part) for part in schema[key])
        if "const" in schema:
            return f"`{json.dumps(schema['const']).strip(chr(34))}`"
        kind = schema.get("type")
        if isinstance(kind, list):
            return " or ".join(kind)
        if kind == "array":
            items = schema.get("items")
            return f"array of {self.type_of(items)}" if items else "array"
        if kind == "object" and not schema.get("properties"):
            values = schema.get("additionalProperties")
            if isinstance(values, dict) and values:
                return f"map of {self.type_of(values)}"
        if kind and "format" in schema:
            return f"{kind} ({schema['format']})"
        return kind or "any"

    def notes(self, schema, required=False):
        parts = ["Required."] if required else []
        if schema.get("description"):
            parts.append(schema["description"])
        if "enum" in schema:
            parts.append("One of " + ", ".join(f"`{v}`" for v in schema["enum"]) + ".")
        if "default" in schema:
            parts.append(f"Default `{json.dumps(schema['default'])}`.")
        if schema.get("deprecated"):
            parts.append("Deprecated.")
        return cell(" ".join(parts))

    def rows(self, schema, prefix="", show_required=False):
        """One row per field, with inline objects flattened into dotted names."""
        required = set(schema.get("required", []))
        for name, field in schema.get("properties", {}).items():
            yield (
                f"`{prefix}{name}`",
                self.type_of(field),
                self.notes(field, show_required and name in required),
            )
            if "$ref" in field:
                continue
            if field.get("properties"):
                yield from self.rows(field, f"{prefix}{name}.", show_required)
            items = field.get("items", {})
            if field.get("type") == "array" and items.get("properties"):
                yield from self.rows(items, f"{prefix}{name}[].", show_required)

    def fields(self, schema, show_required=False):
        """Markdown for a body or schema: a link, a field table, or both."""
        if "$ref" in schema:
            return [f"Type: {self.link(schema)}.", ""]
        if "allOf" in schema:
            refs = [self.link(part) for part in schema["allOf"] if "$ref" in part]
            merged = {"properties": {}, "required": []}
            for part in schema["allOf"]:
                if "$ref" not in part:
                    merged["properties"].update(part.get("properties", {}))
                    merged["required"] += part.get("required", [])
            lines = [f"Everything in {' and '.join(refs)}, plus:", ""]
            return lines + self.table(merged, show_required)
        if "oneOf" in schema and any(p.get("properties") for p in schema["oneOf"]):
            lines = ["One of:", ""]
            for part in schema["oneOf"]:
                if part.get("title"):
                    lines += [f"**{part['title']}**", ""]
                lines += self.fields(part, show_required)
            return lines
        if schema.get("properties"):
            return self.table(schema, show_required)
        return [f"Type: {self.type_of(schema)}. {self.notes(schema)}".strip(), ""]

    def table(self, schema, show_required):
        lines = ["| Field | Type | Description |", "| --- | --- | --- |"]
        lines += [
            f"| {a} | {b} | {c} |" for a, b, c in self.rows(schema, "", show_required)
        ]
        return lines + [""]

    def operation(self, path, method, op, path_params):
        lines = [
            f"### {op['summary']} {{ #{op['operationId']} }}",
            "",
            f"`{method.upper()} {path}`",
            "",
        ]
        if op.get("description"):
            lines += [op["description"].strip(), ""]
        if op.get("security") == []:
            lines += ["No sign-in needed.", ""]
        if "externalDocs" in op:
            docs = op["externalDocs"]
            lines += [
                f"See [{docs.get('description', docs['url'])}]({docs['url']}).",
                "",
            ]

        params = [resolve(self.spec, p) for p in path_params + op.get("parameters", [])]
        if params:
            rows = [
                "| Parameter | In | Type | Description |",
                "| --- | --- | --- | --- |",
            ]
            for p in params:
                schema = {
                    **p.get("schema", {}),
                    "description": p.get("description", ""),
                }
                required = p.get("required") and p["in"] != "path"
                rows.append(
                    f"| `{p['name']}` | {p['in']} | {self.type_of(schema)} "
                    f"| {self.notes(schema, required)} |"
                )
            lines += collapsed("Parameters", rows)

        body = op.get("requestBody")
        if body:
            schema = body["content"]["application/json"]["schema"]
            lines += collapsed("Request body", self.fields(schema, show_required=True))

        rows = ["| Status | Description |", "| --- | --- |"]
        bodies = []
        for status, response in op["responses"].items():
            response = resolve(self.spec, response)
            text = cell(response.get("description", ""))
            content = response.get("content", {})
            schema = content.get("application/json", {}).get("schema", {})
            # A bare "object" says nothing worth a section.
            if status.startswith("2") and set(schema) - {
                "type",
                "additionalProperties",
            }:
                bodies.append((status, schema))
            other = [kind for kind in content if kind != "application/json"]
            if other:
                kinds = ", ".join(f"`{kind}`" for kind in content)
                text += f" Content: {kinds}."
            rows.append(f"| {status} | {text.strip()} |")
        rows.append("")
        for status, schema in bodies:
            rows += [f"**{status} response**", ""] + self.fields(schema)
        return lines + collapsed("Responses", rows)


def index_page(spec, writer):
    info = spec["info"]
    lines = [
        "# API reference",
        "",
        "Every endpoint of Keera Gateway, generated from its",
        "[OpenAPI spec](https://gateway.keera.ch/openapi.json). To get started,",
        "see [The API](../../use/api.md). Errors are listed in",
        "[Errors](../errors.md).",
        "",
        info.get("description", "").strip(),
        "",
    ]
    operations = {}
    for path, item in spec["paths"].items():
        for method in METHODS:
            if method in item:
                op = item[method]
                operations.setdefault(op["tags"][0], []).append(
                    (path, method, op, item.get("parameters", []))
                )
    for tag in spec.get("tags", []):
        if tag["name"] not in operations:
            continue
        lines += [f"## {title(tag['name'])}", ""]
        if tag.get("description"):
            lines += [tag["description"].strip(), ""]
        for path, method, op, path_params in operations[tag["name"]]:
            lines += writer.operation(path, method, op, path_params)
    return lines


def schemas_page(spec, writer):
    lines = [
        "# Schemas",
        "",
        "The shapes the [API reference](index.md) refers to.",
        "",
    ]
    for name, schema in spec["components"]["schemas"].items():
        lines += [f"## {name} {{ #{name.lower()} }}", ""]
        if schema.get("description") and schema.get("properties"):
            lines += [schema["description"].strip(), ""]
        fields = writer.fields(schema)
        # A one-line type is short enough to stay open.
        lines += (
            fields if fields[0].startswith("Type:") else collapsed("Fields", fields)
        )
    return lines


def main():
    spec = load(sys.argv[1] if len(sys.argv) > 1 else SPEC)
    OUT.mkdir(parents=True, exist_ok=True)
    pages = {
        "index.md": index_page(spec, Writer(spec, "schemas.md")),
        "schemas.md": schemas_page(spec, Writer(spec, "")),
    }
    for name, lines in pages.items():
        (OUT / name).write_text("\n".join(lines).rstrip() + "\n")
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
