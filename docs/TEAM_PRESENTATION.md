# StudioFace Flet Frontend — Team Presentation Guide

**MCSBT @ IE University Madrid | 2026**

Total presentation time: ~25 minutes (5 minutes per module)

---

## Module 1: Architecture & Infrastructure

**Presenter:** Person 1

### What It Covers

This module explains why Flet was chosen as the frontend framework, how the application architecture works from browser to backend, and how the routing, theming, and deployment systems are structured. It sets the technical foundation that all other modules build upon.

### Key Files to Present

- `app/main.py` — Application entry point, routing logic
- `app/theme.py` — Complete design system (colors, spacing, typography)
- `requirements.txt` — Dependencies

### Talking Points

1. **Why Flet over alternatives.** React requires JavaScript expertise our team doesn't have. Flutter requires learning Dart. Streamlit is too limited for a multi-page SPA with routing. Gradio is designed for ML model demos, not full applications. Django templates produce server-rendered HTML, not an SPA experience. Flet lets us write Python exclusively and get a Material Design SPA powered by Flutter's rendering engine. One codebase targets web, desktop, and mobile.

2. **How server-side rendering works.** Unlike React or Vue where the browser runs JavaScript, Flet runs all UI logic on the server in Python. The server builds a Flutter widget tree and sends it to the browser, which renders it as a canvas application. User interactions (clicks, input) are sent back to the server as events. This means zero JavaScript on the client side — the browser is essentially a thin rendering layer.

3. **Routing with page.controls.** The `navigate()` function in `main.py` is the router. On each route change, it clears `page.controls`, imports the matching page module, calls its `build(page)` function, and extends the page controls with the returned list. Query parameters are stripped for route matching but preserved for pages like auth callback that need them. This is a simple, explicit routing system with no external router library.

4. **Design system architecture.** The `StudioFaceTheme` class is a single source of truth for all visual constants: 5 background shades, gold/amber primary palette, 6 text colors, spacing on a 4px grid (4/8/16/24/32/48/64/96), 5 border radius values, and 10 typography sizes. Every component references these constants instead of hardcoding values, ensuring visual consistency across the entire application.

### Demo Scenario

Open `app/main.py` and walk through a route change. Show how navigating to `/create` clears the page, imports `app.pages.create`, calls `build(page)`, and renders the result. Then open `app/theme.py` and show how changing `BG_PRIMARY` from `#131314` to a lighter color would update the background of every page in the application.

### Duration: ~5 minutes

---

## Module 2: Authentication & Security

**Presenter:** Person 2

### What It Covers

This module covers both authentication methods (magic link email and Microsoft OAuth), how tokens are managed throughout the session lifecycle, the automatic token refresh mechanism, and GDPR compliance features including the cookie consent banner.

### Key Files to Present

- `app/pages/login.py` — Login page UI (first 30 lines for structure)
- `app/pages/auth_callback.py` — Token verification and redirect handling
- `app/services/auth_service.py` — Authentication business logic and token storage
- `app/services/api_client.py` — Token refresh logic (lines 128-160, the `_try_refresh` method)
- `app/components/cookie_banner.py` — GDPR cookie consent

### Talking Points

1. **Magic link email flow.** The user enters their email on the login page. The frontend sends `POST /auth/magic-link` to the backend, which sends an email containing a one-time link. When the user clicks that link, they are redirected to `/auth/callback?token=<value>`. The callback page sends `POST /auth/magic-link/verify` to exchange the token for JWT access and refresh tokens. No password is ever stored or transmitted. This is the same pattern used by Slack, Notion, and other modern SaaS products.

2. **Microsoft OAuth flow.** The frontend calls `GET /auth/microsoft/url` to get an authorization URL, then launches it in the browser. Microsoft handles the login and redirects back to `/auth/callback?code=<value>&state=<csrf>`. The callback page sends `POST /auth/microsoft/callback` with the code and state to exchange for tokens. The state parameter prevents CSRF attacks — if the state doesn't match what the server generated, the login is rejected.

3. **Automatic token refresh.** The API client (`api_client.py`) intercepts 401 responses on any request. Before failing, it calls `POST /auth/refresh` with the stored refresh token. If successful, it updates both tokens, notifies a registered callback (which persists the new tokens to the session), and retries the original request. This happens transparently — the user never sees a "session expired" message. The refresh is skipped for auth endpoints themselves to avoid infinite loops.

4. **GDPR compliance.** The cookie banner uses a session key (`studioface_cookie_consent`) to track whether the user has accepted or declined cookies. The login page includes a mandatory GDPR consent checkbox. The API supports data export (`POST /users/me/export`) and account deletion (`DELETE /users/me`). All of these comply with the EU's General Data Protection Regulation requirements.

### Alternatives Considered

- **Firebase Auth:** Would add vendor lock-in to Google Cloud. Our backend already has its own auth system.
- **Auth0:** Powerful but expensive for an MVP and adds a third-party dependency.
- **Supabase Auth:** Good option but would require Supabase infrastructure. Our backend uses its own database.
- **Custom JWT from scratch:** What we effectively use, but through the backend API rather than implementing JWT in the frontend.
- **Why our approach:** Uses the existing backend's OAuth implementation. No additional vendor lock-in. Supports both passwordless (magic link) and enterprise (Microsoft) login flows.

### Demo Scenario

Walk through the login page. Enter an email, show the magic link being sent (API call in the network log). Then show the auth callback page parsing URL parameters. Open `auth_service.py` and trace how `_store_auth_result` saves tokens to both the API client and the page session. Finally, show the cookie banner appearing on first visit and disappearing after accepting.

### Duration: ~5 minutes

---

## Module 3: Upload & Camera

**Presenter:** Person 3

### What It Covers

This module explains how users get their selfie photos into the application — through file upload (the primary method) and webcam capture (the secondary method). It covers the file picker integration, camera control, file validation, and the upload pipeline to the backend API.

### Key Files to Present

- `app/pages/create.py` — Create wizard, Step 1 (first 30 lines for structure)
- `app/components/upload_zone.py` — File upload area component
- `app/services/upload_service.py` — Validation and upload logic
- `app/services/api_client.py` — Upload endpoints (lines 346-374)

### Talking Points

1. **File picker integration in Flet 0.82.** Flet's `FilePicker` is an async control. The `pick_files()` method returns a coroutine, so we can't call it directly from a synchronous button click handler. Instead, we wrap it in an async function and use `page.run_task()` to schedule it. The file picker dialog allows multiple file selection, filters for JPG/JPEG/PNG extensions, and shows a native OS file dialog. When files are picked, the callback receives a list of file results with name, path, and size.

2. **Camera capture with flet-camera.** The `flet-camera` package provides webcam access in the browser. It's imported conditionally with a try/except block — if the package isn't available (e.g., in a desktop environment without a webcam), the camera option is gracefully hidden. The camera feed is displayed in a container with Capture and Flip Camera buttons. Captured photos are added to the same uploaded files list as picked files, so the rest of the pipeline treats them identically.

3. **File validation.** Before upload, every file goes through two validation checks. `validate_file()` checks the extension (must be .jpg, .jpeg, or .png) and size (must be under 10 MB). `validate_file_count()` checks the total count (must be between 2 and 5). If validation fails, the relevant i18n error key is returned (e.g., `create.invalid_format`, `create.file_too_large`) and displayed to the user. Validation happens client-side before any API calls are made.

4. **Upload pipeline.** The `create_session_and_upload()` function orchestrates the full upload: first, it creates an upload session via `POST /uploads/sessions` to get a session UUID. Then it uploads each file sequentially via `POST /uploads/` as multipart form data, passing the session ID. Each upload returns a file UUID. If any upload fails, the function returns immediately with the error. On success, it returns the session ID and list of upload UUIDs, which are needed for the generation step.

### Alternatives Considered

- **HTML5 `<input type="file">`:** Not available in Flet's Python-to-Flutter pipeline. Flet provides its own FilePicker abstraction.
- **WebRTC directly:** Would require JavaScript interop, which defeats the purpose of using Flet's Python-only approach.
- **Third-party upload SDKs (Filestack, Uploadcare):** Adds cost and external dependencies for a simple upload use case.
- **Why our approach:** Uses Flet's native FilePicker and flet-camera controls. No JavaScript interop needed. Cross-platform compatible. File validation runs locally before any network requests.

### Demo Scenario

Open the Create page and demonstrate Step 1. Click "Choose Photos" to show the file picker dialog. Select some images and show the file chips appearing with filenames and the upload count. Try uploading a file that's too large or wrong format to show the validation error. If a webcam is available, demonstrate the camera capture. Then show the upload service code that creates a session and uploads files sequentially to the API.

### Duration: ~5 minutes

---

## Module 4: Generation & Payment

**Presenter:** Person 4

### What It Covers

This module covers the core business flow: the 3-step wizard (upload, style selection, attire selection), the Stripe payment integration, generation polling, and the payment result pages. This is where the user's journey converts into revenue.

### Key Files to Present

- `app/pages/create.py` — 3-step wizard flow (Steps 2 and 3)
- `app/components/style_card.py` — Visual style selection cards
- `app/components/progress_tracker.py` — Step indicator component
- `app/services/generation_service.py` — Generation creation and polling
- `app/services/payment_service.py` — Stripe checkout
- `app/pages/payment_success.py` — Success confirmation
- `app/pages/payment_cancel.py` — Cancellation handling

### Talking Points

1. **3-step wizard design.** The Create page manages a `current_step` state variable (0, 1, 2). Step 0 is Upload (covered in Module 3). Step 1 is Style — users select from 6 style cards (Corporate, Medical, Banking, Startup, Casual, Tech), each showing a real example photo, style name, and description. The selected card gets a gold border and checkmark badge. Step 2 is Attire — users choose Masculine or Feminine presentation, which determines the clothing in the generated headshot. The progress tracker at the top shows completed (green), current (gold), and future (grey) steps with connecting lines. "Continue" and "Back" buttons navigate between steps.

2. **Stripe checkout integration.** When the user clicks "Generate Headshots - EUR 6.99" on the final step, the flow is: (1) upload photos to the API, (2) create a generation job via `POST /generations/`, (3) create a Stripe checkout session via `POST /payments/checkout` with the generation ID, (4) redirect the user to Stripe's hosted checkout page. Stripe handles the entire payment form — credit card input, 3D Secure, Apple Pay, Google Pay. After payment, Stripe redirects to either `/payment/success` or `/payment/cancel`.

3. **Generation polling.** After payment, the backend triggers the AI generation. The `poll_generation()` function calls `GET /generations/{id}` every 5 seconds, checking for status changes. It polls for up to 120 attempts (10 minutes). Status values progress through `pending` -> `processing` -> `completed` or `failed`. When completed, the response includes image URLs. An optional `on_update` callback allows the UI to show progress updates during polling.

4. **Payment result pages.** The success page shows a gold checkmark, "Payment Confirmed!", and a "View My Headshots" button linking to the gallery. The cancel page shows a grey cancel icon, "Payment Cancelled", a reassuring "No charges were made" message, and a "Retry" button back to the Create page. Both pages are fully responsive and translated in all 3 languages.

### Alternatives Considered

- **PayPal:** Less developer-friendly API, higher fees in Europe. Stripe is the industry standard for SaaS.
- **Paddle:** Good for SaaS but overkill for a single product with one price point.
- **LemonSqueezy:** Simpler but less mature. Limited payment method support in EU.
- **In-app purchase:** Not applicable for a web application.
- **Why Stripe:** PCI DSS compliance handled by Stripe (we never touch card data). Full EU payment method support (cards, iDEAL, Bancontact, etc.). Reliable webhooks for payment confirmation. Hosted checkout page eliminates PCI scope for our application entirely.

### Demo Scenario

Start from Step 1 with files already uploaded. Click "Continue" to Step 2 (Style). Click on different style cards to show the selection state changing (gold border, checkmark). Click "Continue" to Step 3 (Attire). Select a presentation option and click "Generate Headshots". Show the Stripe checkout redirect. Then demonstrate the Payment Success page and trace how the "View My Headshots" button navigates to the gallery.

### Duration: ~5 minutes

---

## Module 5: Internationalization & UX

**Presenter:** Person 5

### What It Covers

This module covers the translation system supporting 3 languages, the responsive design system that adapts to mobile/tablet/desktop, the dark premium theme implementation, and the UX patterns for loading states, error handling, and empty states throughout the application.

### Key Files to Present

- `app/i18n.py` — Translation dictionary and `t()` function
- `app/components/language_picker.py` — Language switching dropdown
- `app/theme.py` — Design system constants (colors, spacing, typography)
- `app/components/loading_spinner.py` — Loading state component
- `app/components/headshot_card.py` — Three-state card (loading, error, loaded)
- `app/pages/not_found.py` — Error state page

### Talking Points

1. **Translation system.** All 103+ user-facing strings across 3 languages live in a single Python dictionary in `i18n.py`. The `t(key, lang, **kwargs)` function looks up a key in the requested language, falls back to English if missing, and returns the key itself if not found anywhere (making missing translations obvious during development). Variable interpolation uses Python's `str.format()` — for example, `t("create.uploaded_count", "en", count=3)` returns "3 photo(s) uploaded". This is simpler and more maintainable than external i18n libraries like i18next (JavaScript) or gettext (Python) — no .po files, no compilation step, no external dependencies. Adding a new language means adding one more dictionary entry.

2. **Language switching.** The language picker is a dark-styled Flet Dropdown with flag emojis (English, Espanol, Deutsch). When the user selects a language, it's stored in `page.session.store`, and the current route is re-navigated (effectively a full re-render). Every component reads the language from session at build time and passes it to the `t()` function. This means a language change instantly updates all text on the page — navbar, content, footer, buttons, error messages — everything.

3. **Responsive design.** Every page checks `is_mobile = page_width < MOBILE_MAX (600px)` and adjusts its layout accordingly. On mobile: font sizes shrink (FONT_HERO 56px becomes FONT_H1 40px), padding reduces (24px becomes 16px), horizontal rows become vertical columns, the navbar shows a hamburger menu instead of text links, and the results gallery becomes horizontally scrollable. The theme provides `MOBILE_MAX = 600` and `TABLET_MAX = 1024` breakpoints. The landing page style cards use `ResponsiveRow` with `col={"xs": 12, "sm": 6, "md": 4}` for a true responsive grid.

4. **UX states and the dark premium theme.** Every user-facing operation has three visual states: loading (gold spinner with optional message), success (content display), and error (red icon with message and retry option). The headshot card component demonstrates this perfectly — it renders a spinner during loading, a red error icon on failure, or the actual image on success. The dark theme (#131314 background, #F59E0B gold accents) creates a premium feel similar to professional photography studio websites. Even the 404 page is designed with a giant muted "404" text and a gold "Go Home" button — no generic error page.

### Alternatives Considered

- **i18next (JavaScript):** Industry standard for React/Vue apps, but requires JavaScript which defeats the purpose of a Python-only Flet app.
- **gettext (Python):** Well-established but requires .po file compilation, message extraction tools, and adds complexity for 3 languages.
- **ICU MessageFormat:** Powerful for complex pluralization rules (Arabic, Russian), but overkill for EN/ES/DE which have simple plural forms.
- **Why our approach:** A simple Python dictionary is readable by non-developers, requires no build tools, has zero external dependencies, and is easy to extend. For 3 languages with 103 keys each, this is the right level of complexity.

### Demo Scenario

Open the landing page in English. Switch to Spanish using the language picker — show how every piece of text on the page updates instantly (hero, features, pricing, styles, navigation, footer). Switch to German. Then resize the browser window from desktop to mobile width and show how the layout adapts: navbar collapses to hamburger, content stacks vertically, font sizes adjust. Finally, navigate to an invalid URL like `/xyz` to show the 404 page in the current language.

### Duration: ~5 minutes

---

## Presentation Flow Summary

| Order | Module | Presenter | Time |
|-------|--------|-----------|------|
| 1 | Architecture & Infrastructure | Person 1 | 5 min |
| 2 | Authentication & Security | Person 2 | 5 min |
| 3 | Upload & Camera | Person 3 | 5 min |
| 4 | Generation & Payment | Person 4 | 5 min |
| 5 | Internationalization & UX | Person 5 | 5 min |
| | **Total** | | **25 min** |

### Suggested Live Demo Order

For maximum impact, the live demo should follow the actual user journey:

1. **Person 1** opens the app and shows the landing page rendering, explains the Flet architecture
2. **Person 2** clicks "Sign In", shows the login flow, walks through token handling
3. **Person 3** demonstrates file upload and camera capture on the Create page
4. **Person 4** shows style selection, payment flow, and the success/cancel pages
5. **Person 5** switches languages, resizes the browser, and demonstrates error states

This way the presentation tells a coherent story from first visit to generated headshots.
