# INC002 - Simulated Incident Status Updates

These messages simulate the customer-facing communication lifecycle for a critical incident.

## 1. Investigating

We are investigating elevated errors affecting session creation.

Some requests are currently returning HTTP 503. Our technical teams are actively investigating and assessing customer impact.

Status: Investigating  
Severity: SEV-1

---

## 2. Identified

We have isolated the issue to an upstream session-provider dependency used by the session creation workflow.

The primary API remains available, but requests requiring the affected dependency may fail.

Recovery work is in progress.

Status: Identified  
Severity: SEV-1

---

## 3. Monitoring

The affected session-provider dependency has been restored.

Initial validation shows successful session creation and HTTP 200 responses.

We are continuing to monitor the service before declaring the incident fully resolved.

Status: Monitoring  
Severity: SEV-1

---

## 4. Resolved

Session creation has been fully restored.

Post-recovery validation completed successfully with 10 consecutive HTTP 200 responses, and monitoring has returned to normal.

Status: Resolved  
Severity: SEV-1
