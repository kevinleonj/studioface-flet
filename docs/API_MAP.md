# StudioFace Backend API — Endpoint Reference

Base URL: `https://api.studioface.app/api/v1`

All endpoints return JSON. Errors follow the format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

The Flet client normalizes errors into:

```json
{
  "error": "...",
  "code": "...",
  "status": 400
}
```

---

## Health

### `GET /health/`

Check whether the backend API is reachable and operational.

| Field        | Value            |
|--------------|------------------|
| Auth         | No               |
| Request Body | None             |

**Response:**

```json
{
  "status": "ok"
}
```

---

## Authentication

### `POST /auth/magic-link`

Send a magic-link sign-in email to the given address.

| Field        | Value            |
|--------------|------------------|
| Auth         | No               |
| Content-Type | application/json |

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response (success):**

```json
{
  "message": "Magic link sent",
  "email": "user@example.com"
}
```

---

### `POST /auth/verify`

Verify a magic-link or OAuth token and return user data.

| Field        | Value            |
|--------------|------------------|
| Auth         | No               |
| Content-Type | application/json |

**Request Body:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (success):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

The client stores the returned token in `client_storage` and attaches it as a `Bearer` header on subsequent requests.

---

### `GET /auth/microsoft/url`

Get the Microsoft OAuth authorization URL for redirect-based sign-in.

| Field        | Value            |
|--------------|------------------|
| Auth         | No               |
| Request Body | None             |

**Response:**

```json
{
  "url": "https://login.microsoftonline.com/..."
}
```

The client opens this URL in the browser via `page.launch_url_async()`.

---

### `GET /auth/me`

Get the currently authenticated user's profile.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Request Body | None                           |

**Response (success):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name"
}
```

**Response (401):**

```json
{
  "detail": "Not authenticated"
}
```

---

## Upload

### `POST /upload/session`

Create a new upload session. A session groups multiple photo uploads together.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Request Body | None                           |

**Response:**

```json
{
  "session_id": "uuid",
  "created_at": "2026-03-20T12:00:00Z"
}
```

---

### `POST /upload/{session_id}`

Upload a single photo file to an existing upload session.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Content-Type | multipart/form-data            |

**Request Body (multipart):**

| Field  | Type   | Description                       |
|--------|--------|-----------------------------------|
| `file` | binary | JPG or PNG image, max 10 MB       |

**Response:**

```json
{
  "id": "uuid",
  "filename": "selfie1.jpg",
  "session_id": "uuid",
  "uploaded_at": "2026-03-20T12:00:05Z"
}
```

**Constraints (enforced client-side):**

- Allowed formats: `.jpg`, `.jpeg`, `.png`
- Max file size: 10 MB per file
- Min files per session: 2
- Max files per session: 5

---

## Generations

### `POST /generations/`

Create a new headshot generation job. This triggers the AI pipeline on the backend.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Content-Type | application/json               |

**Request Body:**

```json
{
  "upload_session_id": "uuid",
  "style": "corporate",
  "presentation": "masculine"
}
```

| Parameter           | Type   | Values                                                          |
|---------------------|--------|-----------------------------------------------------------------|
| `upload_session_id` | string | UUID from the upload session                                    |
| `style`             | string | `corporate`, `medical`, `banking`, `startup`, `casual`, `tech`  |
| `presentation`      | string | `masculine`, `feminine`                                         |

**Response:**

```json
{
  "id": "uuid",
  "status": "pending",
  "style": "corporate",
  "presentation": "masculine",
  "created_at": "2026-03-20T12:01:00Z"
}
```

---

### `GET /generations/`

List all generations for the authenticated user.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Request Body | None                           |

**Response:**

```json
[
  {
    "id": "uuid",
    "status": "completed",
    "style": "corporate",
    "presentation": "masculine",
    "created_at": "2026-03-20T12:01:00Z"
  }
]
```

---

### `GET /generations/{id}`

Get the status and details of a specific generation. Used for polling during AI processing.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Request Body | None                           |

**Response:**

```json
{
  "id": "uuid",
  "status": "completed",
  "style": "corporate",
  "presentation": "masculine",
  "created_at": "2026-03-20T12:01:00Z",
  "completed_at": "2026-03-20T12:04:30Z"
}
```

**Possible `status` values:**

| Status        | Meaning                              |
|---------------|--------------------------------------|
| `pending`     | Job created, not yet started         |
| `processing`  | AI pipeline is running               |
| `completed`   | All headshots generated successfully |
| `failed`      | Generation encountered an error      |

The client polls this endpoint every 5 seconds (max 120 attempts / 10 minutes) until the status is terminal (`completed` or `failed`).

---

### `GET /generations/{id}/images`

Retrieve the generated headshot images for a completed generation.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Request Body | None                           |

**Response:**

```json
{
  "generation_id": "uuid",
  "images": [
    {
      "id": "uuid",
      "url": "https://blob.studioface.app/...",
      "style": "corporate",
      "created_at": "2026-03-20T12:04:30Z"
    }
  ]
}
```

---

## Payments

### `POST /checkout/`

Create a Stripe checkout session for a generation. Returns the Stripe-hosted payment URL.

| Field        | Value                          |
|--------------|--------------------------------|
| Auth         | Yes — `Bearer <token>` header  |
| Content-Type | application/json               |

**Request Body:**

```json
{
  "generation_id": "uuid"
}
```

**Response:**

```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/...",
  "session_id": "cs_live_..."
}
```

The client opens `checkout_url` in the browser. After successful payment, Stripe redirects the user to `/payment/success`.

---

## Error Codes

All `4xx` and `5xx` responses include a `detail` field. The Flet client maps these to structured errors:

| HTTP Status | Meaning                     |
|-------------|-----------------------------|
| 400         | Bad request / validation     |
| 401         | Not authenticated            |
| 403         | Forbidden                    |
| 404         | Resource not found           |
| 409         | Conflict (duplicate)         |
| 422         | Validation error             |
| 429         | Rate limited                 |
| 500         | Internal server error        |
| 502/503/504 | Gateway error (auto-retried) |

The client automatically retries on `502`, `503`, and `504` with exponential backoff (up to 3 attempts).

---

## Authentication Header

All authenticated endpoints require:

```
Authorization: Bearer <token>
```

The token is obtained via magic-link verification (`POST /auth/verify`) and stored in the browser's `client_storage` for session persistence across page reloads.
