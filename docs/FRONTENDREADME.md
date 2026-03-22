# StudioFace Flet Frontend

**Professional AI Headshot Generator — Frontend Application**

MCSBT @ IE University Madrid | 2026

---

## 1. Project Overview

### What is StudioFace?

StudioFace is a web application that generates professional AI headshots from selfies. Users upload 2-5 photos, choose a professional style (Corporate, Medical, Banking, Startup, Casual, or Tech), and receive 4 studio-quality AI-generated headshots in minutes. The service costs EUR 6.99 per generation and is designed for job seekers, professionals, and anyone needing a polished headshot without visiting a photography studio.

### What does this frontend do?

This repository contains the **user-facing frontend application** built with Flet. It provides the complete user interface: a marketing landing page, authentication flows, a 3-step headshot creation wizard, a gallery to view and download results, and payment processing through Stripe. The frontend communicates with a separate backend API server that handles AI generation, file storage, and payment processing.

### Why Flet?

| Framework | Language | Pros | Cons | Verdict |
|-----------|----------|------|------|---------|
| **Flet** | Python | Python-only, Flutter rendering engine, Material Design, web + mobile + desktop from one codebase, rapid prototyping | Smaller community, fewer UI libraries | **Chosen** |
| React | JavaScript/TypeScript | Massive ecosystem, industry standard | Requires JavaScript expertise, separate mobile app needed | Too much JS for a Python-centric team |
| Flutter | Dart | Beautiful UIs, cross-platform | Requires learning Dart, separate language from backend | Dart learning curve too steep |
| Streamlit | Python | Very fast prototyping, Python-only | Limited UI customization, not SPA-like, no routing | Too limited for a multi-page app |
| Gradio | Python | Great for AI demos, Python-only | Designed for ML model demos, not full applications | Too AI-demo-focused |
| Django Templates | Python | Mature, well-documented | Server-rendered HTML, not SPA-like, requires HTML/CSS/JS | Templates feel dated for this use case |

**Flet was chosen because it allows the entire team to write Python exclusively** while producing a modern, Material Design application that runs in the browser. Flet compiles Python UI code into a Flutter web application, giving us a Single Page Application (SPA) experience without writing any JavaScript, HTML, or CSS.

---

## 2. Architecture Overview

```
Browser (User)
    |
    v
Flet Server (Python) --- renders Flutter/Material UI in the browser
    |
    v
Backend API (api.studioface.app/api/v1) --- FastAPI server
    |
    v
Google AI (Imagen) --- generates headshots
Stripe --- handles payments
Microsoft Entra --- handles OAuth login
```

**How it works:**

1. The user opens the StudioFace website in their browser
2. The Flet server runs Python code that builds a Flutter-based UI and sends it to the browser as a canvas application
3. When the user interacts with the app (clicks buttons, uploads photos, etc.), events are sent back to the Flet server
4. The Flet server makes async HTTP requests to the backend API using the httpx library
5. The backend API handles authentication, file uploads, AI generation (via Google Imagen), and payments (via Stripe)
6. Results flow back through the same chain to update the UI in real time

**Key architectural decisions:**
- **Server-side rendering**: All UI logic runs on the server in Python. The browser only renders the final Flutter canvas. This means no JavaScript runs in the browser for app logic.
- **Stateful sessions**: User state (language preference, authentication tokens, upload progress) is stored in Flet's session store on the server.
- **Async API calls**: All backend communication is asynchronous, keeping the UI responsive while waiting for API responses.
- **Page-based routing**: Navigation uses Flet's page.controls pattern, where each route clears the page and loads a new set of controls.

---

## 3. Page Descriptions

### Landing Page (`/`)

The marketing homepage that visitors see first. Designed with a dark premium aesthetic to convey professionalism and trust.

- **Hero Section**: Large headline "Your Professional AI Photo for Resume" with a gold-accented keyword, the EUR 6.99 price, a subtitle explaining the service, a prominent gold call-to-action button, and a trust bar showing "GDPR Compliant, Powered by Google AI, Secure Payments"
- **Results Gallery**: A horizontal row of 5 sample headshots from real customers (Miguel, Juan, Filippo, Maggie, Anita) to demonstrate quality
- **How It Works**: Three numbered cards explaining the 3-step process: (1) Upload Selfies, (2) Choose Your Style, (3) Get Your Headshots
- **Style Showcase**: Six visual cards showing each available style with real example photos: Corporate, Medical, Banking, Startup, Casual, Tech
- **Pricing Section**: A centered pricing card showing the crossed-out original price (EUR 24.99), the current price (EUR 6.99) with 4 feature checkmarks, and a gold "Buy Now" button
- **Cookie Banner**: GDPR-compliant consent bar at the bottom

### Login Page (`/login`)

The authentication page where users sign in before creating headshots.

- **Magic Link Login**: Users enter their email address and receive a one-time login link via email. No password is required.
- **Microsoft SSO**: A "Sign in with Microsoft" button that redirects to Microsoft's OAuth login page. This supports university and workplace Microsoft accounts.
- **GDPR Consent**: A checkbox requiring users to agree to data processing in accordance with the GDPR Privacy Policy before proceeding.
- **Redirect Logic**: If a user is already authenticated, they are automatically redirected to the Create page.

### Auth Callback Page (`/auth/callback`)

A technical page that users see briefly during the login process. It handles the redirect back from email magic links and Microsoft OAuth.

- Parses the authentication token or authorization code from the URL
- Displays a "Verifying your identity..." spinner while contacting the backend
- On success, stores authentication tokens and redirects to the Create page
- On failure, shows an error message with a link back to the login page

### Create Page (`/create`)

The core feature page: a 3-step wizard for creating AI headshots.

- **Step 1 - Upload Photos**: Users upload 2-5 selfie photos (JPG or PNG, max 10 MB each) using a file picker, OR take photos directly with their device camera using the webcam integration. Uploaded files appear as removable chips showing filenames and count.
- **Step 2 - Choose Style**: Users select one of 6 professional styles (Corporate, Medical, Banking, Startup, Casual, Tech) from visual cards showing example photos. Each card displays the style name, a description, and a sample headshot.
- **Step 3 - Choose Attire**: Users select masculine or feminine presentation for the generated headshot's clothing style.
- **Payment and Generation**: After completing all steps, users click "Generate Headshots - EUR 6.99" which creates a Stripe checkout session and redirects to Stripe's payment page. A progress tracker at the top shows which step the user is on (gold active circle, green completed circles, grey future circles connected by lines).

### Gallery Page (`/gallery`)

Where users view and download their generated headshots after payment.

- Displays headshot cards in a grid layout, each showing the generated image, style label, and a download button
- Shows generation status with colored badges: green for completed, yellow for processing, red for failed
- Includes a "Download All" button for batch downloading
- Shows creation date and style label for each generation
- Provides a "Create New Headshots" button to start a new session
- Displays an empty state message if the user has no generations yet

### Payment Success Page (`/payment/success`)

A confirmation page shown after successful Stripe payment.

- Large gold checkmark icon
- "Payment Confirmed!" heading
- "Your headshots are being generated" subtitle
- Gold "View My Headshots" button linking to the Gallery
- Note: "You'll receive an email when they're ready"

### Payment Cancel Page (`/payment/cancel`)

Shown when a user cancels or abandons the Stripe checkout process.

- Cancel icon in muted grey
- "Payment Cancelled" heading
- Reassuring message: "No charges were made. You can try again anytime."
- Gold "Retry" button linking back to the Create page
- Text link to return to the homepage

### 404 Not Found Page

A friendly error page for invalid URLs.

- Very large "404" text in muted grey
- "Page not found" heading
- "The page you're looking for doesn't exist" subtitle
- Gold "Go Home" button

---

## 4. Component Descriptions

### Navbar (`app/components/navbar.py`)

The top navigation bar displayed on every page.

- **Logo**: Gold square icon + "STUDIOFACE" in bold white text, links to homepage
- **Navigation Links**: "My Headshots" link to the gallery (desktop)
- **Language Picker**: Dropdown to switch between English, Spanish, and German
- **User Avatar**: Gold circle with the first letter of the user's email. Click to sign in (if not authenticated) or sign out (if authenticated)
- **Mobile Menu**: On small screens, the navigation links collapse into a hamburger menu with a popup containing Home, Create, Gallery, and Sign In/Out options
- **Active State**: Current page is highlighted in gold in the mobile menu

### Footer (`app/components/footer.py`)

The bottom section displayed on most pages.

- **Logo**: Smaller version of the StudioFace logo in muted colors
- **Product Links**: Home, Create, My Headshots
- **Legal Links**: Privacy Policy, Terms of Service
- **Copyright Bar**: "2026 StudioFace, Made in Spain" on the left, "GDPR Compliant" on the right
- **Responsive**: Stacks vertically on mobile, horizontal layout on desktop

### Cookie Banner (`app/components/cookie_banner.py`)

A GDPR-compliant consent bar shown at the bottom of the landing page.

- Title: "We use cookies"
- Description: "We use cookies to improve your experience and for analytics"
- Two buttons: gold "Accept All" and outlined "Decline"
- Remembers the user's choice in the session store and hides after selection
- Responsive: buttons below text on mobile, side-by-side on desktop

### Style Card (`app/components/style_card.py`)

A visual card used in the Create wizard for selecting a headshot style.

- Shows a real example headshot photo at the top (or a colored band with an icon as fallback)
- Style name in bold white text
- Short description in muted text
- Gold border and checkmark badge when selected, subtle grey border when unselected
- Clickable with ink ripple effect
- Fixed width of 200px

### Language Picker (`app/components/language_picker.py`)

A dropdown selector for switching the application language.

- Three options with flag emojis: English, Espanol, Deutsch
- Dark-themed dropdown matching the app's design system
- On selection, stores the new language in session and re-renders the current page
- Width: 160px, styled with dark background and gold focus border

### Progress Tracker (`app/components/progress_tracker.py`)

A horizontal step indicator used in the Create wizard.

- Displays numbered circles connected by lines
- **Completed steps**: Green circle with white checkmark, green connecting line
- **Current step**: Gold circle with step number, white label text
- **Future steps**: Dark grey circle with muted number, muted label text
- Labels below each circle show the step name (e.g., "Upload", "Style", "Attire")

### Loading Spinner (`app/components/loading_spinner.py`)

A centered loading indicator for async operations.

- Gold progress ring (48px, 3px stroke)
- Optional message text below the spinner in secondary color
- Centered in a full-height dark container
- Used during API calls, file uploads, and generation polling

### Headshot Card (`app/components/headshot_card.py`)

A display card for generated headshots in the Gallery.

- Three states: loading (spinner), error (red error icon), loaded (image)
- Image displayed at 240x280px with rounded corners
- Variant label below the image
- Outlined "Download" button with download icon
- Download button hidden during loading and error states

### Upload Zone (`app/components/upload_zone.py`)

A file upload area used in Step 1 of the Create wizard.

- Dashed border container with camera icon, title, and description
- Gold "Choose Photos" button that triggers the file picker
- Displays uploaded files as removable chips with filename text
- Shows upload count in gold text (e.g., "3 photo(s) uploaded")
- Accepts JPG and PNG files via Flet's FilePicker
- Entire zone is clickable to trigger the file picker

---

## 5. Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Flet** | >= 0.25.0 | UI framework (Python to Flutter/Material Design) |
| **httpx** | >= 0.27.0 | Async HTTP client for API communication |
| **flet-camera** | >= 0.81.0 | Webcam capture for taking selfies in-browser |
| **Pillow** | >= 10.0.0 | Image processing and validation |
| **python-dotenv** | >= 1.0.0 | Environment variable management |
| **Python** | 3.12+ | Runtime |

---

## 6. Design System

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `BG_PRIMARY` | `#131314` | Main page background (near-black) |
| `BG_SURFACE` | `#1C1B1C` | Card backgrounds |
| `BG_SURFACE_HIGH` | `#2A2A2B` | Elevated surfaces, cookie banner |
| `BG_SURFACE_LOW` | `#0E0E0F` | Footer background |
| `PRIMARY` | `#FFC174` | Gold text accents |
| `PRIMARY_CONTAINER` | `#F59E0B` | Gold buttons, badges, avatar circles |
| `TEXT_WHITE` | `#FFFFFF` | Headings, primary text |
| `TEXT_SECONDARY` | `#A0A0A0` | Subtitles, descriptions |
| `TEXT_MUTED` | `#6B6B6B` | Captions, disabled elements |
| `SUCCESS` | `#22C55E` | Completed status, checkmarks |
| `ERROR` | `#EF4444` | Error states, failed status |

### Typography

| Token | Size | Usage |
|-------|------|-------|
| `FONT_HERO` | 56px | Landing page main headline |
| `FONT_H1` | 40px | Section headings |
| `FONT_H2` | 32px | Sub-section headings |
| `FONT_H3` | 24px | Card headings |
| `FONT_H4` | 20px | Minor headings |
| `FONT_BODY` | 16px | Body text, buttons |
| `FONT_CAPTION` | 14px | Captions, small labels |
| `FONT_SMALL` | 12px | Fine print, footer text |

### Layout

- **Max Width**: 1200px (content centered within this boundary)
- **Nav Height**: 64px
- **Border Radius**: 8px (small), 12px (medium), 16px (large), 100px (pill buttons)
- **Spacing Grid**: 4px base unit (4, 8, 16, 24, 32, 48, 64, 96)
- **Breakpoints**: Mobile < 600px, Tablet < 1024px, Desktop >= 1024px
- **Mobile Padding**: 16px, Desktop Padding: 24px

---

## 7. Internationalization (i18n)

The application supports three languages, with all user-facing text fully translatable:

| Language | Code | Coverage |
|----------|------|----------|
| English | `en` | 103+ translation keys |
| Spanish (Espanol) | `es` | 103+ translation keys |
| German (Deutsch) | `de` | 103+ translation keys |

**How it works:**
- All text strings are stored in `app/i18n.py` as a nested Python dictionary
- The `t(key, lang)` function retrieves the correct translation for the current language
- If a key is missing in the selected language, it falls back to English
- If the key does not exist in any language, the key itself is returned (useful for debugging)
- Variable interpolation is supported: `t("create.uploaded_count", lang, count=3)` produces "3 photo(s) uploaded"
- The user's language preference is stored in the session and persists across page navigations

**Translation categories:**
- Hero section text, results gallery labels
- Feature descriptions, pricing copy
- Style names and descriptions (6 styles)
- Authentication prompts and status messages
- Create wizard labels and validation messages
- Gallery status labels and download buttons
- Payment confirmation and cancellation messages
- Navigation links, footer text, cookie banner
- Error messages and common UI labels

---

## 8. Security and Compliance

### GDPR Compliance
- Cookie consent banner with Accept/Decline options
- Explicit GDPR consent checkbox on the login page
- GDPR consent status stored server-side via API endpoint
- Data export endpoint available (POST /users/me/export)
- Account deletion endpoint available (DELETE /users/me)
- "GDPR Compliant" badge displayed in the footer and trust bar

### Authentication Security
- Magic link login: passwordless, time-limited one-time tokens
- Microsoft OAuth: industry-standard OAuth 2.0 flow with CSRF state parameter
- JWT Bearer tokens for API authentication
- Automatic token refresh on 401 responses (transparent to the user)
- Tokens stored in server-side session, never exposed to the browser
- Logout invalidates tokens on both client and server

### Payment Security
- All payments processed through Stripe Checkout (PCI DSS compliant)
- No credit card data ever touches the StudioFace servers
- Users are redirected to Stripe's hosted checkout page

### Code Security
- No credentials or API keys hardcoded in source code
- API URL configurable via environment variable (`STUDIOFACE_API_URL`)
- Input validation for file types (JPG/PNG only), file sizes (10 MB max), and file counts (2-5)
- Email validation with regex pattern before sending magic links
- All API errors normalized into a consistent format for safe display

---

## 9. How to Run

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Quick Start

```
# 1. Clone the repository
git clone <repository-url>
cd studioface-flet

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate  (Windows)
source venv/bin/activate  (macOS/Linux)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set the API URL (optional, defaults to production)
set STUDIOFACE_API_URL=https://api.studioface.app/api/v1

# 5. Run the application
flet run app/main.py --web

# 6. Open in browser
# The app will be available at http://localhost:8550
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STUDIOFACE_API_URL` | `https://api.studioface.app/api/v1` | Backend API base URL |

---

## 10. Team

**Master in Customer Experience and Innovation (MCSBT)**
IE University, Madrid, Spain

Academic Year 2025-2026

---

*Built with Flet, powered by Google AI, secured by Stripe.*
