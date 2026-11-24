# Kubernetes

Two Helm charts install Keera on Kubernetes:

| Chart           | What it installs                                                  |
| --------------- | ----------------------------------------------------------------- |
| `keera-gateway` | Keera Gateway and a Postgres for it                               |
| `keera-agents`  | Keera Agents, a Postgres for it, and a namespace where agents run |

Both are at `oci://ghcr.io/bespinian/keera-helm-charts/`. Every value is
listed in each chart's README in the
[keera-helm-charts repository](https://github.com/bespinian/keera-helm-charts).
Keera Chat has no chart; see [Run Keera Chat](chat.md#on-kubernetes).

## Keera Gateway

**1. Create the secrets.** One Secret holds the operator key, the secret key
and the database's password:

```sh
kubectl create namespace keera-gateway
kubectl create secret generic keera-gateway-credentials \
  --namespace keera-gateway \
  --from-literal=KEERA_OPERATOR_KEY="$(openssl rand -hex 32)" \
  --from-literal=KEERA_SECRET_KEY="$(openssl rand -hex 32)" \
  --from-literal=password="$(openssl rand -hex 32)"
```

Keep this Secret: Postgres only accepts the password it started with.

**2. Write the values.** For example, with an Ingress and Google sign-in:

```yaml title="gateway.yaml"
publicUrl: https://keera.example.ch
operators: [you@example.ch]

credentials:
  existingSecret:
    name: keera-gateway-credentials
database:
  internal:
    existingSecret: keera-gateway-credentials

gateway:
  ingress:
    enabled: true
    ingressClassName: nginx
    hostname: keera.example.ch
    tls: true # from the Secret keera-gateway-tls
    annotations:
      nginx.ingress.kubernetes.io/proxy-buffering: "off"
      nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
      nginx.ingress.kubernetes.io/proxy-body-size: 32m

oidc:
  enabled: true
  name: google
  issuer: https://accounts.google.com
  clientId: <from the Google Cloud console>
  clientSecret: <from the Google Cloud console>
```

See [Publish it](install.md#publish-it) for what the proxy must do, and
[Single sign-on](sign-on.md) for each provider. `gateway.httpRoute` replaces
the Ingress with a Gateway API route.

**3. Install it:**

```sh
helm upgrade --install keera-gateway \
  oci://ghcr.io/bespinian/keera-helm-charts/keera-gateway \
  --namespace keera-gateway --values gateway.yaml
kubectl --namespace keera-gateway rollout status deployment/keera-gateway
```

Then continue with [First run](install.md#first-run).

### Gateway values

| Value                                         | Setting                                                    |
| --------------------------------------------- | ---------------------------------------------------------- |
| `publicUrl`                                   | `KEERA_PUBLIC_URL`                                         |
| `operators`                                   | `KEERA_OPERATORS`                                          |
| `passkeys`                                    | `KEERA_PASSKEYS`                                           |
| `upstreamPrivate`                             | `KEERA_UPSTREAM_PRIVATE`                                   |
| `oidc.*`                                      | one provider; `oidc.providers` for several, one entry each |
| `gateway.replicaCount`, `gateway.autoscaling` | how many replicas run                                      |
| `database.internal.*`                         | the chart's Postgres, on a 1 Gi volume by default          |

The chart sets only these settings. It has no value yet for the others in
[Settings](settings.md), such as `KEERA_CHAT_URL`, `KEERA_AGENTS_URL` or a
provider's key.

With several replicas, set up Redis for rate limits; see
[Traffic](settings.md#traffic).

Charts after 0.1.3 name the chart's database `keera_gateway`, where it was
`keera`. Postgres creates it only on first start, so an older install keeps
its own: set `database.internal.database: keera` before you upgrade.

## Keera Agents

Install the gateway first.

**1. Create the secrets.** The service key is shared with the gateway:

```sh
kubectl create namespace keera-agents
kubectl create secret generic keera-agents-credentials \
  --namespace keera-agents \
  --from-literal=KEERA_AGENTS_SERVICE_KEY="$(openssl rand -hex 32)" \
  --from-literal=KEERA_AGENTS_SECRET_KEY="$(openssl rand -hex 32)" \
  --from-literal=password="$(openssl rand -hex 32)"
```

**2. Tell the gateway**, and restart it:

```sh
KEERA_AGENTS_URL=https://agents.example.ch
KEERA_AGENTS_SERVICE_KEY=<the same value as in the Secret>
```

**3. Write the values:**

```yaml title="agents.yaml"
publicUrl: https://agents.example.ch
gateway:
  url: https://keera.example.ch
  internalUrl: http://keera-gateway.keera-gateway.svc

credentials:
  existingSecret:
    name: keera-agents-credentials
database:
  internal:
    existingSecret: keera-agents-credentials

agents:
  networkPolicy:
    gateway:
      namespace: keera-gateway
  runtimeClasses:
    isolated: gvisor # if the cluster has it
    vm: kata # if the cluster has it

controlPlane:
  ingress:
    enabled: true
    ingressClassName: nginx
    hostname: agents.example.ch
    tls: true
```

**4. Install it:**

```sh
helm upgrade --install keera-agents \
  oci://ghcr.io/bespinian/keera-helm-charts/keera-agents \
  --namespace keera-agents --values agents.yaml
kubectl --namespace keera-agents rollout status deployment/keera-agents
```

### Where agents run

Each agent and workspace is a StatefulSet in a namespace of its own,
`keera-agents-sandbox` here. Whoever can read pods there reads the agents'
runtime tokens, so give nobody else access. The chart creates the namespace
with:

- the Pod Security Standard `restricted`
- a NetworkPolicy that denies everything except DNS, the gateway and Keera
  Agents. Your CNI must enforce it. Add destinations, such as a package
  proxy, to `agents.networkPolicy.extraEgress`.
- a Role that lets Keera Agents manage StatefulSets and read pods there

The namespace stays when you uninstall, since it holds the workspaces.

Isolation tiers need RuntimeClasses: gVisor for **Isolated**, Kata for **VM**.
A tier without one cannot be chosen. `agents.minIsolation` sets the weakest
tier allowed. Also set `podPidsLimit` on the kubelet, so one agent cannot use
up the node's processes.

### Agents values

| Value                                          | Setting                                                           |
| ---------------------------------------------- | ----------------------------------------------------------------- |
| `publicUrl`                                    | `KEERA_AGENTS_PUBLIC_URL`                                         |
| `gateway.url`, `gateway.internalUrl`           | `KEERA_AGENTS_GATEWAY_URL`, `KEERA_AGENTS_GATEWAY_INTERNAL_URL`   |
| `upstreamPrivate`, `upstreamDeny`              | `KEERA_AGENTS_UPSTREAM_PRIVATE`, `KEERA_AGENTS_UPSTREAM_DENY`     |
| `taskTimeout`, `watchInterval`                 | `KEERA_AGENTS_TASK_TIMEOUT`, `KEERA_AGENTS_WATCH_INTERVAL`        |
| `prices.*`                                     | [what machines cost](agents.md#bill-machines)                     |
| `agents.idleSuspend`, `workspaces.idleSuspend` | how long an idle agent or workspace stays awake                   |
| `agents.maxCpu`, `maxMemory`, `maxDisk`        | the largest machine                                               |
| `agents.image`, `workspaces.image`             | the [images](agents.md#the-agent-image) agents and workspaces run |
| `credentials.metricsToken`                     | turns on `/metrics`                                               |
| `database.type: external`                      | your own Postgres, with `database.external.url`                   |
| `extraEnvVars`                                 | any other setting in [Settings](agents.md#settings)               |

Back up the database, `KEERA_AGENTS_SECRET_KEY` and the workspaces' volumes;
see [Back up and upgrade](agents.md#back-up-and-upgrade).
