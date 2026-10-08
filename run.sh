#!/bin/bash

set -e

# Call the venv directly: `uv run` re-syncs the env on every start, which only
# widens the window between "pod Running" and "port 8000 open".
export PATH="/app/.venv/bin:$PATH"

# LMS injects AUTH_SERVICE_URL=http://localhost:8000, which inside the pod is
# this very service. Services there follow the pattern <namespace>-web.<namespace>,
# and the auth-service namespace differs from ours only by its suffix.
NS_FILE=/var/run/secrets/kubernetes.io/serviceaccount/namespace
if [ -f "$NS_FILE" ] && [[ "${AUTH_SERVICE_URL:-}" =~ ^(https?://(localhost|127\.0\.0\.1)(:[0-9]+)?/?)?$ ]]; then
    auth_ns="$(sed 's/ad-service$/auth-service/' "$NS_FILE")"
    export AUTH_SERVICE_URL="http://${auth_ns}-web.${auth_ns}.svc.cluster.local:8000"
fi

alembic upgrade head

# The cluster runs a single container per service, so the outbox relay lives
# next to the API. It's kept in a restart loop so a Kafka hiccup never takes
# the API down with it; uvicorn stays PID 1 and owns signals.
(
    while true; do
        python -m bin.outbox || true
        echo "outbox relay exited, restarting in 5s" >&2
        sleep 5
    done
) &

exec uvicorn bin.api:app --host 0.0.0.0 --port "${PORT:-8000}"
