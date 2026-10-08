# INC002 - Postmortem

## Summary

A critical simulated incident caused the customer-facing session creation endpoint to return HTTP 503 responses.

The main API depended on a separate `session-provider` service over HTTP. During fault injection, the `session-provider` container was stopped, making the upstream dependency unavailable while the rest of the platform remained operational.

Prometheus detected the resulting 5xx responses and triggered `HighAPI5xxRate`.

## Customer Impact

Session creation was unavailable during the outage window.

L1 validation confirmed:

- 8 consecutive requests failed
- Failure rate: 100%
- HTTP status: `503 Service Unavailable`

## Detection

The incident was detected by Prometheus.

Alert:

`HighAPI5xxRate`

Alert state:

`FIRING`

Severity:

`critical`

The alert entered FIRING state during repeated HTTP 503 failures.

## Root Cause

The dedicated `session-provider` container was unavailable.

The main FastAPI service remained running, but its request to:

`http://session-provider:9000/session`

failed with an upstream connection error.

Application logs recorded:

`session_creation_failed`

Reason:

`upstream_connection_failure`

## Investigation

L1 confirmed:

- Nginx remained operational
- Main FastAPI API remained operational
- PostgreSQL remained healthy
- Prometheus remained operational
- `session-provider` was unavailable
- Session creation returned HTTP 503
- Customer request IDs correlated with backend failure logs

## Response

L1:

1. Reproduced the customer-facing failure.
2. Confirmed 8/8 HTTP 503 responses.
3. Assessed customer impact and classified the incident as SEV-1.
4. Verified healthy platform components.
5. Isolated the unavailable upstream dependency.
6. Reviewed monitoring and application logs.
7. Prepared a documented L2/L3 escalation.
8. Avoided restarting healthy services.

## Recovery Validation

The stopped `session-provider` container was restored and allowed to become healthy.

No restart of the main API, Nginx, PostgreSQL or Prometheus was required.

Validation after restoration:

- 10/10 session requests returned HTTP 200
- Upstream session IDs were returned successfully
- Main API remained healthy
- Database remained connected

Prometheus subsequently returned to an inactive state after the monitoring window cleared.

## Lessons

- Dependency-level isolation prevents unnecessary platform restarts.
- Monitoring provides fast confirmation of customer-facing 5xx impact.
- Request-ID and backend-log correlation produces stronger engineering escalations.
- Recovery should be validated with repeated successful requests, dependency health and monitoring state rather than a single HTTP 200.

## Preventive Improvements

- Continue monitoring API 5xx rates.
- Maintain health checks for upstream dependencies.
- Maintain a defined SEV-1 escalation path.
- Maintain 15-minute customer update cadence during critical incidents.
- Correlate customer failures with request IDs and backend logs.
- Keep automated fault-injection coverage for outage and recovery behavior.
