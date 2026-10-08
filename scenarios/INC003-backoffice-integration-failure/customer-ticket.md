# INC003 - Provider Integration Failure

## Customer

Acme Gaming

## Reported Problem

The customer reports that provider sessions can no longer be created.

The provider integration previously worked normally.

## Customer Impact

Users attempting to start a provider session receive an integration failure.

## Affected Workflow

`POST /api/v1/provider/session`

## Support Goal

Determine whether the failure is caused by:

- provider availability
- API failure
- application defect
- integration configuration
- regional configuration
- back-office settings
