# Platform MVP

This folder contains the sellable platform foundation:

- `backend/` - FastAPI + Mongo API for auth, courses, orders, enrollments
- `web/` - Next.js app for landing, catalog, checkout, dashboard, admin

Run everything from root:

```bash
docker compose up --build
```

Then open:

- Web app: `http://localhost:3000`
- API docs: `http://localhost:8080/docs`
