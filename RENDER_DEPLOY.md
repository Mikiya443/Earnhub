# Deploy Earnhubs on Render

1. Push this whole folder to your GitHub `Earnhubs` repository.
2. In Render, create a new Blueprint and select that GitHub repository.
3. Render reads `render.yaml` and creates:
   - `earnhubs-django`
   - `earnhubs-realtime`
   - `earnhubs-frontend`
   - `earnhubs-db` PostgreSQL
4. After deployment, open the Django service shell and create an admin:
   `python manage.py createsuperuser`
5. Check the Django service, Node health endpoint, and frontend.
6. If your Render service names/URLs differ, update the frontend/Django CORS and CSRF environment variables accordingly.

Important:
- Do not commit `.env` files or passwords.
- Generated secrets in the Blueprint should be kept private.
- Use PostgreSQL for production; SQLite remains only as a local fallback.
- For real payments, add a payment provider and verified webhooks before accepting real money.
