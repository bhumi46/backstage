# Operations

- **Deploy:** CI builds `ghcr.io/bhumi46/${{ values.name }}:<sha>` and the chart, then bumps `envs/dev/${{ values.name }}/values.yaml` in gitops. Argo CD syncs it. Other environments are promoted by PR (`gitops/scripts/promote.sh`).
- **Database:** a CloudNativePG `Cluster` named `${{ values.name }}-db` in each environment. The operator creates the Secret `${{ values.name }}-db-app`; the app reads `DATABASE_URL` from its `uri` key.
- **Migrations:** the Job `${{ values.name }}-migrate` runs on every Argo CD sync, before the new pods roll out. If it fails, the sync stops and the old pods keep serving.
- **Health:** `/healthz` (liveness), `/readyz` (readiness, checks the database).
- **Logs:** one JSON object per line, with `request_id` (also returned as the `X-Request-ID` header).
- **Metrics:** Prometheus format on `/metrics`.
{%- if values.framework == 'django' %}
- **Admin user:** `kubectl -n <env> exec -it deploy/${{ values.name }} -- python manage.py createsuperuser`
{%- endif %}

Connect to the database:

```sh
kubectl -n <env> exec -it ${{ values.name }}-db-1 -- psql app
```
