# Sandboxes

A sandbox is a machine Keera lends out for one task or one working day. It
runs inside the gateway's private network, with the toolchain, its own API
key and an expiry.

Keera controls the requests an editor sends, but it cannot see what an agent
does on a laptop. A sandbox moves that work into the gateway's private
network, where:

- **outgoing traffic can be limited** to the gateway and a few internal hosts
- **the API key never lands on a laptop**: each sandbox gets its own, which
  ends with the sandbox
- **an agent's work leaves as a branch** that a person reviews

## Two kinds

|                 | Engineer sandbox                   | Agent sandbox               |
| --------------- | ---------------------------------- | --------------------------- |
| For             | a developer's working day          | one task for a coding agent |
| How you get in  | ssh, or your editor over ssh       | nobody gets in              |
| When it expires | it is suspended; you can resume it | it ends                     |
| How work leaves | you push                           | the agent pushes a branch   |

## Use an engineer sandbox

```sh
keera sandbox create fix-login --class standard \
  --repo git@github.com:acme/service.git
keera sandbox ssh fix-login
```

To use VS Code or a JetBrains IDE, add the sandboxes to your ssh settings once:

```sh
keera sandbox config >> ~/.ssh/config
```

Then connect to `sbx-fix-login` like any ssh host.

| Command                                | What it does                                   |
| -------------------------------------- | ---------------------------------------------- |
| `keera sandbox list`                   | your live sandboxes (`--all` for ended ones)   |
| `keera sandbox show <name>`            | one sandbox in full                            |
| `keera sandbox extend <name> --ttl 4h` | gives it more time, counted from now           |
| `keera sandbox suspend <name>`         | stops it and keeps its disk                    |
| `keera sandbox resume <name>`          | starts it again; an expired one gets a new key |
| `keera sandbox terminate <name>`       | ends it and frees its disk                     |

## Run an agent in a sandbox

```sh
keera sandbox agent fix-flaky-test --class agent \
  --repo git@github.com:acme/service.git \
  --task "Fix the flaky test in payments/transfer_test.go"
```

Keera starts a machine, checks out the repository, runs the coding agent on
the task and pushes a branch. Then the sandbox ends. It never pushes to the
default branch.

## For administrators

**Classes** are the machine types people can ask for, such as `standard` or
`agent`. Each sets the image, the size, the isolation and the lifetimes.

```yaml title="sandboxes.yaml"
sandboxes:
  - name: standard
    description: The repo toolchain and an agent.
    image: registry.internal/keera/sandbox-base:1
    isolation: isolated # standard, isolated (gVisor) or vm (Kata)
    cpu: "4"
    memory: 16Gi
    disk: 50Gi
    default_ttl: 8h
    max_ttl: 24h
    purposes: [engineer]
```

```sh
keera sandbox apply sandboxes.yaml
keera sandbox classes
keera sandbox delete-class standard
```

A class can use the image of a class your organisation started with, or an
image the gateway's operator allows. Ask your operator for any other image.
On a self-hosted gateway, see
[`KEERA_SANDBOX_IMAGES`](../operate/settings.md#sandboxes).

**Quotas** are part of a project's guardrail, set on the command line:

```sh
keera guardrail set project "Payments Platform" \
  --max-sandboxes 6 --max-sandbox-ttl 8h --sandbox-classes standard,agent \
  --max-sandbox-cpu 8 --max-sandbox-memory 32768   # memory in MiB
```

**Repositories** a sandbox may check out are set on the organisation, by an
operator, and a project can narrow them:

```sh
keera guardrail set org --repos acme
keera guardrail set project "Payments Platform" --repos acme/service
```

**Costs.** `keera sandbox usage --by project` shows how many sandboxes ran,
for how long, and how many core-hours they used.

Administrators can see, suspend, resume, extend and terminate every sandbox
in the organisation, but cannot open a shell in someone else's sandbox.
