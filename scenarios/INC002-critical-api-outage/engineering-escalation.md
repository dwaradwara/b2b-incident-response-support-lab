# INC002 - L2/L3 Engineering Escalation

## Severity

SEV-1 - Critical

## Impact

Customer session creation is unavailable.

During L1 validation:

- Requests tested: 8
- Successful requests: 0
- Failed requests: 8
- Failure rate: 100%
- HTTP response: `503 Service Unavailable`

## Affected Endpoint

`POST /api/v1/session`

## Monitoring Evidence

Prometheus alert:

`HighAPI5xxRate`

State:

`FIRING`

Severity:

`critical`

The alert entered FIRING state during the fault-injection window while repeated HTTP 503 responses were being generated.

## Infrastructure Validation

The following services remained operational:

- Nginx
- Main FastAPI API
- PostgreSQL
- Prometheus

The following dependency was unavailable:

- `session-provider`

Database health remained healthy.

## Application Evidence

Application logs contain:

`session_creation_failed`

Reason:

`upstream_connection_failure`

Upstream:

`http://session-provider:9000/session`

HTTP status:

`503`

The customer-facing response request ID was correlated with the backend failure log. Evidence is captured in:

`docs/evidence/inc002-503-upstream-log.png`

## L1 Actions

1. Reproduced the customer-impacting failure.
2. Confirmed 8/8 HTTP 503 responses.
3. Verified main API, Nginx, PostgreSQL and Prometheus health.
4. Isolated the unavailable `session-provider` dependency.
5. Reviewed application logs and identified `upstream_connection_failure`.
6. Correlated customer request evidence with backend logs.
7. Confirmed the critical Prometheus alert.
8. Avoided unnecessary restarts of healthy services.

## Engineering Request

Investigate and restore the unavailable `session-provider` dependency.

After restoration, L1 will verify dependency health, validate session creation with repeated HTTP 200 responses and confirm monitoring recovery.
