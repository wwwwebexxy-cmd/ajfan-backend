# Implementation Plan: AJFAN Customer Add and List

## Overview

Build the first independent AJFAN Django/DRF backend slice in
`D:\ajfan-backend`. The slice provides an email/password Django admin at
`/ajifan-documents/` and a protected Customer create/list API.

## Architecture decisions

- Use a custom Django user model with email as the login identifier from the
  first migration, avoiding a later auth migration.
- Use Django session authentication for the admin and DRF API, with HTTP Basic
  authentication available for API clients in this slice; API token login is a
  later slice.
- Use SQLite for local development/tests only and read the Django secret key
  from an environment variable with a safe local fallback.
- Use DRF `ListCreateAPIView` with `IsAuthenticated`; validation remains in the
  serializer boundary.
- Expose admin under `/ajifan-documents/` and do not expose the default
  `/admin/` route.

## Task list

### Phase 1: Identity foundation

- [x] Task 1: Bootstrap Django project and email-based admin login
  - Acceptance: project checks pass; custom user uses email login; admin is
    mounted at `/ajifan-documents/`; an admin user can log in with email and
    password.
  - Verify: focused Django auth/admin tests and `python manage.py check`.
  - Files: `manage.py`, `config/*`, `accounts/*`, `requirements.txt`.

### Phase 2: Customer create/list vertical slice

- [x] Task 2: Add Customer model, admin, serializer, and protected API
  - Acceptance: authenticated `POST /api/customers/` validates and saves all
    requested fields; authenticated `GET /api/customers/` returns newest-first
    records with name, email, and phone; anonymous requests return `401`.
  - Verify: customer API tests, model migration, and `python manage.py check`.
  - Files: `customers/*`, `config/urls.py`.

### Checkpoint: First delivery

- [x] Full test suite passes with `python manage.py test`.
- [x] API and admin routes are verified with Django's test client.
- [x] No deployment settings, credentials, secrets, or old project resources
      are present.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Changing the user model after initial migrations | High | Define `AUTH_USER_MODEL` before the first migration. |
| Customer bank/account fields are sensitive | High | Keep them behind authentication, avoid logging payloads, and do not expose them in list responses. |
| Admin URL ambiguity | Medium | Use the explicitly requested `/ajifan-documents/` route and document it. |

## Out of scope

Frontend navigation/seed, customer edit/search, API token login, logout,
deployment, cloud resources, production database, and data migration.
