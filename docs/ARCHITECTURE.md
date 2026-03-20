# StudioFace — Architecture Document

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                             │
│                                                                     │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │                     Flet Web App                              │ │
│   │                                                               │ │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │ │
│   │  │ Landing  │  │  Login   │  │  Create  │  │   Gallery    │ │ │
│   │  │  Page    │  │  Page    │  │  Wizard  │  │    Page      │ │ │
│   │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘ │ │
│   │       │              │             │               │         │ │
│   │  ┌────┴──────────────┴─────────────┴───────────────┴───────┐ │ │
│   │  │                   Shared Components                     │ │ │
│   │  │  Navbar · Footer · LanguagePicker · CookieBanner · ...  │ │ │
│   │  └────────────────────────┬────────────────────────────────┘ │ │
│   │                           │                                   │ │
│   │  ┌────────────────────────┴────────────────────────────────┐ │ │
│   │  │                   Service Layer                         │ │ │
│   │  │  api_client · auth_service · upload_service · ...       │ │ │
│   │  └────────────────────────┬────────────────────────────────┘ │ │
│   │                           │                                   │ │
│   │  ┌────────────────────────┴────────────────────────────────┐ │ │
│   │  │              Core: i18n · theme · state                 │ │ │
│   │  └─────────────────────────────────────────────────────────┘ │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                           │                                         │
│                      WebSocket                                      │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                       HTTPS / REST
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                    StudioFace API (FastAPI)                          │
│                           │                                         │
│   ┌───────────────────────┴─────────────────────────────────────┐   │
│   │  /auth   /upload   /generations   /checkout   /health       │   │
│   └───────────────────────┬─────────────────────────────────────┘   │
│                           │                                         │
│          ┌────────────────┼────────────────┐                        │
│          │                │                │                        │
│   ┌──────┴──────┐  ┌─────┴──────┐  ┌──────┴──────┐                │
│   │  Azure SQL  │  │Azure Blob  │  │  Azure AI   │                │
│   │  Database   │  │  Storage   │  │  Services   │                │
│   └─────────────┘  └────────────┘  └─────────────┘                │
│                                                                     │
│                    ┌─────────────┐                                   │
│                    │   Stripe    │                                   │
│                    │  Payments   │                                   │
│                    └─────────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Tech Stack Justification

### Why Flet?

- **Single-language stack** — The entire frontend is Python, matching the FastAPI backend. No JavaScript/TypeScript context-switching required.
- **Flutter under the hood** — Flet compiles to Flutter, giving native-quality rendering on web, desktop, and mobile from a single codebase.
- **Material Design 3** — Built-in MD3 widget set means professional-looking UI without a separate component library.
- **Async-first** — Native `async/await` support aligns with the async HTTP calls to the backend.
- **Rapid prototyping** — Ideal for an academic MVP where time-to-ship matters more than frontend ecosystem maturity.

### Why httpx?

- **Async HTTP client** — First-class `asyncio` support, unlike `requests`.
- **Connection pooling** — Reuses connections across the application lifetime.
- **Timeout and retry** — Built-in timeout configuration; the `StudioFaceAPI` wrapper adds automatic retry with exponential backoff on 502/503/504.
- **Streaming support** — Can handle large file uploads efficiently via multipart form data.

### Why python-dotenv?

- **Simple config** — Loads `.env` files into `os.environ` at startup.
- **Standard practice** — Keeps secrets out of code and version control.
- **Zero dependencies** — Lightweight, no framework lock-in.

### Why Pillow?

- **Image validation** — Verifies uploaded files are valid images before sending to the backend.
- **Format detection** — Confirms JPG/PNG format at the byte level, not just file extension.
- **Python standard** — The canonical image library for Python.

## Page Descriptions

### Landing Page (`/`)

Marketing page with three sections:
1. **Hero** — Headline, subtitle, primary CTA button ("Get Started — EUR 6.99"), generated photo counter.
2. **How It Works** — Three-step feature cards: Upload, Choose Style, Get Headshots.
3. **Pricing** — Single-tier pricing card with feature list and CTA.

Includes the shared navbar, footer, cookie banner, and language picker.

### Login Page (`/login`)

Two authentication options:
1. **Magic Link** — User enters email, receives a one-time sign-in link.
2. **Microsoft OAuth** — Button redirects to Microsoft login, returns with a token.

After successful auth, the token is stored in `client_storage` and the user is redirected to `/create`.

### Create Page (`/create`)

Three-step wizard with progress tracker:
1. **Upload** — File picker for 2-5 selfie photos (JPG/PNG, max 10 MB each). Files are uploaded to a backend session.
2. **Style** — Grid of 6 style cards (Corporate, Medical, Banking, Startup, Casual, Tech) with icons and descriptions.
3. **Attire** — Binary choice between masculine and feminine presentation.

After selection, triggers generation and redirects to Stripe checkout.

### Gallery Page (`/gallery`)

Displays the user's generated headshots in a responsive grid. Each headshot card shows the image, style label, and creation date. Supports individual and bulk download. Handles four generation states: completed, partial, failed, and processing (with polling).

### Payment Success Page (`/payment/success`)

Post-Stripe confirmation screen. Shows a success message, a note that an email will arrive when images are ready, and a button to navigate to the gallery.

### Not Found Page (`*`)

404 error page with a message and a button to return to the landing page.

## State Management

The app uses a layered state approach:

### Page Session (`page.session`)

Flet's built-in per-session key-value store. Used for:
- `api` — The `StudioFaceAPI` client instance
- `lang` — Current language code (`en`, `es`, `de`)
- `user` — Authenticated user dict (or absent if logged out)
- `current_generation_id` — Active generation being tracked
- `upload_session_id` — Active upload session

### Client Storage (`page.client_storage`)

Browser-side persistent storage (survives page reloads). Used for:
- `sf_token` — Auth token for session restoration

### AppState Class (`app/state.py`)

A convenience wrapper around `page.session` with typed properties. Provides `lang`, `user`, `is_authenticated`, `current_generation_id`, and `upload_session_id` as Python properties with getters and setters.

### Data Flow

```
User interaction
    → Page handler (async function)
        → Service layer (auth_service, upload_service, etc.)
            → StudioFaceAPI._request() (HTTP call)
                → Backend API
            ← JSON response
        ← Dict result
    ← UI update via page.update_async()
```

## Authentication Flow

### Magic Link Flow

```
1. User enters email on /login
2. Client calls POST /auth/magic-link { email }
3. Backend sends email with a one-time token link
4. User clicks link (opens app with token in URL)
5. Client calls POST /auth/verify { token }
6. Backend validates token, returns user data + JWT
7. Client stores JWT in client_storage
8. Client sets user in page.session
9. Redirect to /create
```

### Microsoft OAuth Flow

```
1. User clicks "Sign in with Microsoft" on /login
2. Client calls GET /auth/microsoft/url
3. Backend returns Microsoft OAuth URL
4. Client opens URL in browser (page.launch_url_async)
5. User authenticates with Microsoft
6. Microsoft redirects back with auth code
7. Backend exchanges code for token, returns JWT
8. Client stores JWT in client_storage
9. Client sets user in page.session
10. Redirect to /create
```

### Session Restoration

On every app load (`main()`):
1. Read `sf_token` from `client_storage`
2. If present, call `GET /auth/me` with the token
3. If valid, set `user` in session — user is logged in
4. If invalid (401), clear stored token — user sees logged-out state

## Upload, Generate, and Payment Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Upload     │     │   Generate   │     │   Payment    │
│   Photos     │────▶│   Request    │────▶│   Checkout   │
│   (2-5)      │     │              │     │   (Stripe)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
  POST /upload/        POST /generations/   POST /checkout/
  session              (creates job)        (returns URL)
       │                    │                    │
  POST /upload/{id}    Poll GET               Stripe hosted
  (per file)           /generations/{id}      checkout page
       │               every 5s                  │
       │                    │                    │
       │              GET /generations/     Redirect to
       │              {id}/images           /payment/success
       │              (when complete)            │
       └────────────────────┴────────────────────┘
```

### Step-by-step:

1. **Create upload session** — `POST /upload/session` returns a `session_id`.
2. **Upload files** — For each photo, `POST /upload/{session_id}` with multipart form data.
3. **Create generation** — `POST /generations/` with `upload_session_id`, `style`, and `presentation`.
4. **Start checkout** — `POST /checkout/` with `generation_id`. Backend creates a Stripe session and returns the `checkout_url`.
5. **User pays** — Stripe-hosted checkout page. On success, Stripe redirects to `/payment/success`.
6. **Poll for completion** — Client polls `GET /generations/{id}` every 5 seconds until `status` is `completed` or `failed` (max 10 minutes).
7. **Fetch images** — `GET /generations/{id}/images` returns URLs to the generated headshots stored in Azure Blob Storage.

## Internationalization (i18n)

### Architecture

All UI strings are defined in `app/i18n.py` as a nested dict:

```python
TRANSLATIONS = {
    "en": { "hero.title": "Professional AI Headshots", ... },
    "es": { "hero.title": "Fotos Profesionales con IA", ... },
    "de": { "hero.title": "Professionelle KI-Portratfotos", ... },
}
```

### Translation Function

```python
t(key: str, lang: str = "en", **kwargs) -> str
```

- Looks up `key` in the `lang` dict.
- Falls back to `"en"` if missing.
- Returns the key itself if not found in any language.
- Supports `str.format()` interpolation: `t("create.uploaded_count", lang="en", count=3)` returns `"3 photo(s) uploaded"`.

### Language Switching

- Current language is stored in `page.session` as `lang`.
- The `LanguagePicker` component in the navbar lets users switch between EN, ES, and DE.
- On switch, the page re-renders with the new language.

### Coverage

Each language has 80+ keys covering: landing page, auth, create wizard, gallery, payments, navigation, footer, cookie banner, error messages, and common actions.

## Design System

The visual identity is centralized in `app/theme.py` via the `StudioFaceTheme` class.

### Color Palette

| Token            | Value     | Usage                        |
|------------------|-----------|------------------------------|
| PRIMARY          | `#1A237E` | Indigo — buttons, headers    |
| PRIMARY_LIGHT    | `#534BAE` | Hover states, gradients      |
| SECONDARY        | `#FF6F00` | Amber — CTAs, accents        |
| BACKGROUND       | `#FAFAFA` | Page background              |
| SURFACE          | `#FFFFFF` | Cards, modals                |
| ERROR            | `#D32F2F` | Error states                 |
| SUCCESS          | `#388E3C` | Success states               |

### Spacing (4px Grid)

```
XS=4  SM=8  MD=16  LG=24  XL=32  XXL=48  HERO=64
```

### Typography

```
HERO=48px  H1=36  H2=28  H3=22  H4=18  BODY=16  CAPTION=14  SMALL=12
```

### Border Radius

```
SM=8  MD=12  LG=24  PILL=100
```

### Breakpoints

```
MOBILE_MAX = 600px
TABLET_MAX = 1024px
MAX_WIDTH  = 1200px
```

### Style Cards

Each headshot style has a dedicated color and icon:

| Style      | Color     | Icon             |
|------------|-----------|------------------|
| Corporate  | `#1A237E` | business_center  |
| Medical    | `#1565C0` | local_hospital   |
| Banking    | `#283593` | account_balance  |
| Startup    | `#FF6F00` | rocket_launch    |
| Casual     | `#388E3C` | emoji_people     |
| Tech       | `#6A1B9A` | computer         |
