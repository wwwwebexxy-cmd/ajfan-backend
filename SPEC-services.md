# AJFAN Service Module

## Data contract

The authenticated service API accepts:

- `name`
- `image` (optional image upload)
- `service_charge`
- `includes_government_fee`
- `government_fee`
- `description`

Service charges and government fees are non-negative decimal amounts. Deleted
services are soft-deleted and excluded from active list/detail responses.

## API contract

- `GET /api/services/` lists active services.
- `POST /api/services/` creates a service using multipart form data.
- `GET /api/services/<id>/` returns complete service details.
- `PATCH /api/services/<id>/` updates supplied fields and can replace the image.
- `DELETE /api/services/<id>/` soft-deletes the service and returns `204`.
- All service endpoints require an authenticated staff/admin user.
