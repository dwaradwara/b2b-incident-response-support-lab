# Incident Severity Matrix

## SEV-1 - Critical

Examples:

- Business-critical customer workflow unavailable
- Platform-wide or multi-customer outage
- Sustained 5xx responses preventing core operations
- Immediate SLA risk

Target response:

- Initial triage: within 5 minutes
- Engineering escalation: immediate
- Client update cadence: every 15 minutes
- Incident coordination continues until recovery is validated

## SEV-2 - Major

Examples:

- Major feature degradation
- Significant performance issue
- Partial customer impact with workaround available

Target response:

- Initial triage: within 15 minutes
- Client update cadence: every 30 minutes

## SEV-3 - Standard

Examples:

- Individual customer issue
- Configuration issue
- Non-critical feature problem

Target response:

- Standard support workflow
