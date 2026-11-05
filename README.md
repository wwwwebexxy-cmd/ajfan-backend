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
timestamps. Bank and account fields are accepted on create but are not exposed
in the list response.

For anything beyond local development, set `DJANGO_SECRET_KEY`, disable
`DJANGO_DEBUG`, configure `DJANGO_ALLOWED_HOSTS`, and serve the API over HTTPS.

## Verification

```powershell
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```
