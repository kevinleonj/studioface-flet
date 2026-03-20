# StudioFace: React-to-Flet Translation Map

> Generated 2026-03-20 from production frontend analysis + live API testing.

---

## Pages

| React File | Flet File | Status | Notes |
|-----------|-----------|--------|-------|
| `Home.tsx` | `app/pages/landing.py` | DONE | Hero, results carousel, styles grid, pricing cards, FAQ accordion |
| `Login.tsx` | `app/pages/login.py` | NEEDS WIRE | Magic link + Microsoft OAuth + GDPR consent checkbox |
| `AuthCallback.tsx` | `app/pages/auth_callback.py` | MISSING | Reads `?token=` or `?provider=microsoft&code=&state=` from URL, calls verify/callback, stores tokens, redirects to `/create`. **CRITICAL for auth to work.** |
| `Create.tsx` | `app/pages/create.py` | NEEDS WIRE | 3-step flow: Upload photos -> Select style -> Payment. Needs upload session + file upload + generation creation wired. |
| `Gallery.tsx` | `app/pages/gallery.py` | NEEDS WIRE | WebSocket progress bar, image grid display, ZIP download button |
| `PaymentSuccess.tsx` | `app/pages/payment_success.py` | NEEDS WIRE | Stripe confirmation display + auto-redirect to gallery after delay |
| `PaymentCancel.tsx` | `app/pages/payment_cancel.py` | MISSING | Handles Stripe checkout cancellation, offers retry |
| `Settings.tsx` | `app/pages/settings.py` | MISSING | Language selector, GDPR data export, account deletion |
| `Privacy.tsx` | `app/pages/privacy.py` | MISSING | Static privacy policy page |
| `Terms.tsx` | `app/pages/terms.py` | MISSING | Static terms of service page |
| `NotFound.tsx` | `app/pages/not_found.py` | DONE | 404 page with back-to-home link |
| `Admin.tsx` | N/A | SKIP | Admin dashboard not needed for Flet client |

---

## API Endpoints (Real Production vs Current Flet)

Base URL: `https://api.studioface.app/api/v1`

### Health

| Method | Path | React Usage | Current Flet | Correct? | Live Status |
|--------|------|-------------|-------------|----------|-------------|
| GET | `/health/` | `healthApi.check()` | `health_check()` | YES | 200 OK |

### Auth

| Method | Path | React Usage | Current Flet | Correct? | Live Status |
|--------|------|-------------|-------------|----------|-------------|
| POST | `/auth/magic-link` | `authApi.sendMagicLink(email, locale)` | `send_magic_link(email)` | NEEDS `locale` param | 200 (with locale), 422 (empty email) |
| POST | `/auth/magic-link/verify` | `authApi.verifyMagicLink(token)` | `verify_token(token)` | YES | 422 (token too short) |
| GET | `/auth/microsoft/url` | `authApi.getMicrosoftAuthUrl()` | `get_microsoft_auth_url()` | YES | 200 returns auth_url |
| POST | `/auth/microsoft/callback` | `authApi.microsoftCallback(code, state)` | MISSING | ADD | 401 (invalid state = endpoint exists) |
| GET | `/auth/microsoft/callback` | browser redirect landing | N/A (browser handles) | N/A | 302 redirect |
| GET | `/auth/me` | `authApi.getMe()` | `get_current_user()` | YES | 401 (no token) |
| PUT | `/auth/gdpr-consent` | `authApi.updateGdprConsent(consent)` | MISSING | ADD | 401 (no token = exists) |
| POST | `/auth/logout` | `authApi.logout()` sends `{refresh_token}` | `logout()` no body | NEEDS `refresh_token` in body | 401 (requires Bearer + body) |
| POST | `/auth/refresh` | auto in `apiFetch` interceptor | `refresh_token()` exists | YES (method exists) | 401 (invalid token) |

### Uploads

| Method | Path | React Usage | Current Flet | Correct? | Live Status |
|--------|------|-------------|-------------|----------|-------------|
| POST | `/uploads/sessions` | `uploadApi.createSession()` | Uses `/upload/session` | PATH WRONG: fix to `/uploads/sessions` | 401 (exists, needs auth) |
| POST | `/uploads/` | `uploadApi.upload(file, sessionId)` | Uses `/upload/{id}` | PATH WRONG: fix to `/uploads/` with FormData (`file` + `upload_session_id`) | 401 (exists, needs auth) |

> OLD path `/upload/session` returns **404**. The correct path is `/uploads/sessions`.

### Generations

| Method | Path | React Usage | Current Flet | Correct? | Live Status |
|--------|------|-------------|-------------|----------|-------------|
| POST | `/generations/` | `generationApi.create({style, upload_ids, presentation, upload_session_id})` | `create_generation(session_id, style, presentation)` | MISSING `upload_ids` in payload | 401 (needs auth) |
| GET | `/generations/{id}` | `generationApi.get(id)` | `get_generation(id)` | YES | (needs auth) |
| GET | `/generations/` | `generationApi.list(page, pageSize)` | `list_generations()` | NEEDS `page` + `page_size` params | 401 (needs auth) |

### Payments

| Method | Path | React Usage | Current Flet | Correct? | Live Status |
|--------|------|-------------|-------------|----------|-------------|
| POST | `/payments/checkout` | `paymentApi.createCheckout(genId, currency)` | Uses `/payments/create-checkout` | PATH WRONG: fix to `/payments/checkout` | 401 (exists, needs auth) |
| GET | `/payments/` | `paymentApi.list()` | MISSING | ADD | 401 (exists, needs auth) |

> OLD path `POST /payments/create-checkout` returns **405 Method Not Allowed**. Correct endpoint: `POST /payments/checkout`.

### User Settings

| Method | Path | React Usage | Current Flet | Correct? | Live Status |
|--------|------|-------------|-------------|----------|-------------|
| PUT | `/users/me/locale` | `userApi.updateLocale(locale)` | MISSING | ADD | 401 (exists, needs auth) |
| POST | `/users/me/export` | `userApi.exportData()` | MISSING | ADD | 401 (exists, needs auth) |
| DELETE | `/users/me` | `userApi.deleteAccount()` | MISSING | ADD | 401 (exists, needs auth) |

---

## Auth Flow

### Microsoft OAuth

```
1. Client calls GET /auth/microsoft/url
   → Returns { auth_url: "https://login.microsoftonline.com/..." }

2. Client opens auth_url in browser (or WebView)
   → User signs in with Microsoft account

3. Microsoft redirects to: https://api.studioface.app/api/v1/auth/microsoft/callback?code=...&state=...
   → Backend processes the code, then 302 redirects to:
     https://app.studioface.app/auth/callback?provider=microsoft&code=...&state=...

4. AuthCallback page reads URL params:
   - provider = "microsoft"
   - code = "..."
   - state = "..."

5. Client calls POST /auth/microsoft/callback with { code, state }
   → Returns { access_token, refresh_token, user: {...} }

6. Client stores sf_access_token + sf_refresh_token
   → Redirects to /create
```

### Magic Link

```
1. Client calls POST /auth/magic-link with { email, locale }
   → Returns { message: "Magic link sent to your email", success: true }

2. User clicks link in email
   → Opens: https://app.studioface.app/auth/callback?token=...

3. AuthCallback page reads URL params:
   - token = "eyJhbGciOiJIUzI1NiIs..." (min 32 chars)

4. Client calls POST /auth/magic-link/verify with { token }
   → Returns { id, email, name, token } (and likely refresh_token)

5. Client stores sf_access_token + sf_refresh_token
   → Redirects to /create
```

### Token Refresh (Automatic)

```
1. Any API call returns 401
2. Client checks if refresh_token exists
3. POST /auth/refresh with { refresh_token }
   → Returns { access_token, refresh_token } (new pair)
4. Client stores new tokens
5. Original request is retried with new access_token
6. If refresh also fails → redirect to /login
```

### Logout

```
1. POST /auth/logout with:
   - Header: Authorization: Bearer <access_token>
   - Body: { refresh_token: "..." }
2. Server invalidates both tokens
3. Client clears sf_access_token + sf_refresh_token
4. Redirect to /login
```

---

## Token Storage

| Token | React (Browser) | Flet (Desktop/Web) |
|-------|-----------------|-------------------|
| Access Token | `localStorage["sf_access_token"]` | `page.client_storage` (persists) or `page.session` (in-memory) |
| Refresh Token | `localStorage["sf_refresh_token"]` | `page.client_storage` (persists) or `page.session` (in-memory) |

**Recommendation for Flet:** Use `page.client_storage` for web deployments (maps to localStorage). For desktop, use `page.client_storage` which persists across restarts. Fall back to `page.session` for ephemeral sessions.

---

## Generation Flow

### Step 1: Upload Photos

```
1. POST /uploads/sessions (auth required)
   → Returns { id: "session-uuid", ... }

2. For each photo file:
   POST /uploads/ (auth required)
   Content-Type: multipart/form-data
   Body: FormData {
     file: <binary>,
     upload_session_id: "session-uuid"
   }
   → Returns { id: "upload-uuid", ... }
```

### Step 2: Select Style

User picks from 6 styles:
- `CORPORATE` - Professional corporate headshots
- `STARTUP` - Modern startup look
- `TECH` - Technology industry style
- `BANKING` - Financial/banking professional
- `MEDICINE` - Medical professional
- `CASUAL` - Casual professional

User picks presentation:
- `masculine`
- `feminine`

### Step 3: Create Generation

```
POST /generations/ (auth required)
Body: {
  "style": "CORPORATE",
  "upload_ids": ["upload-uuid-1", "upload-uuid-2", ...],
  "presentation": "masculine",
  "upload_session_id": "session-uuid"
}
→ Returns { id: "generation-uuid", status: "pending", ... }
```

### Step 4: Payment

```
POST /payments/checkout (auth required)
Body: {
  "generation_id": "generation-uuid",
  "currency": "EUR"  // or "USD", etc.
}
→ Returns {
    "checkout_url": "https://checkout.stripe.com/c/pay/...",
    "session_id": "cs_live_..."
  }

Client opens checkout_url in browser.
Stripe redirects to:
  - Success: /payment/success?session_id=cs_live_...
  - Cancel: /payment/cancel
```

### Step 5: Progress Tracking (WebSocket)

```
WebSocket: wss://api.studioface.app/api/v1/generations/ws/{generation_id}

1. Client connects to WebSocket
2. Client sends auth token: { "token": "..." }
3. Server sends progress updates:
   { "status": "processing", "progress": 45, "message": "Generating headshots..." }
   { "status": "processing", "progress": 80, "message": "Applying style..." }
   { "status": "completed", "progress": 100 }
4. Client closes connection on "completed" or "failed"
```

### Step 6: Gallery / Results

```
GET /generations/{id} (auth required)
→ Returns {
    "id": "...",
    "status": "completed",  // pending | processing | completed | failed
    "images": [
      { "id": "img-1", "url": "https://...", "thumbnail_url": "https://..." },
      ...
    ]
  }

Images are displayed in a grid.
ZIP download bundles all images.
```

---

## WebSocket Connection Details

| Field | Value |
|-------|-------|
| URL Pattern | `wss://api.studioface.app/api/v1/generations/ws/{generation_id}` |
| Auth | Send `{"token": "..."}` as first message after connect |
| Messages | JSON: `{status, progress, message}` |
| Status values | `processing`, `completed`, `failed` |
| Progress | Integer 0-100 |
| Close | Client closes after `completed` or `failed` |

---

## Styles Reference

| Style Key | Display Name | Description |
|-----------|-------------|-------------|
| `CORPORATE` | Corporate | Professional corporate headshots |
| `STARTUP` | Startup | Modern startup aesthetic |
| `TECH` | Tech | Technology industry style |
| `BANKING` | Banking | Financial services professional |
| `MEDICINE` | Medicine | Medical professional |
| `CASUAL` | Casual | Casual professional |

---

## Error Response Formats

The backend uses two error formats:

### FastAPI Validation Error (422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "",
      "ctx": {"reason": "..."}
    }
  ]
}
```

### Custom Application Error (400/401/403/404/409)
```json
{
  "error": {
    "code": "AUTH_FAILED",
    "message": "Authentication required. Please provide a Bearer token.",
    "details": {}
  }
}
```

### Flet Client Normalization

Both formats are normalized to:
```python
{"error": "message string", "code": "HTTP_STATUS_OR_CODE", "status": 401}
```

---

## Changes Summary (What Must Be Fixed)

### Path Corrections
1. `/upload/session` -> `/uploads/sessions` (404 on old path)
2. `/upload/{session_id}` -> `/uploads/` with FormData body
3. `/payments/create-checkout` -> `/payments/checkout` (405 on old path with POST)

### Missing Methods to Add
1. `microsoft_callback(code, state)` - POST `/auth/microsoft/callback`
2. `update_gdpr_consent(consent)` - PUT `/auth/gdpr-consent`
3. `update_locale(locale)` - PUT `/users/me/locale`
4. `export_data()` - POST `/users/me/export`
5. `delete_account()` - DELETE `/users/me`
6. `list_payments()` - GET `/payments/`

### Methods to Fix
1. `send_magic_link()` - add `locale` parameter
2. `logout()` - add `refresh_token` in request body
3. `create_generation()` - add `upload_ids` to payload
4. `list_generations()` - add `page` + `page_size` params
5. `create_checkout()` - add `currency` param, fix path

### Missing Pages
1. `auth_callback.py` - CRITICAL for completing auth flow
2. `payment_cancel.py` - Stripe cancellation handling
3. `settings.py` - Language, GDPR export, account deletion
4. `privacy.py` - Privacy policy
5. `terms.py` - Terms of service

### Token Refresh Logic
Add 401 auto-retry to `_request()`:
1. On 401 response, attempt token refresh
2. On refresh success, retry original request with new token
3. On refresh failure, return 401 (caller redirects to login)
