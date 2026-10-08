# INC002 - Postmortem

## Summary

A critical incident caused the session creation endpoint to return HTTP 503 responses.

Prometheus detected elevated 5xx responses and triggered the `HighAPI5xxRate` alert.

## Customer Impact

Session creation was unavailable during the incident.

L1 validation confirmed:

- 12 consecutive requests failed
- Failure rate: 100%
- HTTP status: 503

## Detection

The incident was detected by Prometheus.

Alert:

`HighAPI5xxRate`

Alert state:

`FIRING`

Severity:

`critical`

Alert active from:

`2026-10-08 15:04:49 UTC`

## Investigation

L1 confirmed:

- Nginx remained operational
- FastAPI process remained operational
- PostgreSQL remained healthy
- Prometheus remained operational
- Session creation specifically returned HTTP 503

Application logs identified:

`session_creation_failed`

Reason:

`upstream_connection_failure`

## Response

L1:

1. Reproduced the failure.
2. Assessed customer impact.
3. Classified the incident as SEV-1.
4. Reviewed monitoring and logs.
5. Avoided unnecessary service restarts.
6. Prepared a documented L2/L3 escalation.
7. Maintained client status communication.
8. Validated recovery after remediation.

## Recovery Validation

At `2026-10-08 15:09:12 UTC`:

- 10/10 session requests returned HTTP 200
- API health returned OK
- Database remained connected

Prometheus subsequently returned to an inactive state.

## Lessons

- Monitoring allowed rapid detection before relying only on customer reports.
- Endpoint-level investigation prevented unnecessary infrastructure restarts.
- Request/log evidence produced a cleaner engineering escalation.
- Recovery required multiple successful requests and monitoring validation before closure.

## Preventive Improvements

- Continue monitoring API 5xx rates.
- Maintain a defined SEV-1 escalation path.
- Maintain 15-minute customer update cadence during critical incidents.
- Correlate customer failures with request IDs and backend logs.
- Validate recovery using both functional tests and monitoring.
