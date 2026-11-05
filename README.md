# AJFAN Backend

Independent Django REST API backend for AJFAN customer records.

## Local setup

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Use the email and password created by `createsuperuser` at:

- Admin: `http://127.0.0.1:8000/ajifan-documents/`
- Customer API: `http://127.0.0.1:8000/api/customers/`

The API requires authentication. `POST /api/customers/` creates a customer;
`GET /api/customers/` lists customers with `id`, `name`, `email`, `phone`, and
timestamps. Bank and account fields, including SWIFT address, IBAN, and TRN, are
accepted on create but are not exposed in the list response.
Use `GET /api/customers/<id>/` for the complete customer details and
`PATCH /api/customers/<id>/` to edit a customer. Use
`DELETE /api/customers/<id>/` to remove a customer.
Deletion is soft delete: the database record is retained and marked deleted,
while active customer lists no longer include it.

For anything beyond local development, set `DJANGO_SECRET_KEY`, disable
`DJANGO_DEBUG`, configure `DJANGO_ALLOWED_HOSTS`, and serve the API over HTTPS.

## MySQL Workbench

The backend supports a separate local MySQL database. In MySQL Workbench, use
the AJFAN connection at `127.0.0.1:3306` and create the new schema:

```sql
CREATE DATABASE IF NOT EXISTS ajfan_backend
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

Then set these environment variables before running migrations. Keep the real
password only in the local environment; never commit a `.env` file.

```text
DJANGO_DB_ENGINE=mysql
DJANGO_DB_NAME=ajfan_backend
DJANGO_DB_USER=root
DJANGO_DB_PASSWORD=your-local-mysql-password
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=3306
```

Run `python manage.py migrate` after the schema exists.

## Verification

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```
