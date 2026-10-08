# INC003 - Investigation

## Initial Validation

The provider session workflow was healthy before the incident.

Baseline:

`POST /api/v1/provider/session`

Result:

`HTTP 200 OK`

## Failure Reproduction

After the integration configuration changed, the same workflow returned:

`HTTP 403`

Response:

`integration_error`

Message:

`Provider callback is disabled`

## Back-Office Investigation

The Provider Integration Back Office was reviewed.

Provider:

`Demo Gaming Provider`

Provider ID:

`provider_demo_001`

Region:

`EU`

Observed configuration:

`callback_enabled: false`

## Database Validation

The configuration was independently verified in PostgreSQL.

Observed state:

`callback_enabled = false`

This confirmed that the failure was caused by persisted integration configuration rather than a frontend display issue.

## Application Log Evidence

Backend logs recorded the provider session failure with the corresponding request ID.

Event:

`provider_session_failed`

Reason:

`callback_disabled`

## Root Cause

The provider callback was disabled in the integration configuration.

The API, database, Nginx, and provider-session service remained operational.

The problem was therefore an integration configuration issue rather than a platform outage.
