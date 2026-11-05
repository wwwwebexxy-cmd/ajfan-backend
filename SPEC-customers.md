# Spec: AJFAN Customer Add and List

## Objective

Create the first independent AJFAN backend slice in `D:\ajfan-backend` using
Django and Django REST Framework. An authenticated admin user must be able to
create customer records and list existing records. Django admin must be
available at `/ajifan-documents/` with email/password login and customer
management.

This slice does not implement the frontend, customer detail/edit screens,
search/filtering, API token login, logout, deployment, cloud resources, or
production database configuration.

## Customer data contract

The customer create endpoint accepts these fields:

| Field | Type | Required in this slice |
|---|---|---|
| `name` | string | yes |
| `email` | email string | yes |
| `phone` | string | yes |
| `address_line_1` | string | no |
| `address_line_2` | string | no |
| `address_line_3` | string | no |
| `bank_name` | string | no |
| `account_holder_name` | string | no |
| `account_number` | string | no |
| `swift_address` | string | no |
| `trn` | string | no |
| `notes` | string | no |

The list response includes at minimum `id`, `name`, `email`, and `phone`, plus
the server timestamps if present. A later detail endpoint will expose the
complete record.

## API contract

- `POST /api/customers/` creates a customer and returns HTTP `201` with the
  created record.
- `GET /api/customers/` returns HTTP `200` with a list of customers, newest
  first.
- Only authenticated staff/admin users may access the API; non-staff users
  return HTTP `403`.
- Unauthenticated API requests return HTTP `401`.
- Invalid create data returns HTTP `400` with field-level validation errors.
- The API uses plural resource naming and snake_case field names matching the
  Django model.
- API authentication accepts HTTP Basic credentials and Django admin session
  authentication; production traffic must use HTTPS.

## Admin contract

- `GET /ajifan-documents/` shows the Django admin login page when unauthenticated.
- The admin login accepts email and password.
- After login, the admin can add and list customers.
- The admin customer list shows name, email, and phone.
- No existing project deployment settings, credentials, data, domains, or
  server configuration are copied into this project.

## Tech stack

- Python 3.12+
- Django 5.2+
- Django REST Framework 3.16+
- SQLite for local development/tests when `DJANGO_DB_ENGINE` is unset
- MySQL 8.0 supported through environment-based settings

## Commands

```text
python -m pip install -r requirements.txt
python manage.py check
python manage.py test
python manage.py runserver
```

## Project structure

```text
manage.py                 Django entry point
config/                   Project settings, URLs, and WSGI/ASGI
accounts/                 Admin-compatible email user model and admin login support
customers/                Customer model, serializer, API view, admin, and tests
requirements.txt          Runtime dependencies
```

## Testing strategy

- Django test client/API tests cover authenticated create and list flows.
- Authentication tests cover anonymous API rejection and admin email login.
- Model/serializer tests cover required fields and email validation.
- Run the full suite with `python manage.py test` before committing.

## Boundaries

- Always: validate input at the API boundary, protect customer APIs, keep
  credentials out of source control, and run Django checks/tests.
- Ask first: deployment, cloud resources, production database, frontend
  integration, or any data migration.
- Never: reuse any previous project resource, copy `.env` files,
  commit secrets, or change another project.

## Success criteria

- A fresh checkout installs from `requirements.txt` and passes `python manage.py check`.
- The test suite proves customer create/list behavior and admin email login.
- `/ajifan-documents/` is the only admin route exposed by this slice.
- No old project names, domains, IP addresses, API URLs, credentials, or
  deployment configuration are present in the new project.

## Open questions

- The frontend link label can be shown as “Ajifan Documents”; its frontend
  seed/navigation entry will be added only when frontend work is requested.
