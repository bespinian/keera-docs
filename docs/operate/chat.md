# Run Keera Chat

How to run [Keera Chat](../use/chat.md) next to your gateway.

Keera Chat is a separate, stateless service. It needs no database or volume
and can run as several replicas. The image is
`ghcr.io/bespinian/keera-chat:<version>`. It runs as `nobody` and listens on
port `8090`.

On the gateway, set `KEERA_CHAT_URL` so people can sign in to Keera Chat:

```sh
KEERA_CHAT_URL=https://chat.example.ch
```

With [`KEERA_AGENTS_URL`](agents.md) set too, people can also chat with their
agents.

On Keera Chat:

```sh
KEERA_CHAT_PUBLIC_URL=https://chat.example.ch
KEERA_CHAT_GATEWAY_URL=https://keera.example.ch
KEERA_CHAT_SECRET_KEY=…   # openssl rand -hex 32
```

Put TLS in front of it, as for the gateway, and turn off response buffering so
replies stream. Keera Chat must run at the root of its host: its addresses take
no path. `/healthz` answers health checks.

## Next to compose

Next to the gateway's [compose](install.md#one-host-with-compose), add to its
`.env`:

```sh
KEERA_PUBLIC_URL=http://localhost:8080
KEERA_CHAT_URL=http://localhost:8090
```

Run `podman compose up -d` again, then start Keera Chat on the same network:

```sh
podman run -d --name keera-chat --network compose_default \
  -p 127.0.0.1:8090:8090 \
  -e KEERA_CHAT_PUBLIC_URL=http://localhost:8090 \
  -e KEERA_CHAT_GATEWAY_URL=http://localhost:8080 \
  -e KEERA_CHAT_GATEWAY_INTERNAL_URL=http://keera-gateway:8080 \
  -e KEERA_CHAT_SECRET_KEY="$(openssl rand -hex 32)" \
  ghcr.io/bespinian/keera-chat:<version>
```

Open <http://localhost:8090>. Use `localhost` everywhere, not `127.0.0.1`: the
browser keeps the sign-in apart by host name.

## On Kubernetes

There is no Helm chart. A Deployment and a Service are enough:

```yaml title="keera-chat.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keera-chat
spec:
  replicas: 2
  selector:
    matchLabels: { app: keera-chat }
  template:
    metadata:
      labels: { app: keera-chat }
    spec:
      containers:
        - name: keera-chat
          image: ghcr.io/bespinian/keera-chat:<version>
          ports: [{ containerPort: 8090 }]
          env:
            - { name: KEERA_CHAT_PUBLIC_URL, value: https://chat.example.ch }
            - { name: KEERA_CHAT_GATEWAY_URL, value: https://keera.example.ch }
            - name: KEERA_CHAT_GATEWAY_INTERNAL_URL
              value: http://keera-gateway.keera-gateway.svc
            - name: KEERA_CHAT_SECRET_KEY
              valueFrom:
                secretKeyRef: { name: keera-chat, key: secret-key }
          readinessProbe:
            httpGet: { path: /healthz, port: 8090 }
---
apiVersion: v1
kind: Service
metadata:
  name: keera-chat
spec:
  selector: { app: keera-chat }
  ports: [{ port: 80, targetPort: 8090 }]
```

Publish the Service at `KEERA_CHAT_PUBLIC_URL` with an Ingress, as for the
gateway.

## Settings

| Variable                          | Default                   | What it is                                                                                  |
| --------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------- |
| `KEERA_CHAT_GATEWAY_URL`          | required                  | The gateway's address, as a browser reaches it.                                             |
| `KEERA_CHAT_SECRET_KEY`           | required                  | Encrypts the sign-in cookie. At least 16 characters. Changing it signs everyone out.        |
| `KEERA_CHAT_PUBLIC_URL`           | `http://127.0.0.1:<port>` | Keera Chat's address, as a browser reaches it. Must match `KEERA_CHAT_URL`.                 |
| `KEERA_CHAT_GATEWAY_INTERNAL_URL` | `KEERA_CHAT_GATEWAY_URL`  | The gateway's address from Keera Chat, if different, such as `http://gateway:8080`.         |
| `KEERA_CHAT_AGENTS_INTERNAL_URL`  | the gateway's             | Keera Agents' address from Keera Chat, if it differs from the gateway's `KEERA_AGENTS_URL`. |
| `KEERA_CHAT_ADDR`                 | `:8090`                   | The address and port to listen on.                                                          |
| `KEERA_CHAT_SECURE_COOKIES`       | on for https              | Marks the sign-in cookie `Secure`.                                                          |
| `KEERA_CHAT_MAX_BODY_BYTES`       | 32 MiB                    | The largest request, at least 1 MiB. Each one carries the whole conversation and its files. |
| `KEERA_CHAT_LOG_LEVEL`            | `info`                    | `debug`, `info`, `warn` or `error`.                                                         |
| `KEERA_CHAT_LOG_FORMAT`           | `text`                    | `text` or `json`.                                                                           |

Keera Chat logs each request's method, path, status and duration, and what
went wrong on a failure. It never logs tokens or messages. The sign-in is
kept in an encrypted cookie. Signing out also signs out at the gateway, and
when the gateway ends a sign-in, Keera Chat follows within a minute.
