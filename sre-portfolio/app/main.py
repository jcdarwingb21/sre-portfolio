import time
import signal
import sys
import logging
import os
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Prometheus metrics ---
REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'HTTP request latency',
    ['endpoint']
)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENV         = os.getenv("ENV", "dev")
START_TIME  = time.time()


def handle_sigterm(sig, frame):
    logger.info("SIGTERM received — shutting down gracefully")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)


@app.route("/")
def index():
    start = time.time()
    REQUEST_COUNT.labels(method="GET", endpoint="/", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start)
    return jsonify({
        "service": "sre-portfolio-app",
        "version": APP_VERSION,
        "env": ENV
    })


@app.route("/health")
def health():
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()
    return jsonify({"status": "healthy", "uptime_seconds": round(time.time() - START_TIME, 2)})


@app.route("/ready")
def ready():
    # Readiness probe — add real dependency checks here (DB, cache, etc.)
    REQUEST_COUNT.labels(method="GET", endpoint="/ready", status="200").inc()
    return jsonify({"status": "ready"})


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    logger.info(f"Starting sre-portfolio-app v{APP_VERSION} in {ENV}")
    app.run(host="0.0.0.0", port=5000)
