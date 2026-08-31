# Coldline Task 1.5 — Capacity review correction

The supplied system runs one bounded asynchronous workflow:

```text
sensor reading -> API -> PostgreSQL -> Redis Streams -> worker -> PostgreSQL
                    |                                      |
                    +---------- local telemetry -----------+
```

The API accepts an out-of-range synthetic shipment reading. PostgreSQL stores its durable state.
Redis Streams carries a provider-neutral `JobQueue` message. The worker calls the deterministic
`ModelProvider` and stores the result. Prometheus, Grafana, and Jaeger provide local diagnostic
evidence.

There is no hosted model, LocalStack service, UI, or agent framework in Task 1.1.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)]({{CODESPACES_URL}})

The Codespaces URL is an authoring substitution token. CMS must replace it with the exact generated
repository and supported branch. A remaining token blocks publication.

## Start the system

Prerequisites are Python 3.12 and Docker with Compose v2. The bootstrap installs pinned uv 0.11.8
under `.tools/bin`.

```shell
python infra/scripts/bootstrap.py
./.tools/bin/uv sync --frozen
./.tools/bin/uv run --frozen poe preflight
./.tools/bin/uv run --frozen poe start
./.tools/bin/uv run --frozen poe ready
./.tools/bin/uv run --frozen poe scenario
```

PowerShell and POSIX wrappers are available under `infra/scripts/`. After uv is on `PATH`, the
shorter `uv run --frozen poe <task>` form works.

| Service | Local URL | Purpose |
|---|---|---|
| API | `http://localhost:8000` | Submit and inspect exception workflows |
| Grafana | `http://localhost:3000` | Use the focused diagnostics dashboard |
| Prometheus | `http://localhost:9090` | Query bounded metrics |
| Jaeger | `http://localhost:16686` | Inspect local traces |

Each of these ports can be overridden by setting the matching `COLDLINE_API_HOST_PORT`,
`COLDLINE_GRAFANA_HOST_PORT`, `COLDLINE_PROMETHEUS_HOST_PORT`, or `COLDLINE_JAEGER_HOST_PORT` environment
variable (see `.env.example`) before running `poe start`, if a default collides with something already
running on your machine.

PostgreSQL, Redis, worker metrics, and OTLP remain inside the Compose network. Codespaces uses the
same `compose.yaml` and keeps every forwarded port private.

## Find your way around

Start with the [codebase guide](docs/student/codebase-guide.md). It explains the reading order,
folder responsibilities, runtime flow, five ports, tests, commands, and files that cannot safely
contain comments.

The application source lives in five flat packages:

| Package | Responsibility |
|---|---|
| `api` | HTTP delivery, API use case, configuration, and composition |
| `worker` | Background processing, retries, configuration, and composition |
| `domain` | Provider-neutral contracts, state rules, identity, and redaction |
| `ports` | Exactly five visible application interfaces |
| `adapters` | PostgreSQL, Redis Streams, deterministic model, logs, and traces |

## Common commands

| Command | Use |
|---|---|
| `poe unit` | Run fast isolated behavior tests |
| `poe contract` | Check interfaces, boundaries, submissions, and repository structure |
| `poe smoke` | Check the initialized running platform |
| `poe e2e` | Run the external API-to-worker workflow |
| `poe verify` | Run the public student verification path |
| `poe restart` | Restart API and worker processes |
| `poe stop` | Stop containers and keep named volumes |
| `poe reset` | Stop containers and delete local named volumes |

## Task boundary

Task 1.5 asks you to audit a flawed, AI-generated 10x capacity report claim by claim, correct its
scaling math with explicit units, and author an Architecture Decision Record (ADR) that recommends
one bounded scaling action. This Task is read-only for application code — you add only new answer
content.

Only these paths are student-editable:

- `submission.yaml`

The public verifier checks answer structure, completeness, and that your corrected worker-count
calculation is within tolerance of the measured `docs/student/task-1-4-reference-metrics.yaml`
fixture. It cannot grade engineering judgment. The instructor reviews the quality of the claim
audit, the scaling recommendation, and the ADR.

### Student walkthrough

See **Task 1.5: Capacity Review Correction** in your course platform for the full walkthrough. In outline: read `docs/student/ai-capacity-report-draft.md` and classify
every major claim as supported, a calculation error, or an unsupported assumption; recompute the
10x ingestion rate, exception rate, and worker count with explicit units, using the real Task 1.4
measurements in `docs/student/task-1-4-reference-metrics.yaml`; propose one bounded, cost-effective
scaling recommendation; write an ADR covering Context, Decision, Consequences, Alternatives
Considered, Action Trigger, Rollback Condition, and Next Measurement; run `poe verify`; then record
all of it in `submission.yaml`.

## Operational limits

This local system has no user authentication, authorization, TLS termination, or production secret
store. The Compose PostgreSQL password is a local-only non-secret credential. Never place real
credentials, personal data, or production records in this repository.

Named volumes preserve local PostgreSQL, Redis, Prometheus, Grafana, and Jaeger state across
`poe stop`. The `poe reset` command deletes that state. This topology makes no backup,
replication, high-availability, disaster-recovery, capacity, latency-SLO, or availability claim.
See [JobQueue fidelity](docs/fidelity/JobQueue.md) and
[ModelProvider fidelity](docs/fidelity/ModelProvider.md) for the active adapter boundaries. The
[local runtime evidence](docs/fidelity/local-runtime.md) records the current measurement and its
qualification limits.
