# INC003 - Resolution

## Resolution

The provider callback setting was restored through the administrative back-office workflow.

Configuration changed from:

`callback_enabled = false`

to:

`callback_enabled = true`

## Validation

The provider session workflow was retested after remediation.

Result:

- 5 consecutive requests tested
- 5 successful requests
- HTTP status: 200
- Provider session creation restored

The final PostgreSQL configuration also confirmed that the callback was enabled.

## Result

The integration returned to normal operation.

No application restart or infrastructure remediation was required.
