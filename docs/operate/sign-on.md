# Single sign-on and passkeys

Without single sign-on, the only way into the panel is the shared operator
key, and every audit entry reads `operator@localhost`. With single sign-on,
people sign in as themselves, roles can differ, and the audit log names a
person.

Keera supports:

- any **OpenID Connect** provider, such as Google Workspace, Microsoft Entra
  ID, Keycloak or Okta
- **GitHub**
- **LDAP and Active Directory**, with username and password
- **passkeys**, for people without an account in a directory

You can offer several at once. The panel shows one button for each.

## Set up a provider

Each provider has a short name, listed in `KEERA_OIDC_PROVIDERS`, and reads its
settings from `KEERA_OIDC_<NAME>_*`. Register this redirect address with the
provider:

```text
https://keera.example.ch/control/auth/callback
```

=== "Google Workspace"

    In the Google Cloud console, create an OAuth consent screen of type
    **Internal**, then an **OAuth client ID** of type **Web application**
    with the redirect address above.

    ```sh
    KEERA_PUBLIC_URL=https://keera.example.ch
    KEERA_OIDC_PROVIDERS=google
    KEERA_OIDC_GOOGLE_ISSUER=https://accounts.google.com
    KEERA_OIDC_GOOGLE_CLIENT_ID=<from the console>
    KEERA_OIDC_GOOGLE_CLIENT_SECRET=<from the console>
    KEERA_OPERATORS=you@example.ch
    ```

    Google sends no groups. Make administrators in the panel or with
    `keera user role`.

=== "Microsoft Entra ID"

    Create an **app registration** for your own directory only, with the
    redirect address above as a **Web** redirect. Add a client secret, and add
    the optional ID token claims `email` and `xms_edov`. To let Entra decide
    who is an administrator, create the **app roles** `keera-admins` and
    `keera-operators` and assign them.

    ```sh
    KEERA_PUBLIC_URL=https://keera.example.ch
    KEERA_OIDC_PROVIDERS=entra
    KEERA_OIDC_ENTRA_ISSUER=https://login.microsoftonline.com/<tenant-id>/v2.0
    KEERA_OIDC_ENTRA_CLIENT_ID=<application (client) id>
    KEERA_OIDC_ENTRA_CLIENT_SECRET=<the secret value>
    KEERA_OIDC_ENTRA_GROUPS_CLAIM=roles
    KEERA_OIDC_ENTRA_ADMIN_GROUPS=keera-admins
    KEERA_OIDC_ENTRA_OPERATOR_GROUPS=keera-operators
    ```

=== "GitHub"

    Create an **OAuth App** (not a GitHub App) on your GitHub organisation,
    with the redirect address above as the callback URL.

    ```sh
    KEERA_PUBLIC_URL=https://keera.example.ch
    KEERA_OIDC_PROVIDERS=github
    KEERA_OIDC_GITHUB_ISSUER=https://github.com
    KEERA_OIDC_GITHUB_CLIENT_ID=<the client id>
    KEERA_OIDC_GITHUB_CLIENT_SECRET=<the secret>
    KEERA_OIDC_GITHUB_DOMAINS=example.ch
    ```

    Any GitHub account can sign in, so `DOMAINS` is required: only addresses
    at these domains are let in.

=== "LDAP / Active Directory"

    Keera checks the username and password against the directory with a
    read-only service account. The connection is always encrypted.

    ```sh
    KEERA_PUBLIC_URL=https://keera.example.ch
    KEERA_OIDC_PROVIDERS=corp
    KEERA_OIDC_CORP_LABEL=Corp account
    KEERA_OIDC_CORP_ISSUER=ldaps://dc1.corp.example.ch
    KEERA_OIDC_CORP_LDAP_BIND_DN=CN=keera-svc,OU=Service,DC=corp,DC=example,DC=ch
    KEERA_OIDC_CORP_LDAP_BIND_PASSWORD=<the service account's password>
    KEERA_OIDC_CORP_LDAP_BASE_DN=DC=corp,DC=example,DC=ch
    KEERA_OIDC_CORP_DOMAINS=corp.example.ch
    KEERA_OIDC_CORP_ADMIN_GROUPS=CN=keera-admins,OU=Groups,DC=corp,DC=example,DC=ch
    ```

The gateway checks each provider when it starts, and refuses to start with a
message if something is wrong.

## Roles

**Operators** come only from the settings: an address in `KEERA_OPERATORS`, or
a member of `KEERA_OIDC_<NAME>_OPERATOR_GROUPS`. The panel never grants the
operator role.

**Administrators** come from one of two places:

- If `KEERA_OIDC_<NAME>_ADMIN_GROUPS` is set, **the directory decides**. Members
  of the group are administrators, and the panel no longer lets you change
  roles.
- If it is not set, **Keera decides**. Everyone starts as a member (or as set
  in `KEERA_OIDC_<NAME>_DEFAULT_ROLE`), and an administrator promotes people
  with `keera user role` or on the **Users** screen.

While someone is active, Keera asks the directory again every 15 minutes.
Someone removed from the directory, or from a group, loses access or the role
within that time. An OpenID Connect provider must hand out refresh tokens for
this; without them, it is asked only at sign-in. GitHub is asked only whether
the person still allows Keera.

## Organisations and domains

A first sign-in lands in the organisation whose email domain matches the
person's address. Set the domain when you create an organisation:

```sh
keera org create "Another Bank" --domain anotherbank.ch
keera org set "Example Bank" --domain example.ch
```

While there is only one organisation and no provider allows self sign-up
(below), everyone who can sign in lands in it. So limit the
provider to your own staff (Google: **Internal**; Entra: your directory only).

With several providers, each must list the domains it may sign people in
with, in `KEERA_OIDC_<NAME>_DOMAINS`. Use `*` only for a provider that checks
every address itself, such as Google.

**Self sign-up.** On a public gateway, `KEERA_OIDC_<NAME>_SIGNUP=true` lets
someone with no matching organisation create their own. A new organisation
starts limited until its first payment; see [Billing](../manage/billing.md).
Sign-up needs `KEERA_UPSTREAM_PRIVATE`, and does not work with admin groups or
an LDAP directory.

## Passkeys

A passkey signs someone in with their fingerprint, face or device PIN, without
a directory. Use it for people who are not in your directory, or on a gateway
with no directory at all.

```sh
KEERA_PASSKEYS=true
KEERA_PUBLIC_URL=https://keera.example.ch
```

Passkeys need `https`, or `http://localhost`. They are tied to the host name,
so do not change it later.

An administrator adds a person with `keera user add <email> --passkey`, or
**Users → Add user**, and sends them the set-up link. The address must be at
the organisation's email domain, if it has one. For anyone else, such as a
contractor at another company, an operator adds the account. A passkey account
is never an operator. With no directory, make the first administrator with the
operator key:

```sh
keera user add you@example.ch --passkey --role admin
```

## The operator key afterwards

Once a provider is set up, the operator key is no longer on the sign-in
screen. It still works for scripts and pipelines, and it is the way back in if
single sign-on breaks: open `https://keera.example.ch/?operator_key=1`.

Removing someone from the directory does not revoke their API keys. See
[When someone leaves](../manage/users.md#when-someone-leaves).
