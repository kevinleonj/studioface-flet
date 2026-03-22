# StudioFace Flet Frontend — Component Technical Documentation

This document provides inline-style technical documentation for every page and component in the application.

---

## Pages

---

### app/pages/landing.py

```
Purpose: Marketing landing page for StudioFace — first page visitors see
Sections: Hero, Results Gallery, How It Works, Style Showcase, Pricing
Build Function: build(page) -> list[ft.Control]
Internal Functions:
  - _build_hero(page): Gold pill badge, heading with italic accent word, price line, subtitle, CTA button, trust bar
  - _build_results_gallery(page): Horizontal row of 5 sample customer headshots (from T.SAMPLE_PHOTOS)
  - _build_how_it_works(page): Three numbered dark cards with icons explaining the 3-step process
  - _build_style_showcase(page): Six responsive style cards with real photos using ResponsiveRow (xs:12, sm:6, md:4)
  - _build_pricing(page): Centered pricing card with strikethrough old price, feature list, gold CTA button
API Calls: None (static content, all data from theme constants and i18n)
i18n Keys Used: hero.*, results.label, features.*, pricing.*, style.*, styles.title
Theme Constants: BG_PRIMARY, BG_SURFACE, BG_SURFACE_HIGH, PRIMARY, PRIMARY_CONTAINER, ON_PRIMARY,
                 TEXT_WHITE, TEXT_SECONDARY, TEXT_MUTED, BUTTON_PRIMARY_BG, BUTTON_TEXT,
                 FONT_HERO, FONT_H1, FONT_H2, FONT_H3, FONT_H4, FONT_BODY, FONT_BODY_LG,
                 FONT_CAPTION, FONT_SMALL, FONT_LABEL, RADIUS_PILL, RADIUS_MD, RADIUS_LG,
                 SPACE_*, MOBILE_MAX, MAX_WIDTH, CARD_PADDING, CONTENT_PADDING, MOBILE_PADDING,
                 SAMPLE_PHOTOS, STYLE_PHOTOS, STYLE_COLORS, STYLE_ICONS
Navigation: CTA buttons -> /create, pricing CTA -> /create
Dependencies: app.components.navbar (build_navbar), app.components.footer (build_footer),
              app.components.cookie_banner (build_cookie_banner), app.i18n (t), app.theme (T)
Responsive: is_mobile check (page_width < MOBILE_MAX), adjusts font sizes, padding, and layouts
Output: [navbar, hero, results_gallery, how_it_works, style_showcase, pricing, footer, cookie_banner]
```

---

### app/pages/login.py

```
Purpose: Authentication page with magic link email and Microsoft OAuth login
Build Function: build(page) -> list[ft.Control]
Features:
  - Email magic link: Text field + "Send Magic Link" button, calls API send_magic_link endpoint
  - Microsoft SSO: "Sign in with Microsoft" button, calls API get_microsoft_auth_url then launches URL
  - GDPR consent: Checkbox required before either login method
  - Success state: Shows "Check your email!" message after magic link sent
  - Error handling: Displays validation errors (invalid email) and API errors
  - Redirect: If user already authenticated (page.session.store.get("user")), auto-redirects to /create
API Calls:
  - POST /auth/magic-link (via api.send_magic_link)
  - GET /auth/microsoft/url (via api.get_microsoft_auth_url) -> launches auth_url in browser
i18n Keys Used: auth.title, auth.email_placeholder, auth.send_magic_link, auth.or,
                auth.microsoft_login, auth.check_email, auth.back_home, auth.gdpr_consent
Theme Constants: BG_PRIMARY, BG_SURFACE, PRIMARY, PRIMARY_CONTAINER, TEXT_WHITE, TEXT_SECONDARY,
                 BUTTON_PRIMARY_BG, BUTTON_TEXT, OUTLINE, RADIUS_SM, RADIUS_LG, BORDER,
                 FONT_H1, FONT_BODY, FONT_CAPTION, SPACE_*, MOBILE_MAX, MAX_WIDTH
Navigation: "Back to Home" -> /, successful auth -> /create
Dependencies: app.components.navbar, app.components.footer, app.components.cookie_banner,
              app.services.api_client (StudioFaceAPI), app.i18n (t), app.theme (T)
Validation: Email regex pattern (^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$)
Output: [navbar, main_content (centered login card), footer]
```

---

### app/pages/auth_callback.py

```
Purpose: Handles redirects from magic link emails and Microsoft OAuth callback
Build Function: build(page) -> list[ft.Control]
Features:
  - Parses URL query parameters: token (magic link), code + state (Microsoft OAuth)
  - Magic link flow: POST /auth/magic-link/verify with token
  - Microsoft OAuth flow: POST /auth/microsoft/callback with code + state
  - Shows "Verifying your identity..." spinner during verification
  - On success: stores tokens in session, shows success message, redirects to /create
  - On failure: shows error message with link to /login
URL Parameters:
  - ?token=<magic-link-token> — for magic link verification
  - ?code=<oauth-code>&state=<csrf-state> — for Microsoft OAuth callback
API Calls:
  - POST /auth/magic-link/verify (via auth_service.verify_and_store_token)
  - POST /auth/microsoft/callback (via auth_service.handle_microsoft_callback)
i18n Keys Used: auth.verifying, auth.verify_success, auth.verify_error, auth.back_home,
                auth.title
Theme Constants: BG_PRIMARY, BG_SURFACE, PRIMARY_CONTAINER, TEXT_WHITE, TEXT_SECONDARY,
                 FONT_H2, FONT_BODY, SPACE_*, RADIUS_LG, BORDER
Navigation: Success -> /create, Error -> /login link
Dependencies: app.services.api_client, app.services.auth_service, app.i18n (t), app.theme (T)
Token Storage: page.session.set("user", ...), page.session.set("sf_access_token", ...),
               page.session.set("sf_refresh_token", ...)
Output: list of controls (status display, no navbar/footer for clean callback UX)
```

---

### app/pages/create.py

```
Purpose: 3-step headshot creation wizard (Upload -> Style -> Attire/Pay)
Build Function: build(page) -> list[ft.Control]
Internal Functions:
  - _build_progress_tracker(current_step, lang): 3-step indicator with gold/green/grey states
  - Step 1 (Upload): File picker + camera capture, file validation, upload chip display
  - Step 2 (Style): 6 selectable style cards with real photos
  - Step 3 (Attire): Masculine/Feminine presentation selection + "Generate" button
Features:
  - File picker using Flet FilePicker (async pick_files via page.run_task)
  - Camera capture using flet-camera (optional, HAS_CAMERA flag for graceful degradation)
  - File validation: JPG/PNG only, max 10 MB each, 2-5 files required
  - Style selection: 6 styles (corporate, medical, banking, startup, casual, tech)
  - Presentation selection: masculine or feminine
  - Generation flow: upload files -> create generation -> create Stripe checkout -> redirect
  - Loading states: "Uploading your photos..." and "Generating your headshots..." spinners
API Calls:
  - POST /uploads/sessions (via upload_service.create_session_and_upload)
  - POST /uploads/ (via upload_service.create_session_and_upload, for each file)
  - POST /generations/ (via generation_service.create_generation)
  - POST /payments/checkout (via payment_service.start_checkout)
i18n Keys Used: create.*, style.*, common.continue, common.back
Theme Constants: BG_PRIMARY, BG_SURFACE, BG_SURFACE_HIGH, PRIMARY, PRIMARY_CONTAINER, ON_PRIMARY,
                 TEXT_WHITE, TEXT_SECONDARY, TEXT_MUTED, BUTTON_PRIMARY_BG, BUTTON_TEXT,
                 SUCCESS, OUTLINE_VARIANT, STYLE_COLORS, STYLE_ICONS, STYLE_PHOTOS,
                 FONT_*, SPACE_*, RADIUS_*, MOBILE_MAX, MAX_WIDTH
Navigation: Back -> /, Success -> Stripe checkout URL (external), Cancel -> /payment/cancel
Dependencies: app.components.navbar (build_navbar), app.services.upload_service,
              app.services.generation_service, app.services.payment_service,
              app.i18n (t), app.theme (T), flet_camera (optional)
State Management: current_step (0-2), selected_style, selected_presentation,
                  uploaded_files list, file_picker ref
Output: [navbar, progress_tracker, step_content (varies by current_step)]
```

---

### app/pages/gallery.py

```
Purpose: Display and download generated AI headshots
Build Function: build(page) -> list[ft.Control]
Internal Functions:
  - _build_gallery_footer(lang): Minimal dark footer with copyright and GDPR text
  - _build_status_badge(status, lang): Colored status chip (green/yellow/red)
Features:
  - Lists user's generation history from API
  - Each generation shows: status badge, created date, style label, headshot grid
  - Headshot cards with loading/error/loaded states
  - Individual download buttons per headshot
  - "Download All" button for batch downloading
  - Empty state: "No headshots yet. Create your first set!" with CTA
  - Polling for in-progress generations
API Calls:
  - GET /generations/ (via api.list_generations, paginated)
  - GET /generations/{id} (via api.get_generation, for status/images)
i18n Keys Used: gallery.*, footer.copyright, footer.gdpr, common.loading,
                error.generation_failed
Theme Constants: BG_PRIMARY, BG_SURFACE, BG_SURFACE_HIGH, PRIMARY, PRIMARY_CONTAINER,
                 TEXT_WHITE, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, ERROR,
                 FONT_*, SPACE_*, RADIUS_*, BORDER, DIVIDER, MOBILE_MAX
Navigation: "Create New Headshots" -> /create
Dependencies: app.components.navbar (build_navbar), app.i18n (t), app.theme (T)
Output: [navbar, main_content (generation list or empty state), gallery_footer]
```

---

### app/pages/payment_success.py

```
Purpose: Confirmation page after successful Stripe payment
Build Function: build(page) -> list[ft.Control]
Features:
  - Gold checkmark icon (CHECK_CIRCLE, 80px)
  - "Payment Confirmed!" title
  - "Your headshots are being generated" subtitle
  - Gold "View My Headshots" button -> /gallery
  - "You'll receive an email when they're ready" note
  - Centered dark card (500px width, responsive)
API Calls: None (static confirmation page)
i18n Keys Used: payment.success_title, payment.success_desc, payment.view_gallery,
                payment.email_note
Theme Constants: BG_PRIMARY, BG_SURFACE, PRIMARY_CONTAINER, TEXT_WHITE, TEXT_SECONDARY,
                 TEXT_MUTED, BUTTON_PRIMARY_BG, BUTTON_TEXT, FONT_H1, FONT_BODY, FONT_CAPTION,
                 SPACE_*, RADIUS_SM, RADIUS_LG, BORDER, CARD_PADDING, MOBILE_PADDING, MOBILE_MAX
Navigation: "View My Headshots" -> /gallery
Dependencies: app.components.navbar, app.components.footer, app.i18n (t), app.theme (T)
Output: [navbar, main_content (centered success card), footer]
```

---

### app/pages/payment_cancel.py

```
Purpose: Informational page when user cancels Stripe checkout
Build Function: build(page) -> list[ft.Control]
Features:
  - Grey cancel icon (CANCEL_OUTLINED, 80px)
  - "Payment Cancelled" title
  - "No charges were made. You can try again anytime." description
  - Gold "Retry" button with refresh icon -> /create
  - "Back to Home" text link -> /
  - Centered dark card (500px width, responsive)
API Calls: None (static informational page)
i18n Keys Used: payment.cancel_title, payment.cancel_desc, common.retry, auth.back_home
Theme Constants: BG_PRIMARY, BG_SURFACE, PRIMARY, TEXT_WHITE, TEXT_SECONDARY, TEXT_MUTED,
                 BUTTON_PRIMARY_BG, BUTTON_TEXT, FONT_H2, FONT_BODY, FONT_CAPTION,
                 SPACE_*, RADIUS_SM, RADIUS_LG, BORDER, CARD_PADDING, MOBILE_PADDING, MOBILE_MAX
Navigation: "Retry" -> /create, "Back to Home" -> /
Dependencies: app.components.navbar, app.components.footer, app.i18n (t), app.theme (T)
Output: [navbar, main_content (centered cancel card), footer]
```

---

### app/pages/not_found.py

```
Purpose: 404 error page for invalid routes
Build Function: build(page) -> list[ft.Control]
Features:
  - Giant "404" text (2.5x FONT_HERO on desktop, 1.8x on mobile) in TEXT_MUTED
  - "Page not found" heading
  - "The page you're looking for doesn't exist" subtitle
  - Gold "Go Home" button -> /
  - Centered content, expand to fill viewport
API Calls: None
i18n Keys Used: error.not_found, error.not_found_desc, error.go_home
Theme Constants: BG_PRIMARY, TEXT_WHITE, TEXT_SECONDARY, TEXT_MUTED, BUTTON_PRIMARY_BG,
                 BUTTON_TEXT, FONT_HERO, FONT_H2, FONT_BODY, SPACE_*, RADIUS_SM,
                 CONTENT_PADDING, MOBILE_PADDING, MOBILE_MAX
Navigation: "Go Home" -> /
Dependencies: app.components.navbar, app.components.footer, app.i18n (t), app.theme (T)
Output: [navbar, main_content (centered 404 display), footer]
```

---

## Components

---

### app/components/navbar.py

```
Purpose: Top navigation bar displayed on every page
Build Function: build_navbar(page) -> ft.Control
Features:
  - Logo: gold square container (32x32) + "STUDIOFACE" bold white text, clickable -> /
  - Gallery link: "My Headshots" text button (desktop only)
  - Language picker: dropdown component (build_language_picker)
  - User avatar: gold circle (36x36) with first letter of email, click toggles sign in/out
  - Mobile hamburger: PopupMenuButton with Home, Create, Gallery, divider, Sign In/Out
  - Active route highlighting: current page shown in gold in mobile menu
  - Two layouts: desktop_row (logo + [gallery, lang, avatar]) and mobile_row (logo + [lang, hamburger])
  - Layout switching: is_mobile = page_width < MOBILE_MAX (600px)
Session Reads: page.session.store.get("lang"), page.session.store.get("user")
i18n Keys Used: nav.home, nav.create, nav.gallery, nav.login, nav.logout
Theme Constants: BG_PRIMARY, PRIMARY, PRIMARY_CONTAINER, ON_PRIMARY, TEXT_WHITE,
                 TEXT_PRIMARY, TEXT_SECONDARY, FONT_BODY, FONT_CAPTION,
                 SPACE_SM, SPACE_MD, SPACE_XS, NAV_HEIGHT, MAX_WIDTH,
                 CONTENT_PADDING, MOBILE_PADDING, MOBILE_MAX
Navigation: Logo -> /, Gallery -> /gallery, Sign In -> /login, Sign Out -> / (clears session)
Dependencies: app.components.language_picker, app.i18n (t), app.theme (T)
Output: ft.Container (height=NAV_HEIGHT, centered, max_width=MAX_WIDTH)
```

---

### app/components/footer.py

```
Purpose: Bottom page footer with links and copyright
Build Function: build_footer(page) -> ft.Control
Features:
  - Logo section: small gold square (24x24) + "STUDIOFACE" in muted text
  - Product links column: "Product" header, Home, Create, My Headshots links
  - Legal links column: "Legal" header, Privacy Policy, Terms of Service links
  - Copyright bar: "2026 StudioFace, Made in Spain" left, "GDPR Compliant" right
  - Responsive: horizontal layout on desktop, stacked column on mobile
  - Top border divider line
Session Reads: page.session.store.get("lang")
i18n Keys Used: footer.product, footer.legal, footer.privacy, footer.terms,
                footer.copyright, footer.made_in, footer.gdpr, nav.home, nav.create, nav.gallery
Theme Constants: BG_SURFACE_LOW, PRIMARY_CONTAINER, TEXT_MUTED, TEXT_SECONDARY,
                 FONT_SMALL, FONT_CAPTION, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
                 SPACE_HERO, DIVIDER, MAX_WIDTH, CONTENT_PADDING, MOBILE_PADDING, MOBILE_MAX
Navigation: Home -> /, Create -> /create, Gallery -> /gallery, Privacy -> /privacy, Terms -> /terms
Dependencies: app.i18n (t), app.theme (T)
Output: ft.Container (dark background, top border, centered content)
```

---

### app/components/cookie_banner.py

```
Purpose: GDPR-compliant cookie consent bar
Build Function: build_cookie_banner(page, lang) -> ft.Control
Features:
  - Shows only if no consent choice has been made (session key: studioface_cookie_consent)
  - "We use cookies" title + description text
  - Gold "Accept All" elevated button
  - Outlined "Decline" button
  - On click: stores "accepted" or "declined" in session, hides banner
  - Uses ft.Ref to toggle visibility without full page re-render
  - Responsive: column layout on mobile, row with space-between on desktop
Session Keys: studioface_cookie_consent (read/write)
i18n Keys Used: cookies.title, cookies.desc, cookies.accept, cookies.decline
Theme Constants: BG_SURFACE_HIGH, TEXT_WHITE, TEXT_SECONDARY, BUTTON_PRIMARY_BG,
                 BUTTON_TEXT, OUTLINE, FONT_H4, FONT_CAPTION, SPACE_*, RADIUS_SM,
                 BORDER, MAX_WIDTH, CONTENT_PADDING, MOBILE_PADDING, MOBILE_MAX
Dependencies: app.i18n (t), app.theme (T)
Output: ft.Container (bottom banner, hidden if consent already given)
```

---

### app/components/style_card.py

```
Purpose: Selectable card for choosing a headshot style in the Create wizard
Build Function: build_style_card(style_key, lang, selected, on_click) -> ft.Control
Parameters:
  - style_key: str — one of "corporate", "medical", "banking", "startup", "casual", "tech"
  - lang: str — current language code
  - selected: bool — whether this card is currently selected
  - on_click: callable — click handler
Features:
  - Top band: real photo from T.STYLE_PHOTOS if available, colored band with icon as fallback
  - Selection state: gold border (3px, PRIMARY_CONTAINER) + checkmark badge when selected,
                     grey border (1px, BORDER) when unselected
  - Text content: style name (bold white) + description (secondary, max 2 lines with ellipsis)
  - Uses ft.Stack to overlay checkmark badge on top-right corner
  - Ink ripple effect on click
  - Fixed width: 200px
Icon Mapping: Maps string icon names from theme to ft.Icons enum values
i18n Keys Used: style.{style_key}, style.{style_key}.desc
Theme Constants: STYLE_COLORS, STYLE_ICONS, STYLE_PHOTOS, PRIMARY, PRIMARY_CONTAINER,
                 BG_SURFACE, BORDER, TEXT_WHITE, TEXT_SECONDARY,
                 FONT_H4, FONT_CAPTION, SPACE_XS, SPACE_MD, RADIUS_MD
Dependencies: app.i18n (t), app.theme (T)
Output: ft.Container (200px wide, dark card with photo/icon top + text bottom)
```

---

### app/components/language_picker.py

```
Purpose: Dropdown to switch between EN/ES/DE
Build Function: build_language_picker(page) -> ft.Control
Features:
  - Dropdown with 3 options: English, Espanol, Deutsch (with flag emojis)
  - On selection: stores new language in session, re-navigates to current route to force re-render
  - Dark styled: BG_SURFACE background, OUTLINE border, PRIMARY focus border
  - Dimensions: 160px wide, 42px tall
Session Keys: lang (read/write)
i18n Keys Used: None (uses LANGUAGES dict from app.i18n directly)
Theme Constants: BG_SURFACE, OUTLINE, PRIMARY, TEXT_PRIMARY,
                 FONT_CAPTION, SPACE_SM, SPACE_XS, RADIUS_SM
Dependencies: app.i18n (LANGUAGES), app.theme (T)
Output: ft.Dropdown
```

---

### app/components/progress_tracker.py

```
Purpose: Horizontal step indicator for the 3-step Create wizard
Build Function: build_progress_tracker(current_step, steps) -> ft.Control
Parameters:
  - current_step: int — 0-indexed current step number
  - steps: list[str] — list of step label strings
Features:
  - Completed steps: green circle (SUCCESS bg) with white checkmark icon, green connecting line
  - Current step: gold circle (PRIMARY_CONTAINER bg) with step number, white label
  - Future steps: dark grey circle (BG_SURFACE_HIGH bg) with muted number, muted label, outlined border
  - Connecting lines between circles: 40px wide, 2px tall, colored based on completion
  - Labels below circles: 80px wide, centered text
  - Circle dimensions: 36x36px
Theme Constants: SUCCESS, PRIMARY_CONTAINER, BG_SURFACE_HIGH, ON_PRIMARY, TEXT_WHITE,
                 TEXT_MUTED, OUTLINE_VARIANT, FONT_CAPTION, FONT_SMALL, SPACE_XS, SPACE_SM,
                 SPACE_MD, SPACE_LG
Dependencies: app.theme (T)
Output: ft.Container wrapping a centered ft.Row
```

---

### app/components/loading_spinner.py

```
Purpose: Gold loading spinner with optional message
Build Function: build_loading_spinner(message="") -> ft.Control
Parameters:
  - message: str — optional text displayed below the spinner
Features:
  - Gold ProgressRing (48x48px, 3px stroke, PRIMARY_CONTAINER color)
  - Optional message text in TEXT_SECONDARY
  - Centered in a full-height container with BG_PRIMARY background
  - Large padding (SPACE_XXL = 48px)
Theme Constants: PRIMARY_CONTAINER, TEXT_SECONDARY, BG_PRIMARY,
                 FONT_BODY, SPACE_MD, SPACE_XXL
Dependencies: app.theme (T)
Output: ft.Container (expand=True, centered column)
```

---

### app/components/headshot_card.py

```
Purpose: Display card for generated headshots in the Gallery
Build Function: build_headshot_card(image_url, variant_label, on_download, loading, error, lang) -> ft.Control
Parameters:
  - image_url: str | None — URL of the generated headshot image
  - variant_label: str — label text below the image (e.g., "Variant 1")
  - on_download: callable — download button click handler
  - loading: bool — show loading spinner instead of image
  - error: bool — show error state instead of image
  - lang: str — current language code
Features:
  - Three states: loading (gold spinner + "Loading..."), error (red icon + error text), loaded (image)
  - Image: 240x280px, COVER fit, rounded corners
  - Variant label in secondary text
  - Outlined "Download" button with download icon (hidden during loading/error)
  - Card width: 240px + padding
i18n Keys Used: gallery.download, common.loading, error.generation_failed
Theme Constants: BG_SURFACE_HIGH, PRIMARY, PRIMARY_CONTAINER, TEXT_SECONDARY, ERROR,
                 FONT_CAPTION, SPACE_SM, SPACE_MD, RADIUS_SM, RADIUS_MD, OUTLINE
Dependencies: app.i18n (t), app.theme (T)
Output: ft.Container (column with image area + label + download button)
```

---

### app/components/upload_zone.py

```
Purpose: File upload area for Step 1 of the Create wizard
Build Function: build_upload_zone(page, file_picker, uploaded_files, on_remove_file, lang, on_files_picked) -> ft.Control
Parameters:
  - page: ft.Page — Flet page reference
  - file_picker: ft.FilePicker — pre-created file picker instance
  - uploaded_files: list — list of uploaded file objects/dicts
  - on_remove_file: callable — callback when removing a file chip (receives index)
  - lang: str — current language code
  - on_files_picked: callable | None — callback when files are picked (receives result list)
Features:
  - Dashed-border container (OUTLINE color, RADIUS_MD corners)
  - Camera icon (48px, muted) + title + description text
  - Gold "Choose Photos" button that triggers async file picker
  - File picker: allows JPG/JPEG/PNG, multiple selection, async via page.run_task
  - File chips: removable Chip components showing filename for each uploaded file
  - Upload count text in gold (e.g., "3 photo(s) uploaded")
  - Entire zone is clickable (triggers file picker)
  - Ink ripple effect
i18n Keys Used: create.upload_title, create.upload_desc, create.upload_button, create.uploaded_count
Theme Constants: BG_SURFACE, BG_SURFACE_HIGH, TEXT_WHITE, TEXT_SECONDARY, TEXT_MUTED,
                 TEXT_PRIMARY, PRIMARY, BUTTON_PRIMARY_BG, BUTTON_TEXT, OUTLINE,
                 FONT_H4, FONT_CAPTION, FONT_SMALL, SPACE_SM, SPACE_XL, RADIUS_SM, RADIUS_MD
Dependencies: app.i18n (t), app.theme (T)
Output: ft.Container (dark bordered upload area with file chips)
```

---

## Services

---

### app/services/api_client.py

```
Purpose: Async HTTP client wrapping all StudioFace backend API endpoints
Class: StudioFaceAPI
Initialization: StudioFaceAPI(base_url: str)
HTTP Client: httpx.AsyncClient with 30-second timeout
Features:
  - Automatic retry on 502/503/504 (up to 3 attempts with backoff)
  - Automatic token refresh on 401 (calls /auth/refresh, retries original request)
  - Token callback: notifies registered callback when tokens are refreshed
  - Consistent error normalization: handles FastAPI detail strings, validation lists, and custom error objects
  - Bearer token authentication via Authorization header
Endpoints:
  - Health: GET /health/
  - Auth: POST /auth/magic-link, POST /auth/magic-link/verify, GET /auth/microsoft/url,
          POST /auth/microsoft/callback, GET /auth/me, PUT /auth/gdpr-consent,
          POST /auth/refresh, POST /auth/logout
  - Uploads: POST /uploads/sessions, POST /uploads/ (multipart)
  - Generations: POST /generations/, GET /generations/{id}, GET /generations/
  - Payments: POST /payments/checkout, GET /payments/
  - Settings: PUT /users/me/locale, POST /users/me/export, DELETE /users/me
Constants: MAX_RETRIES=3, RETRY_CODES={502,503,504}, RETRY_DELAY=1.0
Dependencies: httpx, asyncio, logging
```

---

### app/services/auth_service.py

```
Purpose: Authentication flows and token management
Functions:
  - login_with_magic_link(api, email, locale): Request magic link email
  - login_with_microsoft(api): Get Microsoft OAuth URL
  - handle_microsoft_callback(api, page, code, state): Exchange OAuth code for tokens, store in session
  - verify_and_store_token(api, page, token): Verify magic link token, store in session
  - restore_session(api, page): Try to restore session from stored tokens (validates with /auth/me)
  - logout(api, page): Invalidate tokens on server, clear local session
Internal: _store_auth_result(api, page, result): Stores tokens in api client and page session,
          registers auto-refresh callback
Session Keys: sf_access_token, sf_refresh_token, user
Dependencies: app.services.api_client (StudioFaceAPI), flet (ft.Page)
```

---

### app/services/upload_service.py

```
Purpose: File validation and upload handling
Functions:
  - validate_file(filename, size): Check file extension (.jpg/.jpeg/.png) and size (<10MB)
  - validate_file_count(count): Check count (2-5 files)
  - create_session_and_upload(api, files): Create upload session + upload all files sequentially
Constants: ALLOWED_EXTENSIONS={.jpg, .jpeg, .png}, MAX_FILE_SIZE=10MB, MIN_FILES=2, MAX_FILES=5
Returns: {session_id, upload_ids, uploaded} or {error, code, status}
Dependencies: app.services.api_client (StudioFaceAPI)
```

---

### app/services/generation_service.py

```
Purpose: Headshot generation and polling
Functions:
  - create_generation(api, style, upload_ids, presentation, upload_session_id): Create generation job
  - poll_generation(api, generation_id, on_update): Poll every 5 seconds until completed/failed/timeout
  - get_images(api, generation_id): Fetch generation details with image URLs
Constants: POLL_INTERVAL=5 seconds, MAX_POLL_ATTEMPTS=120 (10 minutes max)
Status Values: pending, processing, completed/complete/done, failed/error
Dependencies: app.services.api_client (StudioFaceAPI), asyncio
```

---

### app/services/payment_service.py

```
Purpose: Stripe checkout session creation and redirect
Functions:
  - start_checkout(api, page, generation_id, currency="EUR"):
    Creates Stripe checkout session via API, launches checkout URL in browser
Returns: {success, url} or {error, code, status}
Dependencies: app.services.api_client (StudioFaceAPI), flet (ft.Page)
```

---

## Core Modules

---

### app/main.py

```
Purpose: Application entry point and router
Function: main(page) — sync, sets up page and routing
Features:
  - Page setup: title, padding, spacing, bgcolor, theme_mode, scroll
  - API client initialization: reads STUDIOFACE_API_URL env var, stores in session
  - Default language: "en" (stored in session)
  - Router: navigate(route) clears page.controls, imports and builds the matching page module
  - Route matching: strips query params, matches against /, /login, /auth/callback, /create,
                    /gallery, /payment/success, /payment/cancel, fallback to 404
  - Route change handler: on_route_change calls navigate with page.route
  - Initial navigation: navigate("/")
Entry: ft.app(target=main)
Environment: STUDIOFACE_API_URL (default: https://api.studioface.app/api/v1)
```

---

### app/theme.py

```
Purpose: Design system constants for the entire application
Class: StudioFaceTheme (aliased as T throughout the codebase)
Categories:
  - Backgrounds: BG_PRIMARY (#131314), BG_SURFACE (#1C1B1C), BG_SURFACE_HIGH (#2A2A2B),
                  BG_SURFACE_HIGHEST (#353436), BG_SURFACE_LOW (#0E0E0F)
  - Primary colors: PRIMARY (#FFC174), PRIMARY_BRIGHT (#FFB95F), PRIMARY_CONTAINER (#F59E0B),
                     PRIMARY_DARK (#855300), ON_PRIMARY (#472A00)
  - Text: TEXT_PRIMARY (#E5E2E3), TEXT_WHITE (#FFFFFF), TEXT_SECONDARY (#A0A0A0),
          TEXT_MUTED (#6B6B6B), TEXT_DISABLED (#555555)
  - Borders: BORDER (#2A2A2B), BORDER_LIGHT (#3A393A), DIVIDER (#1F1F20),
             OUTLINE (#3A393A), OUTLINE_VARIANT (#2A2A2B)
  - Buttons: BUTTON_PRIMARY_BG (#F59E0B), BUTTON_TEXT (#472A00), BUTTON_OUTLINE (#3A393A)
  - Spacing: 4px grid system (4, 8, 16, 24, 32, 48, 64, 96)
  - Border radius: 8, 12, 16, 24, 100 (pill)
  - Typography: 56, 40, 32, 24, 20, 18, 16, 14, 12, 11
  - Layout: MAX_WIDTH=1200, NAV_HEIGHT=64, MOBILE_MAX=600, TABLET_MAX=1024
  - Style colors: per-style brand colors (corporate=#1E40AF, medical=#0891B2, etc.)
  - Style icons: per-style Material icon names
  - Sample photos: 5 customer headshot URLs for the results gallery
  - Style photos: 6 style example headshot URLs for style cards
```

---

### app/i18n.py

```
Purpose: Internationalization with 3 languages
Constants:
  - TRANSLATIONS: dict[str, dict[str, str]] — nested dict with 3 top-level keys (en, es, de),
    each containing 103+ key-value pairs
  - LANGUAGES: dict with display name and flag emoji for each language code
Function: t(key, lang="en", **kwargs) -> str
  - Looks up key in requested language
  - Falls back to English if key missing in requested language
  - Returns key itself if not found in any language
  - Supports variable interpolation via str.format(**kwargs)
Translation Categories: hero.*, results.*, styles.*, features.*, pricing.*, style.*,
                         auth.*, create.*, gallery.*, payment.*, nav.*, footer.*,
                         cookies.*, error.*, common.*
```
