# Customer Update - Acme Gaming

Hi Acme Gaming team,

We investigated the provider session issue and identified an integration configuration problem.

The provider callback setting had been disabled, which caused session requests to return HTTP 403.

We verified the configuration in both the administrative back office and the underlying database, restored the callback setting, and retested the integration.

Post-resolution validation completed successfully with five consecutive provider sessions returning HTTP 200.

The integration is now operating normally.

Regards,

Technical Support Engineering
