# Remaining real screenshot evidence

API evidence is collected; the following screenshots have not been captured.
Computer Use stopped because it could not verify Chrome's current URL confidently
enough to enforce its policy. No further browser control was attempted afterward.
No screenshots have been fabricated.

1. In Google Cloud Console choose project **file-security-scanner**, Monitoring,
   Dashboards, **AI File Security Scanner - Milestone 6 Observability**. Open the
   dashboard whose ID is `014b4b60-8667-45b8-8445-e7e736abae7e`.
2. Select a custom time range covering **November 1, 2026, 4:45-5:15 PM Central**
   (22:45-23:15 UTC). Capture the HTTP 5xx count chart with its single controlled
   event, CPU chart and memory chart. Save under `evidence/dashboard/`.
3. Monitoring, Alerting: open **AI File Security Scanner - HTTP 5xx Alert**,
   policy ID `3124806542354479175`. Capture the condition and channel with private
   details redacted. Save under `evidence/alerting/`.
4. Open incident `0.oeimw7fsr668`, which opened at **4:58:38 PM Central**.
   Capture the policy, incident state and timestamp.
5. Capture the received notification from the authorized recipient's inbox.
   The recipient confirmed receipt in this conversation. Redact unrelated inbox
   messages, personal information and private addresses before committing.

The receipt confirmation and actual incident API response are already saved as
`alerting/received-confirmation.json` and `alerting/incident.json`; they do not
substitute for the assignment's explicitly required screenshot artifacts.
