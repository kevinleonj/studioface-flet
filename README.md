# StudioFace — AI Headshot Generator (Flet Frontend)

Professional AI-powered headshot generator built with [Flet](https://flet.dev) (Python). Upload a few selfies, choose a style, and receive four studio-quality headshots in minutes. Developed as part of the **MCSBT (Master in Computer Science and Business Technology)** program at **IE University, Madrid, Spain**.

## Architecture

```
                         StudioFace System
  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │   ┌──────────┐     ┌─────────────┐     ┌────────────────┐   │
  │   │          │     │             │     │                │   │
  │   │ Browser  │────▶│  Flet App   │────▶│ StudioFace API │   │
  │   │          │◀────│  (Python)   │◀────│  (FastAPI)     │   │
  │   └──────────┘     └─────────────┘     └───────┬────────┘   │
  │                          │                     │            │
  │                     Flet WebSocket         REST/JSON        │
  │                                                │            │
  │                                    ┌───────────┼──────────┐ │
  │                                    │      Azure Cloud     │ │
  │                                    │                      │ │
  │                                    │  ┌──────────────┐    │ │
  │                                    │  │ Azure SQL DB │    │ │
  │                                    │  └──────────────┘    │ │
  │                                    │                      │ │
  │                                    │  ┌──────────────┐    │ │
  │                                    │  │ Blob Storage │    │ │
  │                                    │  └──────────────┘    │ │
  │                                    │                      │ │
  │                                    │  ┌──────────────┐    │ │
  │                                    │  │  Azure AI    │    │ │
  │                                    │  └──────────────┘    │ │
  │                                    │                      │ │
  │                                    └──────────────────────┘ │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

## Features

- **AI Headshot Generation** — Upload 2-5 selfies, receive 4 studio-quality headshots
- **6 Professional Styles** — Corporate, Medical, Banking, Startup, Casual, Tech
- **Internationalization (i18n)** — Full support for English, Spanish, and German
- **Responsive Design** — Mobile-first layout with Material Design 3 theme
- **Async API Communication** — Non-blocking HTTP calls via `httpx` with retry logic
- **Dual Authentication** — Magic link email + Microsoft OAuth sign-in
- **Stripe Payments** — Secure checkout integration at EUR 6.99 per generation
- **GDPR Compliant** — Cookie consent banner, privacy-first data handling
- **Session Persistence** — Token stored in client storage, auto-restored on reload

## Screenshots

> Screenshots will be added after the first production deployment.

## Prerequisites

- **Python** 3.12+
- **Flet** 0.25+
- A running instance of the StudioFace backend API (or access to `https://api.studioface.app`)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-org/studioface-flet.git
cd studioface-flet
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Run the app

**Desktop mode (default):**

```bash
flet run app/main.py
```

**Web mode:**

```bash
flet run --web app/main.py
```

### Docker

```bash
docker compose up --build
```

The app will be available at `http://localhost:8080`.

## Testing

### Unit tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v --tb=short
```

### E2E tests (Playwright)

```bash
playwright install
python -m pytest tests/e2e/ -v
```

## Project Structure

```
studioface-flet/
├── app/
│   ├── assets/                  # Static assets (images, icons)
│   ├── components/              # Reusable UI components
│   │   ├── cookie_banner.py     # GDPR cookie consent banner
│   │   ├── footer.py            # Page footer with links
│   │   ├── headshot_card.py     # Generated headshot display card
│   │   ├── language_picker.py   # EN/ES/DE language switcher
│   │   ├── loading_spinner.py   # Loading state indicator
│   │   ├── navbar.py            # Top navigation bar
│   │   ├── progress_tracker.py  # Multi-step progress indicator
│   │   ├── style_card.py        # Headshot style selection card
│   │   └── upload_zone.py       # Drag-and-drop file upload area
│   ├── pages/                   # Route-level page views
│   │   ├── create.py            # Upload → Style → Generate wizard
│   │   ├── gallery.py           # View and download headshots
│   │   ├── landing.py           # Marketing landing page
│   │   ├── login.py             # Authentication page
│   │   ├── not_found.py         # 404 error page
│   │   └── payment_success.py   # Post-checkout confirmation
│   ├── services/                # Backend API integration
│   │   ├── api_client.py        # Core HTTP client with retries
│   │   ├── auth_service.py      # Auth flows (magic link, OAuth)
│   │   ├── generation_service.py# Generation creation and polling
│   │   ├── payment_service.py   # Stripe checkout integration
│   │   └── upload_service.py    # File validation and upload
│   ├── i18n.py                  # Translation strings (EN/ES/DE)
│   ├── main.py                  # Application entry point and router
│   ├── state.py                 # Global state management
│   └── theme.py                 # Material Design 3 theme constants
├── docs/                        # Documentation
│   ├── API_MAP.md               # Backend API endpoint reference
│   └── ARCHITECTURE.md          # System architecture document
├── scripts/                     # Development scripts
│   ├── run_dev.sh               # Start dev server
│   └── run_tests.sh             # Run test suite
├── tests/                       # Test suite
│   ├── e2e/                     # End-to-end tests (Playwright)
│   └── test_i18n.py             # i18n unit tests
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Container build instructions
├── requirements.txt             # Production dependencies
└── requirements-dev.txt         # Development/test dependencies
```

## Tech Stack

| Layer          | Technology         | Purpose                              |
|----------------|--------------------|--------------------------------------|
| UI Framework   | Flet 0.25+         | Cross-platform Python UI (Flutter)   |
| Language       | Python 3.12        | Application logic                    |
| HTTP Client    | httpx              | Async API calls with retry support   |
| Image Handling | Pillow             | Client-side image validation         |
| Config         | python-dotenv      | Environment variable management      |
| Styling        | Material Design 3  | Theme, colors, typography, spacing   |
| Testing        | pytest             | Unit and integration tests           |
| E2E Testing    | Playwright         | Browser automation tests             |
| Container      | Docker             | Deployment packaging                 |

## Pages

| Route              | Page              | Description                                                    |
|--------------------|-------------------|----------------------------------------------------------------|
| `/`                | Landing           | Hero section, feature overview, pricing, CTA                   |
| `/login`           | Login             | Magic link email input + Microsoft OAuth button                |
| `/create`          | Create            | 3-step wizard: upload selfies, pick style, select attire       |
| `/gallery`         | Gallery           | Grid of generated headshots with download buttons              |
| `/payment/success` | Payment Success   | Post-Stripe confirmation with link to gallery                  |
| `*`                | Not Found         | 404 page with navigation back to home                          |

## Internationalization (i18n)

The app ships with complete translations for three languages:

| Code | Language | Coverage |
|------|----------|----------|
| `en` | English  | 80+ keys |
| `es` | Spanish  | 80+ keys |
| `de` | German   | 80+ keys |

All UI text is routed through the `t(key, lang)` function in `app/i18n.py`. The language can be switched at runtime via the language picker component in the navbar. Translations fall back to English if a key is missing in the selected language.

## API

The frontend communicates with the StudioFace backend API hosted at:

```
https://api.studioface.app/api/v1
```

This can be overridden via the `STUDIOFACE_API_URL` environment variable.

See [`docs/API_MAP.md`](docs/API_MAP.md) for the full endpoint reference.

## Environment Variables

| Variable                 | Required | Default                                    | Description                    |
|--------------------------|----------|--------------------------------------------|--------------------------------|
| `STUDIOFACE_API_URL`     | No       | `https://api.studioface.app/api/v1`        | Backend API base URL           |
| `STRIPE_PUBLISHABLE_KEY` | No       | —                                          | Stripe public key (if needed)  |
| `APP_ENV`                | No       | `development`                              | Environment identifier         |

## License

MIT

## Credits

Built as part of the **Master in Computer Science and Business Technology (MCSBT)** program at **IE University, Madrid, Spain**.
