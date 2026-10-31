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

On Keera Chat:

```sh
KEERA_CHAT_PUBLIC_URL=https://chat.example.ch
KEERA_CHAT_GATEWAY_URL=https://keera.example.ch
KEERA_CHAT_SECRET_KEY=…   # openssl rand -hex 32
```

Put TLS in front of it, as for the gateway, and turn off response buffering so
replies stream.

| Variable                          | Default                   | What it is                                                                           |
| --------------------------------- | ------------------------- | ------------------------------------------------------------------------------------ |
| `KEERA_CHAT_GATEWAY_URL`          | required                  | The gateway's address, as a browser reaches it.                                      |
| `KEERA_CHAT_SECRET_KEY`           | required                  | Encrypts the sign-in cookie. At least 16 characters. Changing it signs everyone out. |
| `KEERA_CHAT_PUBLIC_URL`           | `http://127.0.0.1:<port>` | Keera Chat's address, as a browser reaches it. Must match `KEERA_CHAT_URL`.          |
| `KEERA_CHAT_GATEWAY_INTERNAL_URL` | `KEERA_CHAT_GATEWAY_URL`  | The gateway's address from Keera Chat, if different, such as `http://gateway:8080`.  |
| `KEERA_CHAT_ADDR`                 | `:8090`                   | The address and port to listen on.                                                   |
| `KEERA_CHAT_SECURE_COOKIES`       | on for https              | Marks the sign-in cookie `Secure`.                                                   |
| `KEERA_CHAT_MAX_BODY_BYTES`       | 32 MiB                    | The largest request. Each one carries the whole conversation, attachments included.  |
| `KEERA_CHAT_LOG_LEVEL`            | `info`                    | `debug`, `info`, `warn` or `error`.                                                  |
| `KEERA_CHAT_LOG_FORMAT`           | `text`                    | `text` or `json`.                                                                    |

Keera Chat logs only each request's method, path, status and duration, never
tokens or messages. The sign-in is kept in an encrypted cookie. Signing out
also signs out at the gateway, and when the gateway ends a sign-in, Keera Chat
follows within a minute.
