# SMTP Relay → GC Notify

This container accepts SMTP mail on `$SMTP_PORT` (default 2525) from **private IPs only** and relays each recipient as a separate **GC Notify** email using a single template.

## Configure

Required:
- `NOTIFY_API_KEY` – create in GC Notify.
- `NOTIFY_TEMPLATE_ID` – the template must include `((subject))` and `((body))` placeholders.

Optional:
- `NOTIFY_BASE_URL` (default `https://api.notification.canada.ca`)
- `RECIPIENT_ALLOW_DOMAINS` – comma‐separated list (e.g. `ssc-spc.gc.ca,canada.ca`)
- `RECIPIENT_ALLOW_REGEX` – full regex; if set, overrides `RECIPIENT_ALLOW_DOMAINS`
- `SLACK_WEBHOOK_URL` – mirror subject/body to a webhook (fire‐and‐forget)
- `MAX_BODY_CHARS` – truncate body defensively (default 20000)

## Notes

- GC Notify rate limits: ~1,000 API requests/min per key type. This relay backs off/retries on 429/5xx.  
- Use test keys and simulator addresses to exercise success/failure paths without sending mail:
  - `temp-fail@simulator.notify` → `temporary-failure`
  - `perm-fail@simulator.notify` → `permanent-failure`
  - Any other valid address with a **test** key → `delivered` (simulated)  
- Attachments: GC Notify can send up to **10 files** per email (total ≤ **6 MB**) with malware scanning. To support attachments, add template placeholders and map MIME parts to per-file personalisation (future enhancement).
