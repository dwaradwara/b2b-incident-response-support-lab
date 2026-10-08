# INC001 - Investigation

## Browser DevTools

The issue was reproduced in Chrome using the Network panel.

Request:

`GET /api/v1/account`

Observed status:

`401 Unauthorized`

The request used an expired/invalid bearer token.

## Request Correlation

Response request ID:

`ffb6dc9ef0f3a35ad80b3b579c0cbc18`

The same request ID was found in application logs.

Backend evidence:

`authentication_failed`

Reason:

`invalid_or_expired_token`

The API itself remained available and responsive.

## Validation

The same account request was repeated with a valid token.

Result:

`HTTP 200 OK`

The account payload was returned successfully.

## Root Cause

The failure was caused by an invalid or expired bearer token, not by an API outage or backend service failure.
