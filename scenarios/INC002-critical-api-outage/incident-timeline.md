# INC002 - SEV-1 Incident Timeline

## Incident

Session Creation Service Unavailable

## Severity

SEV-1 - Critical

## Timeline - Relative

### T+0m - Detection

Prometheus `HighAPI5xxRate` entered the FIRING state after repeated failures on:

`POST /api/v1/session`

Observed:

- HTTP status: `503 Service Unavailable`
- Severity: `critical`
- Customer workflow impact: session creation unavailable

### T+1m - Customer Impact Validation

L1 reproduced the failure repeatedly.

Validation:

- 8 consecutive requests tested
- 8 returned HTTP 503
- Failure rate during validation: 100%

### T+2m - Infrastructure Isolation

Infrastructure health was checked.

- Main FastAPI API: running
- PostgreSQL: healthy
- Nginx: running
- Prometheus: running
- `session-provider`: unavailable

The incident was isolated to the upstream session-provider dependency rather than a complete platform outage.

### T+3m - Log Correlation

Application logs were reviewed.

Observed event:

`session_creation_failed`

Reason:

`upstream_connection_failure`

Upstream:

`http://session-provider:9000/session`

Severity:

`critical`

The HTTP 503 response request ID was correlated with the backend failure log.

### T+4m - Escalation

The incident was classified as SEV-1 and prepared for L2/L3 engineering escalation.

### Recovery

The stopped `session-provider` container was restored and allowed to return to a healthy state.

No restart of the main API, Nginx, PostgreSQL or Prometheus was required.

Recovery validation:

- 10 consecutive session requests tested
- 10 returned HTTP 200
- Upstream session IDs were returned
- Main API health remained OK
- Database remained connected

After the monitoring window cleared, `HighAPI5xxRate` returned to an inactive state.

The incident was then eligible for resolution.
