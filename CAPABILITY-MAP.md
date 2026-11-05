# Capability Map: AJFAN Customer Backend

This is a new, independent Django REST API backend. It must not reuse
deployment settings, credentials, data, domains, repositories, or server
configuration from another project.

| Module id | Responsibility | Depends on |
|---|---|---|
| identity | Email/password login for the admin/API user, authenticated API access, logout, and Django admin access | — |
| customers | Customer record storage, validation, create/list/detail APIs, soft delete, name/phone filtering, and Django admin management | identity |

Build order: `identity` → `customers`

## Initiative boundary

The full first initiative covers the two modules above:

- `identity`: login endpoint and protected API access using Django REST Framework authentication.
- `customers`: customer fields requested so far: name, email, phone, address lane 1, address lane 2, address lane 3, bank name, account holder name, account number, SWIFT address, IBAN, TRN, and notes.
- Customer list responses expose name, email, and phone, while detail responses expose the complete record.
- Frontend customer list supports instant local filtering by name, email, and phone.
- Django admin exposes login and customer management.

Frontend screens, deployment, cloud resources, production database setup,
email delivery, roles/permissions beyond the initial authenticated admin flow,
and future requirements are outside this first delivery.

## Current implementation slice

The current approved slice is deliberately smaller than the full initiative:

- Customer create/add and customer list APIs.
- Django admin customer management at `/ajifan-documents/`.
- Email/password login screen supplied by Django admin at that path.

Customer edit, API token login, and logout remain subsequent
slices unless explicitly pulled into this one. The frontend customer create,
list, view, and soft-delete actions are now integrated.
