"""Write the CLI command reference from the keera command's own help.

    python scripts/cli_reference.py [path to keera]

Without a path, it downloads the latest keera release for this machine from
GitHub and checks it against the release's SHA256SUMS. It writes
docs/reference/cli/commands.md, which is generated, so it is not in Git.
"""

import hashlib
import io
import os
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO = "https://github.com/bespinian/keera-gateway"
DOCS = Path(__file__).resolve().parent.parent / "docs"
OUT = DOCS / "reference" / "cli" / "commands.md"
SITE = "https://docs.keera.ch/"


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.geturl(), response.read()


def download(directory):
    """Download the latest keera release for this machine, and check it."""
    final, _ = fetch(f"{REPO}/releases/latest")
    tag = final.rstrip("/").rsplit("/", 1)[-1]
    system = platform.system().lower()
    arch = {"x86_64": "amd64", "aarch64": "arm64"}.get(
        platform.machine().lower(), platform.machine().lower()
    )
    name = f"keera_{tag}_{system}_{arch}.tar.gz"
    _, archive = fetch(f"{REPO}/releases/download/{tag}/{name}")
    _, sums = fetch(f"{REPO}/releases/download/{tag}/SHA256SUMS")
    want = {
        line.split()[1].lstrip("*"): line.split()[0]
        for line in sums.decode().splitlines()
        if line.strip()
    }.get(name)
    if want != hashlib.sha256(archive).hexdigest():
        sys.exit(f"{name} does not match its SHA256SUMS entry")
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        member = next(m for m in tar.getmembers() if m.name.endswith("/keera"))
        path = Path(directory) / "keera"
        path.write_bytes(tar.extractfile(member).read())
    path.chmod(0o755)
    return path


class Help:
    """One `keera help ...` text, split into its parts."""

    def __init__(self, text):
        lines = text.rstrip().splitlines()
        self.name, _, self.summary = lines[0].partition(" - ")
        self.usage, self.flags, self.examples = [], [], []
        self.aliases = ""
        self.description = []
        part = "description"
        for line in lines[1:]:
            if line in ("Usage:", "Flags:", "Examples:"):
                part = line[:-1].lower()
                continue
            if line.startswith("Also accepted: "):
                self.aliases = line.removeprefix("Also accepted: ")
                part = "description"
                continue
            if line.startswith(("Flags for one of them:", "More about ")):
                continue
            if part == "usage" and line.startswith("  keera"):
                self.usage.append(line.strip())
                continue
            if part == "usage" and not line.strip():
                continue
            if part == "usage":
                part = "description"
            if part == "flags":
                self.flags.append(line)
            elif part == "examples":
                self.examples.append(line)
            else:
                self.description.append(line)


def run(keera, *args):
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("KEERA_CONTROL_URL", "KEERA_ORG", "KEERA_OPERATOR_KEY")
    }
    with tempfile.TemporaryDirectory() as config:
        env.update(KEERA_CONFIG_DIR=config, NO_COLOR="1")
        result = subprocess.run(
            [keera, "help", *args], capture_output=True, text=True, env=env
        )
    if result.returncode:
        sys.exit(f"keera help {' '.join(args)} failed: {result.stderr}")
    return Help(result.stdout)


def link(url):
    """A docs.keera.ch address as a link to the page in this site."""
    path, _, anchor = url.removeprefix(SITE).rstrip(".,").partition("#")
    path = path.strip("/")
    for candidate in (f"{path}.md", f"{path}/index.md"):
        if path and (DOCS / candidate).exists():
            target = os.path.relpath(DOCS / candidate, OUT.parent)
            heading = next(
                line[2:].strip()
                for line in (DOCS / candidate).read_text().splitlines()
                if line.startswith("# ")
            )
            return f"[{heading}]({target}{'#' + anchor if anchor else ''})"
    return f"<{url.rstrip('.,')}>"


def prose(text):
    """Help text as Markdown: commands and flags as code, the rest escaped."""
    parts = re.split(r"((?<!\w)'(?:keera [^']+|[^'\s][^']{0,40})'(?!\w)|https://\S+)", text)
    out = []
    for part in parts:
        if part.startswith("'") and part.endswith("'"):
            out.append(f"`{part[1:-1]}`")
        elif part.startswith("https://"):
            trail = part[len(part.rstrip(".,")) :]
            out.append(link(part) + trail if part.startswith(SITE) else f"<{part}>")
        else:
            part = part.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            part = part.replace("*", r"\*")
            part = re.sub(
                r"(?<![\w`])(--?[a-z][\w-]*(?:=\S+)?|KEERA_[A-Z_]+|@-|@path|\$[A-Z_]+)",
                r"`\1`",
                part,
            )
            out.append(part)
    return "".join(out)


def paragraphs(lines):
    """Blocks of description: paragraphs, and indented lines kept as code."""
    blocks, current, code = [], [], []
    for line in lines + [""]:
        if line.startswith("    ") and line.strip():
            if current:
                blocks.append(prose(" ".join(current)))
                current = []
            code.append(line[4:])
            continue
        if code:
            blocks.append("```text\n" + "\n".join(code) + "\n```")
            code = []
        if line.strip():
            current.append(line.strip())
        elif current:
            blocks.append(prose(" ".join(current)))
            current = []
    return blocks


def flag_table(lines):
    rows = []
    for line in lines:
        match = re.match(r"^  (-[^ ]+(?: [^ ]+)?)(?:\s{2,}(.*))?$", line)
        if match and not line.startswith("   "):
            flag, text = match.group(1), match.group(2) or ""
            name, _, kind = flag.partition(" ")
            rows.append([f"`{name} <{kind}>`" if kind else f"`{name}`", text.strip()])
        elif rows:
            rows[-1][1] += " " + line.strip()
    if not rows:
        return []
    table = ["| Flag | What it does |", "| --- | --- |"]
    for flag, text in rows:
        table.append(f"| {flag} | {prose(text.strip()).replace('|', '&#124;')} |")
    return ["\n".join(table)]


def examples(lines):
    if not lines:
        return []
    body = [line[2:] if line.startswith("  ") else line for line in lines]
    while body and not body[-1].strip():
        body.pop()
    return ["```sh\n" + "\n".join(body) + "\n```"]


def usage_line(text):
    """`keera key create [<name>]   issue an API key` as a table row."""
    command, what = (re.split(r"\s{2,}", text, maxsplit=1) + [""])[:2]
    return f"| `{command}` | {prose(what)} |"


def sentence(text):
    return prose(text[:1].upper() + text[1:]) + "."


def subcommands(help_, command):
    """The subcommands a command's usage lists, in its order."""
    names = []
    for line in help_.usage:
        match = re.match(rf"^keera {command} ([a-z][a-z-]*)\b", line)
        if match and match.group(1) not in names:
            names.append(match.group(1))
    return names


def main():
    with tempfile.TemporaryDirectory() as directory:
        keera = sys.argv[1] if len(sys.argv) > 1 else download(directory)
        version = subprocess.run(
            [keera, "version"], capture_output=True, text=True
        ).stdout.strip()
        root = run(keera)
        commands = []
        in_list = False
        for line in root.description:
            if line.strip() == "Commands:":
                in_list = True
                continue
            match = re.match(r"^  ([a-z][a-z-]*)\s{2,}", line)
            if in_list and match:
                commands.append(match.group(1))
            elif in_list and not line.strip():
                in_list = False

        page = [
            "# Commands",
            "",
            "Every command of `keera`, as `keera help` describes it. "
            f"This page is generated from `keera {version.split()[-1] if version else ''}`."
            " See [The keera CLI](index.md) for how to install it and which "
            "gateway it talks to.",
            "",
        ]
        for command in commands:
            help_ = run(keera, command)
            page += [f"## keera {command}", ""]
            page += [sentence(help_.summary), ""]
            subs = subcommands(help_, command)
            if subs:
                page += ["| Command | What it does |", "| --- | --- |"]
                page += [usage_line(line) for line in help_.usage]
                page.append("")
            elif help_.usage:
                page += [f"`{help_.usage[0]}`", ""]
            for block in paragraphs(help_.description):
                page += [block, ""]
            if help_.aliases:
                page += [f"Also accepted: {prose(help_.aliases)}.", ""]
            for block in flag_table(help_.flags) + examples(help_.examples):
                page += [block, ""]
            for sub in subs:
                sub_help = run(keera, command, sub)
                if not sub_help.name.startswith(f"keera {command} {sub}"):
                    continue
                page += [f"### keera {command} {sub}", ""]
                page += [sentence(sub_help.summary), "", f"`{sub_help.name}`", ""]
                for block in paragraphs(sub_help.description):
                    page += [block, ""]
                for block in flag_table(sub_help.flags) + examples(sub_help.examples):
                    page += [block, ""]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(page).rstrip() + "\n")
    print(f"wrote {OUT.relative_to(DOCS.parent)}")


if __name__ == "__main__":
    main()
