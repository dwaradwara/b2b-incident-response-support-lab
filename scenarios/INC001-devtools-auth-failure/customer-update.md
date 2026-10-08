# Customer Update - Acme Gaming

Hi Acme Gaming team,

We reproduced the account access issue and identified the cause.

The account API request was reaching the platform successfully, but the request was rejected with HTTP 401 because the access token was invalid or expired.

We validated the issue using the browser request details and correlated the request ID with the backend logs.

After testing with a valid token, the account request completed successfully with HTTP 200 and the account data loaded normally.

No platform outage was identified.

Regards,

Technical Support Engineering
