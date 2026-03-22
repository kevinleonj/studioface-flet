# StudioFace Flet Frontend — Future Improvements

This document outlines potential enhancements for future development of the StudioFace frontend application, organized by priority and implementation complexity.

---

## 1. WebSocket for Real-Time Generation Progress

**Current state:** The gallery page polls the API every 5 seconds to check generation status.

**Improvement:** Replace HTTP polling with a WebSocket connection to the backend. The server would push status updates (e.g., "Processing face detection...", "Generating variant 2 of 4...", "Applying style filters...") in real time. This would provide more granular progress feedback, reduce unnecessary API calls, and give users confidence that their generation is actively progressing.

**Impact:** Better user experience during the 2-5 minute generation wait. Lower API load.

---

## 2. Image Lightbox / Zoom in Gallery

**Current state:** Headshot images in the gallery are displayed at a fixed 240x280px thumbnail size with no way to view them larger.

**Improvement:** Add a lightbox overlay that opens when clicking a headshot thumbnail. The overlay would display the full-resolution image centered on screen with a dark backdrop, navigation arrows to cycle through images, and a close button. Support pinch-to-zoom on mobile and mouse wheel zoom on desktop.

**Impact:** Users can inspect image quality before downloading, leading to higher satisfaction.

---

## 3. ZIP Download of All Headshots

**Current state:** Users must download each headshot individually by clicking the "Download" button on each card.

**Improvement:** Add a "Download All as ZIP" button that bundles all generated headshots from a session into a single ZIP archive. The ZIP file would be named with the style and date (e.g., `studioface-corporate-2026-03-22.zip`). Generation of the ZIP could happen server-side or client-side using Python's zipfile module.

**Impact:** Saves time for users who want all their headshots. Reduces friction in the download experience.

---

## 4. Settings Page (Language, GDPR Data Export, Account Deletion)

**Current state:** Language is set via the navbar dropdown. GDPR data export and account deletion endpoints exist in the API client but are not exposed in the UI.

**Improvement:** Create a `/settings` page with sections for:
- **Language preference:** Persistent language selection saved to the backend (PUT /users/me/locale)
- **GDPR data export:** Button to request a data export (POST /users/me/export) with download link when ready
- **Account deletion:** Button to permanently delete the account (DELETE /users/me) with confirmation dialog
- **Email preferences:** Opt in/out of marketing emails
- **Session management:** View active sessions, sign out of all devices

**Impact:** Full GDPR compliance with user-facing data controls. Regulatory requirement for EU markets.

---

## 5. Admin Dashboard for Analytics

**Current state:** No admin interface exists. Analytics require direct database queries.

**Improvement:** Build an admin-only dashboard at `/admin` with:
- Total generations, revenue, and active users (daily/weekly/monthly charts)
- Generation success/failure rates by style
- User acquisition funnel (landing views -> sign-ups -> generations -> payments)
- Average generation time and API response times
- Geographic distribution of users
- Revenue breakdown by currency and style

**Impact:** Business intelligence for the team. Identifies bottlenecks and popular styles.

---

## 6. Push Notifications When Generation Completes

**Current state:** Users receive an email notification when headshots are ready. If they stay on the page, they see updates via polling.

**Improvement:** Implement browser push notifications using the Web Push API. When a generation completes, send a push notification even if the user has navigated away from StudioFace. The notification would say "Your headshots are ready!" and link directly to the gallery.

**Impact:** Faster re-engagement. Users don't need to check email or keep the tab open.

---

## 7. Progressive Web App (PWA) Support

**Current state:** The application runs as a standard web page with no offline capability or installability.

**Improvement:** Add PWA support with:
- Service worker for caching static assets (theme, translations, sample images)
- Web app manifest for "Add to Home Screen" functionality
- Offline landing page showing cached content
- Background sync for queued uploads when connectivity returns

**Impact:** App-like experience on mobile. Faster load times on repeat visits.

---

## 8. Accessibility Improvements (Screen Reader, Keyboard Navigation)

**Current state:** The app uses Material Design components that provide some baseline accessibility, but no explicit ARIA labels or keyboard navigation patterns have been implemented.

**Improvement:**
- Add ARIA labels to all interactive elements (buttons, navigation links, form fields)
- Implement keyboard navigation with visible focus indicators
- Ensure color contrast meets WCAG 2.1 AA standards (some text-on-dark combinations may need adjustment)
- Add screen reader announcements for dynamic content changes (route navigation, loading states, error messages)
- Test with NVDA, VoiceOver, and TalkBack

**Impact:** Legal compliance with EU accessibility directives. Inclusive design for all users.

---

## 9. Offline Mode with Cached Assets

**Current state:** The application requires an active internet connection for all functionality.

**Improvement:** Cache the following for offline use:
- Landing page content (hero text, sample photos, style previews)
- Translation dictionaries for all 3 languages
- Theme constants and design assets
- Previously downloaded headshots in the gallery

When offline, show a banner indicating limited functionality and disable features that require the API (login, upload, generation, payment).

**Impact:** Usable landing page in areas with spotty connectivity. Cached gallery for viewing existing headshots.

---

## 10. A/B Testing for CTA Copy

**Current state:** The CTA button text is hardcoded in translation files (e.g., "Create My Headshot -- EUR 6.99 -->").

**Improvement:** Implement a simple A/B testing framework that:
- Randomly assigns visitors to variant groups on first visit
- Tests different CTA copy, button colors, pricing display formats, and hero text
- Tracks conversion events (CTA click, sign-up, payment completion)
- Reports results through the admin dashboard
- Variants could include: "Get Started", "Try Now", "See Your Headshot", with/without price in CTA

**Impact:** Data-driven optimization of the conversion funnel. Could significantly increase payment conversion rates.

---

## 11. Social Sharing (WhatsApp, LinkedIn)

**Current state:** Users can only download their headshots. There is no sharing functionality.

**Improvement:** Add share buttons to the gallery page for each headshot:
- **LinkedIn:** Share headshot directly as a profile photo update or post
- **WhatsApp:** Send headshot to contacts with a preview and link to StudioFace
- **Twitter/X:** Tweet with headshot image and auto-generated caption
- **Copy link:** Generate a shareable link to view the headshot (time-limited for privacy)

Include a referral code in shared links for tracking viral acquisition.

**Impact:** Organic growth through social sharing. LinkedIn sharing is especially valuable given the professional headshot use case.

---

## 12. Before/After Comparison Slider

**Current state:** Users upload selfies and receive generated headshots, but there is no way to see them side by side.

**Improvement:** Add a comparison view in the gallery that shows:
- The original uploaded selfie on the left
- The AI-generated headshot on the right
- A draggable slider in the middle to reveal/hide each side
- This would work both on the gallery page and as a shareable comparison link

**Impact:** Dramatically demonstrates the AI's capability. Excellent for marketing and social sharing.

---

## 13. Multi-Currency Pricing (EUR/USD/GBP)

**Current state:** Pricing is displayed in EUR only. The Stripe checkout API supports a currency parameter but it defaults to EUR.

**Improvement:**
- Auto-detect user's locale/region to suggest appropriate currency
- Display prices in EUR, USD, or GBP throughout the landing page and create wizard
- Allow manual currency selection in a dropdown
- Ensure all i18n strings with prices use dynamic formatting (e.g., `{price}` instead of hardcoded "EUR 6.99")
- Update the Stripe checkout call to pass the selected currency

**Impact:** Better user experience for non-EU users. May increase international conversion rates.

---

## 14. Camera Face Detection Overlay Guide

**Current state:** The webcam capture shows a raw camera feed with a simple "Capture Photo" button. Users receive no guidance on positioning.

**Improvement:** Overlay a face detection guide on the camera feed:
- Draw a translucent oval outline where the face should be positioned
- Use a lightweight face detection model (e.g., MediaPipe Face Detection via JavaScript interop) to detect when a face is properly centered
- Show green outline when the face is well-positioned, red when it's not
- Provide text hints: "Move closer", "Center your face", "Look at the camera"
- Auto-capture when the face is properly positioned for 2 seconds

**Impact:** Higher quality selfie uploads lead to better AI generation results and fewer failed generations.

---

## Priority Matrix

| # | Improvement | Impact | Effort | Priority |
|---|------------|--------|--------|----------|
| 1 | WebSocket progress | High | Medium | P1 |
| 2 | Image lightbox | Medium | Low | P1 |
| 3 | ZIP download | Medium | Low | P1 |
| 4 | Settings page | High | Medium | P1 |
| 8 | Accessibility | High | Medium | P1 |
| 13 | Multi-currency | Medium | Low | P2 |
| 14 | Camera face guide | High | High | P2 |
| 12 | Before/After slider | Medium | Medium | P2 |
| 11 | Social sharing | Medium | Medium | P2 |
| 6 | Push notifications | Medium | Medium | P2 |
| 7 | PWA support | Medium | Medium | P3 |
| 10 | A/B testing | Medium | High | P3 |
| 5 | Admin dashboard | High | High | P3 |
| 9 | Offline mode | Low | Medium | P3 |
