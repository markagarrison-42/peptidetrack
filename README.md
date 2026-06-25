# PeptideTrack

A patient-facing Progressive Web App (PWA) for self-managing peptide, supplement, and medication protocols. Built with Flask and vanilla JavaScript.

**Live:** https://protocol.mg42health.com

---

## Features

### Today Tab
- Daily dose checklist filtered by day-of-week schedule
- Progress bar with percentage complete
- Tap circle to log dose — `+` when untaken, `✓` when logged
- Dose confirmation modal (bottom sheet)
- Unscheduled dose logging — log any compound at any time without affecting progress

### Protocol Tab
- Create and manage multiple protocols per patient
- Add compounds with dose, unit, frequency, route, timing, and reconstitution fields
- Syringe guide auto-calculates units to draw on an insulin syringe
- Toggle protocols active/paused independently

### Progress Tab
- Body measurements log with weight trend chart
- Progress photo grid (front/side/back) via Cloudinary
- Before/After comparison view

### Profile Tab
- Edit name, email, goals
- Change username and password
- Onboarding flow for new users

### Calc Tab
- Standalone reconstitution calculator
- Supports mg, mcg, IU, g units
- Outputs concentration, volume, and syringe units

### Learn Tab
- **Library** — 127+ peptides with AI-generated reference cards (mechanism, dosing, uses, side effects, stacks) via Claude API — cached per session
- **Research** — Live peptide therapy news and research feed via Claude API web search, refreshable
- **Videos** — Curated reconstitution video guides (YouTube embeds)

---

## Tech Stack

| Layer | Stack |
|---|---|
| Backend | Python 3.11, Flask, SQLAlchemy |
| Database | MySQL (PythonAnywhere) |
| Frontend | Vanilla JS SPA, Space Grotesk font |
| Auth | Flask-Login, session-based |
| Media | Cloudinary |
| Push | VAPID web push notifications |
| AI | Anthropic Claude API (claude-sonnet-4-6) |
| Hosting | PythonAnywhere (`madfella`) |

---

## Project Structure

```
peptidetrack/
├── app.py                  # Flask factory, blueprint registration
├── models.py               # SQLAlchemy models
├── extensions.py           # db, login_manager, mail
├── routes/
│   ├── auth.py             # Login, register, password reset
│   ├── doses.py            # Dose logging, toggle, unscheduled
│   ├── protocols.py        # Protocol + compound management
│   ├── checkins.py         # Body measurements
│   ├── photos.py           # Progress photos
│   ├── profile.py          # User profile
│   ├── learn.py            # Claude API proxy (library + research)
│   ├── push.py             # Push notification subscriptions
│   └── ...
├── static/
│   ├── app.js              # Entire frontend SPA (~1600 lines)
│   ├── sw.js               # Service worker + push handler
│   ├── manifest.json       # PWA manifest
│   └── invite.html         # Onboarding/invite page
└── templates/
    └── index.html          # Single HTML shell + all CSS
```

---

## Infrastructure

- **URL:** https://protocol.mg42health.com
- **Hosting:** PythonAnywhere, account `madfella`
- **App dir:** `/home/madfella/peptidetrack`
- **WSGI:** `/var/www/protocol_mg42health_com_wsgi.py`
- **Virtualenv:** `/home/madfella/.virtualenvs/mg42fitlab` (Python 3.11)
- **DB:** MySQL `madfella$peptidetrack`

---

## Database — Notable Columns

| Table | Column | Notes |
|---|---|---|
| `dose_logs` | `off_schedule` | Boolean — flags unscheduled doses, excluded from progress |
| `protocol_items` | `reminder_time` | `HH:MM` for push notification scheduling |
| `users` | `onboarding_complete` | Controls first-login onboarding flow |
| `checkins` | `waist_in`, `hips_in`, `chest_in`, `arms_in`, `thighs_in`, `neck_in` | Body measurements in inches |

---

## Environment Variables (WSGI)

```
SECRET_KEY
DB_HOST / DB_USER / DB_PASS / DB_NAME
MAIL_USER / MAIL_PASS
CLOUDINARY_URL
VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY / VAPID_EMAIL
ANTHROPIC_API_KEY
```

---

## Deployment

```bash
# After making changes, reload the app
touch /var/www/protocol_mg42health_com_wsgi.py

# Push to GitHub
git add . && git commit -m "your message" && git push
```

---

## Safety Notice

**For Research Use Only.** This application is intended for research and educational purposes. Not medical advice.
