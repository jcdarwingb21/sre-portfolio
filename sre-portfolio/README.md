# SRE Portfolio — CI/CD + IaC on AWS

![CI Pipeline](https://github.com/jcdarwingb21/sre-portfolio/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Terraform](https://img.shields.io/badge/terraform-1.8-purple)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

End-to-end SRE project demonstrating a production-grade deployment pipeline for a containerized Python service on AWS ECS Fargate, with full observability stack and Infrastructure as Code.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      GitHub                             │
│                                                         │
│  push to main ──► GitHub Actions CI/CD Pipeline        │
│                        │                               │
│              ┌─────────┼──────────┐                    │
│              ▼         ▼          ▼                    │
│           Tests      Build     Security                │
│          (pytest)   (Docker)   (Trivy)                 │
└──────────────────────┬──────────────────────────────────┘
                       │  (deploy step — requires AWS secrets)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                      AWS                                │
│                                                         │
│   ECR Registry ──► ECS Fargate Cluster                 │
│                         │                              │
│                    Task Definition                      │
│                    (Flask app + healthcheck)            │
│                         │                              │
│                    CloudWatch Logs                      │
└─────────────────────────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│                  Observability (local)                  │
│                                                         │
│   Flask /metrics ──► Prometheus ──► Grafana :3000      │
│                          │                             │
│                     Alert Rules                        │
│                  (SLO-based: error rate, latency)      │
└─────────────────────────────────────────────────────────┘
```

---

## Stack

| Layer | Technology |
|---|---|
| Application | Python 3.12 + Flask |
| Containerization | Docker (multi-stage build) |
| Orchestration | AWS ECS Fargate |
| Registry | AWS ECR |
| IaC | Terraform 1.8 |
| CI/CD | GitHub Actions |
| Metrics | Prometheus + prometheus-client |
| Dashboards | Grafana |
| Security scanning | Trivy |
| State backend | AWS S3 + DynamoDB locking |

---

## Project Structure

```
sre-portfolio/
├── app/
│   ├── main.py              # Flask app with Prometheus metrics
│   ├── requirements.txt
│   ├── Dockerfile           # Multi-stage, non-root user
│   └── test_main.py         # Pytest unit tests
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD: test → build → scan → deploy
├── terraform/
│   ├── main.tf              # Provider + remote state config
│   ├── variables.tf         # Input variables with validation
│   ├── ecr.tf               # ECR repository + lifecycle policy
│   └── ecs.tf               # ECS cluster, task definition, IAM
├── monitoring/
│   ├── prometheus.yml       # Scrape config
│   └── alerts.yml           # SLO-based alerting rules
├── docker-compose.yml       # Local dev: app + Prometheus + Grafana
└── .gitignore
```

---

## Running Locally

**Prerequisites:** Docker + Docker Compose

```bash
# Clone the repo
git clone https://github.com/jcdarwingb21/sre-portfolio.git
cd sre-portfolio

# Start the full stack (app + Prometheus + Grafana)
docker compose up --build

# Endpoints
# App:        http://localhost:5000
# Health:     http://localhost:5000/health
# Metrics:    http://localhost:5000/metrics
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000  (admin/admin)
```

**Run tests only:**

```bash
cd app
pip install -r requirements.txt
pytest test_main.py -v
```

---

## CI/CD Pipeline

The pipeline runs automatically on every push to `main` or `develop`:

```
push / PR
   │
   ├─ test          pytest — unit tests must pass
   │
   ├─ build         Docker multi-stage build + smoke test
   │    └─ needs: test
   │
   └─ security-scan Trivy — scan for CRITICAL/HIGH CVEs
        └─ needs: build

   # deploy-staging (commented — requires AWS secrets)
   # └─ needs: security-scan, only on main
```

To enable deployment, add these secrets in GitHub → Settings → Secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `ECR_REGISTRY`

---

## Infrastructure (Terraform)

```bash
cd terraform

# Initialize (configure S3 backend first in main.tf)
terraform init

# Preview changes
terraform plan -var="environment=staging"

# Apply
terraform apply -var="environment=staging"

# Teardown
terraform destroy -var="environment=staging"
```

**Resources created:**
- ECR repository with scan-on-push and lifecycle policy
- ECS Fargate cluster with Container Insights enabled
- ECS Task Definition with health checks and CloudWatch logging
- IAM execution role with least-privilege policy
- CloudWatch log group (30-day retention)

---

## Observability & SLOs

Alerting rules are defined in `monitoring/alerts.yml` based on SLO targets:

| SLO | Target | Alert threshold |
|---|---|---|
| Error rate | < 0.5% | > 0.5% for 2 min → CRITICAL |
| p99 latency | < 500ms | > 500ms for 3 min → WARNING |
| Availability | Service up | Down for 1 min → CRITICAL |

---

## Status

- [x] Flask app with `/health`, `/ready`, `/metrics` endpoints
- [x] Multi-stage Dockerfile with non-root user
- [x] GitHub Actions pipeline (test → build → security scan)
- [x] Terraform IaC for ECS Fargate + ECR
- [x] Prometheus scrape config + SLO-based alert rules
- [x] Docker Compose local dev environment
- [ ] Deploy to AWS ECS Fargate (in progress)
- [ ] Grafana dashboard JSON export
- [ ] Blue/green deployment strategy

---

## Author

**Darwin Grueso** — Site Reliability Engineer  
[linkedin.com/in/darwingrueso-656aab201](https://linkedin.com/in/darwingrueso-656aab201)
