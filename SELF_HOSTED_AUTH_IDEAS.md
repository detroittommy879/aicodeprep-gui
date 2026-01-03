# Self-hosted auth brainstorm for `aicodeprep-gui` (PySide6)

Date: 2026-01-02

## What I found in this repo (relevant to auth)

### App shape

- The desktop app is a **local-first PySide6 GUI** under `aicodeprep_gui/`.
- Entry point: `aicodeprep_gui.main:main` (CLI `aicp` / `aicodeprep-gui`).
- It already uses **Qt networking** (`QtNetwork.QNetworkAccessManager`) for things like update checks / telemetry.

### Existing “identity” concepts already present

- **Anonymous per-install UUID**: `QSettings("aicodeprep-gui", "UserIdentity")` stores a generated `user_uuid` and counters (open count, etc.).
- **Pro license activation (Gumroad)**:
  - UI has an “Activate Pro…” action.
  - Activation calls Gumroad’s license verification endpoint, then stores:
    - `QSettings("aicodeprep-gui", "ProLicense").license_key`
    - `license_verified = True`
    - `pro_enabled` (and a timestamp)
  - Pro gating today is purely local (read from QSettings), with the initial verification happening over HTTPS.

### Secrets storage pattern

- API keys for LLM providers are stored locally in: `~/.aicodeprep-gui/api-keys.toml`.
- Pro gating is stored in **QSettings**, not in that TOML.

### What’s missing for “users can log in”

- There is **no general user authentication** flow (email/password/passkeys) in the app today.
- There’s no existing OIDC/OAuth client logic (no PKCE, no token handling, no redirect capture).

That means you have freedom to design auth “the right way” without being boxed into earlier decisions.

---

## What you said you want

- Self-hostable auth: ideally “grab and run a Docker container on an Ubuntu server”.
- Users log in with **email address + passkey and/or password**.
- Add **2FA that is NOT email-based** (but you also want an “easy email” path as a bonus).

---

## Recommended high-level architecture

### The cleanest approach: OIDC (OpenID Connect) + System Browser login

For a desktop app, the best practice is:

1. Your app opens the user’s default browser to an OIDC authorization URL (Authorization Code + PKCE).
2. The identity provider (IdP) handles:
   - email+password (optional)
   - passkeys (WebAuthn)
   - MFA (TOTP / WebAuthn / backup codes)
3. After login, the browser redirects back to the app using either:
   - **Loopback** redirect: `http://127.0.0.1:<random_port>/callback` (recommended)
   - or a **custom URI scheme** like `aicodeprep://callback` (more OS plumbing)
4. The app exchanges the code for tokens (access token, optionally refresh token).
5. The app calls _your API_ and attaches the access token (JWT) as `Authorization: Bearer ...`.

**Key point:** Passkeys work best when the auth UX is _a normal web page_ with a real origin. Using the system browser makes passkeys “just work” and avoids implementing native passkey APIs in PySide6.

### Why you probably still want a small backend API

Even if the initial goal is “only log in”, you usually need _something_ to protect:

- Pro entitlement checks / license sync
- account features (cloud presets sync, telemetry opt-in per account, multi-device, etc.)

So think of it as:

- **IdP = who are you?**
- **API = what are you allowed to do?**

You can start tiny: a single container that only exposes `/me` and maybe `/entitlements`.

---

## Self-hostable IdP options (Docker-friendly)

Below are practical “docker-compose on Ubuntu” candidates.

### Option A (strong default): Keycloak

Best if you want something mature and widely supported.

- Supports:
  - Email+password
  - WebAuthn / passkeys (as passwordless or as second factor)
  - TOTP (Authenticator apps)
  - Backup codes
  - OIDC/OAuth2
- Pros:
  - Very feature-complete, enterprise-grade
  - Tons of docs and community examples
  - Easy to integrate with any backend (JWT verification)
- Cons:
  - Heavier UI/admin surface area
  - More knobs than you need at first

### Option B (modern + nice UX): ZITADEL

Best if you want “modern identity platform” vibes and strong passkey support.

- Supports:
  - Email+password
  - Passkeys / WebAuthn
  - MFA options (varies by configuration)
  - OIDC
- Pros:
  - Good developer ergonomics
  - Good user-facing UI
- Cons:
  - Slightly less “every tutorial exists” than Keycloak

### Option C (homelab-friendly SSO): authentik

Best if you already run homelab SSO and want one system for everything.

- Supports OIDC and a range of MFA options.
- Pros:
  - Very popular for self-hosters
  - Great admin UI
- Cons:
  - Passkey/WebAuthn support depends on version/features; you’d want to verify it meets your exact passkey UX requirements.

### Option D (API-first auth suite): Ory (Kratos + Hydra)

Best if you want to build your own UX and keep auth fully API-driven.

- Pros:
  - Flexible, composable
- Cons:
  - More moving parts and more engineering effort
  - Not “minimal setup” compared to Keycloak/Zitadel

**My practical recommendation:** start with **Keycloak** or **ZITADEL**.

---

## MFA methods that don’t require email

These are “works great for self-hosted”:

1. **TOTP** (Google Authenticator, Authy, 1Password, etc.)

   - Easiest to operate.
   - No SMS cost.
   - Strong baseline security.

2. **Passkey / WebAuthn as MFA**

   - Hardware keys (YubiKey) or platform keys.
   - Great UX and phishing-resistant.
   - Can be used as step-up auth for sensitive actions.

3. **Recovery codes**
   - Essential for account recovery.

Other MFA methods that are possible but add complexity:

- **SMS**: not email, but requires a provider (Twilio, etc.) and brings deliverability/fraud costs.
- **Push** (vendor app): usually not worth building early.

---

## “Easy email” paths (if/when you want email verification/reset)

Even if you don’t want email-based _2FA_, you may want email for:

- account verification
- password reset
- “new login detected” alerts

### Lowest-friction choices

- Use a transactional provider (often easiest): **Mailgun / Postmark / SendGrid / Amazon SES**.
  - Many can send from a shared or subdomain; you don’t necessarily need a fancy custom domain on day 1.

### If you truly don’t have a custom domain yet

- You can still send mail from something like a Gmail account using SMTP + app password.
  - Operationally easy.
  - Not as “professional deliverability” as a provider.

### Self-hosting email

- Running your own mail server is rarely “minimal setup” due to DNS/SPF/DKIM/DMARC and deliverability issues.

---

## Desktop-app integration patterns (PySide6)

### Best practice: system browser + PKCE + loopback redirect

- Open URL in browser using `QDesktopServices.openUrl(...)`.
- Start a tiny local HTTP listener in the app on `127.0.0.1` to receive the redirect.
- Exchange the code for tokens via HTTPS.

Why loopback is great:

- No OS-specific custom protocol registration.
- Works on Windows/macOS/Linux.

### Token storage

Given your current patterns:

- You already store settings in QSettings.
- You store secrets in a user config directory (`~/.aicodeprep-gui`).

For auth tokens, I’d recommend:

- Store **refresh tokens** (if you use them) in an OS keychain via Python `keyring`.
- Store only non-sensitive session state in QSettings.

### Keep Pro licensing separate (optional)

If “login” is for something else (team features, cloud sync), keep it logically separate from your Gumroad Pro license.

If you want to eventually replace Gumroad activation with your own self-hosted entitlement check:

- Your backend can map an IdP user to an entitlement record.
- The app checks `/entitlements` after login.
- You can still allow offline grace periods.

---

## Minimal docker-compose shape (conceptual)

A typical small deployment:

- `reverse-proxy` (Caddy or Traefik)
- `idp` (Keycloak OR Zitadel)
- `db` (Postgres)
- optional `api` (your small service)

Notes:

- You’ll want HTTPS (passkeys/WebAuthn and modern browsers strongly expect it).
- Easiest path is a reverse proxy that auto-manages TLS (Caddy is very “set and forget”).

---

## Suggested phased rollout

### Phase 0 (proof-of-concept)

- Run Keycloak/Zitadel in Docker.
- Create one OIDC client for the desktop app.
- Implement login via system browser + loopback.
- Print the user’s subject (`sub`) and email in the app.

### Phase 1 (real users)

- Enable passkeys and/or password.
- Turn on TOTP as optional/required.
- Add a simple “Account” screen in the app (logged in/out, manage session).

### Phase 2 (product features gated by auth)

- Add a small API service:
  - `/me`
  - `/entitlements`
  - `/sync/presets` (if you want)
- Verify JWT access tokens in the API.

---

## Open questions (that affect the best choice)

If you tell me these, I can narrow to one “best” stack:

1. Are you hosting one shared auth server for all users, or will customers self-host their own?
2. Do you need multi-tenant orgs/teams, or just individual accounts?
3. Do you want passwordless-only (passkeys) or passkeys + password fallback?
4. Do you need offline operation after the first login (cached tokens / grace periods)?

---

## My short recommendation

If you want the highest chance of success with the least surprises:

- Use **Keycloak** (IdP) + **OIDC Authorization Code + PKCE** in the desktop app.
- Configure **Passkeys (WebAuthn)** + **TOTP** + **recovery codes**.
- Use a reverse proxy (Caddy) to make HTTPS painless.

If you want a more modern/pleasant user UX and you’re okay with slightly less “universal tutorial coverage”:

- Use **ZITADEL** instead of Keycloak.
