# StudioFace Backend API — Endpoint Reference

Base URL: `https://api.studioface.app/api/v1`

**Framework:** FastAPI on uvicorn with Pydantic validation.

All endpoints return JSON. Two error formats exist:

```json
// FastAPI default
{"detail": "Error message"}

// Custom error format
{"error": {"code": "ERROR_CODE", "message": "Description", "details": {}}}
```

The Flet client normalizes errors into:

```json
{"error": "...", "code": "...", "status": 400}
```

---

## Health

### `GET /health/`

| Field | Value |
|-------|-------|
| Auth  | No    |

**Response:** `{"status": "ok", "timestamp": "2026-03-20T..."}`

---

## Authentication

### `POST /auth/magic-link`

Send a magic-link sign-in email.

| Field | Value |
|-------|-------|
| Auth  | No    |

**Request:** `{"email": "user@example.com"}`

**Response:** `{"message": "Magic link sent", "email": "user@example.com"}`

---

### `POST /auth/magic-link/verify`

Verify a magic-link token (min 32 chars) and return auth tokens.

| Field | Value |
|-------|-------|
| Auth  | No    |

**Request:** `{"token": "eyJhbGciOiJIUzI1NiIs..."}`

**Response:**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

The client stores the returned token in session and attaches it as a `Bearer` header on subsequent requests.

---

### `GET /auth/microsoft/url`

Get the Microsoft OAuth authorization URL.

| Field | Value |
|-------|-------|
| Auth  | No    |

**Response:** `{"url": "https://login.microsoftonline.com/..."}`

Microsoft OAuth client_id: `f62453e4-de16-48f6-a9fe-efd592b4e5f1`

---

### `GET /auth/microsoft/callback`

OAuth callback (returns 302 redirect). Expects `code` and `state` query params.

---

### `GET /auth/me`

Get the currently authenticated user's profile.

| Field | Value |
|-------|-------|
| Auth  | Yes — `Bearer <token>` |

**Response:** `{"id": "uuid", "email": "user@example.com", "name": "User Name"}`

**401:** `{"detail": "Not authenticated"}`

---

### `POST /auth/refresh`

Refresh an expired access token.

| Field | Value |
|-------|-------|
| Auth  | No    |

**Request:** `{"refresh_token": "..."}`

---

### `POST /auth/logout`

Log out the current user.

| Field | Value |
|-------|-------|
| Auth  | Yes — `Bearer <token>` |

---

## Generations

> **Note:** No separate `/upload/` or `/styles/` endpoints exist on the backend (both return 404). Upload and style selection are handled within the generations flow.

### `POST /generations/`

Create a new headshot generation job.

| Field | Value |
|-------|-------|
| Auth  | Yes — `Bearer <token>` |

**Request:**

```json
{
  "upload_session_id": "uuid",
  "style": "corporate",
  "presentation": "masculine"
}
```

| Parameter | Values |
|-----------|--------|
| `style` | `corporate`, `medical`, `banking`, `startup`, `casual`, `tech` |
| `presentation` | `masculine`, `feminine` |

**Response:** `{"id": "uuid", "status": "pending", "style": "corporate", ...}`

---

### `GET /generations/`

List all generations for the authenticated user.

| Field | Value |
|-------|-------|
| Auth  | Yes — `Bearer <token>` |

---

### `GET /generations/{id}`

Get status and details of a specific generation. Used for polling.

| Status | Meaning |
|--------|---------|
| `pending` | Job created, not yet started |
| `processing` | AI pipeline running |
| `completed` | All headshots generated |
| `failed` | Generation error |

Client polls every 5 seconds (max 120 attempts / 10 minutes).

---

### `GET /generations/{id}/images`

Retrieve generated headshot images for a completed generation.

---

### `GET /generations/status`

Get generation status (query parameter `?id=...`).

---

### `GET /generations/history`

Get generation history for the authenticated user.

---

### `GET /generations/download`

Download generated images (query parameter `?id=...`).

---

### `DELETE /generations/{id}`

Delete a generation.

| Field | Value |
|-------|-------|
| Auth  | Yes — `Bearer <token>` |

---

## Payments

### `POST /payments/create-checkout`

Create a Stripe checkout session. Returns the Stripe-hosted payment URL.

| Field | Value |
|-------|-------|
| Auth  | Yes — `Bearer <token>` |

**Request:** `{"generation_id": "uuid"}`

**Response:**

```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/...",
  "session_id": "cs_live_..."
}
```

Client opens `checkout_url` in the browser. After payment, Stripe redirects to `/payment/success`.

---

### `GET /payments/plans`

List available payment plans.

### `GET /payments/products`

List available products.

### `GET /payments/prices`

List prices.

### `GET /payments/credits`

Get user's credit balance.

### `GET /payments/history`

Get payment history.

### `GET /payments/portal`

Get Stripe customer portal URL.

### `POST /payments/webhook`

Stripe webhook endpoint. Validates `stripe-signature` header.

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 400 | Bad request / validation |
| 401 | Not authenticated |
| 403 | Forbidden |
| 404 | Resource not found |
| 409 | Conflict (duplicate) |
| 422 | Validation error (Pydantic) |
| 429 | Rate limited |
| 500 | Internal server error |
| 502/503/504 | Gateway error (auto-retried) |

The client automatically retries on `502`, `503`, and `504` with exponential backoff (up to 3 attempts).

---

## Security Headers

The API returns strong security headers:
- `Strict-Transport-Security` (HSTS)
- `X-Frame-Options`
- Content Security Policy permissions

## Authentication Header

All authenticated endpoints require:

```
Authorization: Bearer <token>
```

Token is obtained via magic-link verification (`POST /auth/magic-link/verify`) and stored in the session store.

## Notes

- **Google OAuth** is **not configured** on the backend (client_id is a placeholder)
- **No public API docs** — `/docs`, `/openapi.json`, `/schema/` all return 404
- **No separate upload endpoints** — file uploads are handled within the generations flow
