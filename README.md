# AnchorPay

**A persistent virtual account layer built on Nomba.**

AnchorPay gives businesses a permanent, stable account identity for every customer by managing Nomba's expiring virtual accounts behind the scenes — so businesses and customers never see a disruption.

Built for the Nomba x DevCareer Hackathon 2026, Infrastructure Track (Team: Next-Unilag).

---

## The Problem

Nomba's native virtual accounts are dynamic and temporary — they expire and are capped at a small number per user in sandbox. Businesses that rely on dedicated virtual accounts (marketplaces, subscription platforms, savings apps, escrow services) need each customer to have **one stable account number for the life of the relationship**. Without that, businesses either hit account limits at scale, or are forced to constantly reissue and re-communicate new account numbers to customers — leading to missed payments, broken trust, and reconciliation errors.

## The Solution

AnchorPay sits as a middleware layer on top of Nomba's virtual account API and gives every customer **one permanent, logical account identity** that never changes — even though the underlying Nomba account expires and gets renewed behind the scenes.

- **Persistent account abstraction** — when a Nomba account nears expiry, AnchorPay automatically issues a replacement and remaps it to the same permanent identity, invisibly.
- **Webhook reconciliation engine** — catches every incoming Nomba payment webhook, matches it to the correct permanent account, updates balances, and prevents duplicate processing.
- **REST API** — lets any external business create accounts, check balances, and view transaction history.
- **Dashboard** — a live view of every persistent account, its current active Nomba account number, balance, and history.

## Architecture

```
Business/Judge
     │
     ▼
 AnchorPay API (Django REST Framework, API-key protected)
     │
     ├── PersistentAccount  (permanent customer identity)
     │        │
     │        ├── NombaAccount (1-to-many: renewable, expiring Nomba accounts)
     │        └── Transaction  (1-to-many: reconciled payments)
     │
     ▼
 Nomba Sandbox API (auth, virtual account creation, webhooks)
```

**Tech stack:** Python, Django, Django REST Framework, PostgreSQL, deployed on Railway.

## Core Data Model

- **PersistentAccount** — the permanent, business-facing customer identity (UUID, name, email, running balance).
- **NombaAccount** — the actual, expiring Nomba virtual account currently mapped to a PersistentAccount. Old ones are kept (not deleted) for audit history.
- **Transaction** — every reconciled payment, linked to both the permanent account and the specific Nomba account it arrived on, with the full raw webhook payload stored for audit purposes.

## API Endpoints

All endpoints (except the webhook) require an `X-API-Key` header.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/accounts/` | Create a new persistent account (also creates a live Nomba virtual account) |
| GET | `/api/accounts/list/` | List all persistent accounts |
| GET | `/api/accounts/<uuid>/` | Get one account, with nested Nomba accounts and transactions |
| POST | `/webhooks/nomba/` | Receives payment notifications from Nomba |
| GET | `/` | Live dashboard |

## Security & Auth Notes

- Secrets (Nomba credentials, Django secret key, database URL, API key) are managed via environment variables — never committed to the repository.
- All external-facing API endpoints require a valid `X-API-Key` header.
- The webhook endpoint is CSRF-exempt (necessary since Nomba is a server, not a browser session) but protected by reconciliation logic that rejects payments for unrecognized accounts and rejects duplicate transaction references.
- **Known limitation:** Full HMAC signature verification of incoming Nomba webhooks (using a dashboard-configured signature key) is documented as a next step rather than fully implemented, given the hackathon timeline. Current protection relies on obscurity of the webhook URL plus strict reference-based deduplication.
- `DEBUG` should be set to `False` in any real production deployment; it may be temporarily enabled during judging for diagnostic purposes only.

## Running Locally

1. Clone the repo and create a virtual environment
2. `pip install -r requirements.txt`
3. Create a `.env` file with database credentials, Nomba sandbox credentials, and a Django secret key
4. `python manage.py migrate`
5. `python manage.py runserver`

## Live Demo

- **Live app:** https://web-production-2c377.up.railway.app/
- **Live admin panel:** https://web-production-2c377.up.railway.app/admin/

## Team

**Anchorpay** — University of Lagos student developers, Infrastructure Track.

## Roadmap Beyond the Hackathon

- Full HMAC webhook signature verification
- Automated background scheduling for account renewal (Celery/Redis) instead of manual command execution
- Multi-currency support
- Rate limiting and request logging for API consumers
