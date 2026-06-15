# Acme Cloud — Product Handbook

Acme Cloud is a hosted platform for running background jobs and scheduled tasks.
This handbook is sample content so you can try rag-starter out of the box. Replace
the `data/` folder with your own documents and re-ingest.

## Plans

Acme Cloud offers three plans:

- **Starter** — $0/month. Up to 100 job runs per month, 1 concurrent worker,
  community support only. Intended for evaluation and hobby projects.
- **Pro** — $29/month. Up to 50,000 job runs per month, 5 concurrent workers,
  email support with a 24-hour response target.
- **Business** — $199/month. Unlimited job runs, 25 concurrent workers, priority
  support with a 4-hour response target during business hours, and a 99.9% uptime SLA.

All paid plans include the full API, scheduled tasks, and webhook notifications.
Support is included in every plan; only the response target differs.

## Resetting your password

To reset your password:

1. Go to the sign-in page and click **Forgot password**.
2. Enter the email address on your account. A reset link is emailed within a few minutes.
3. The reset link is valid for 30 minutes. If it expires, request a new one.
4. Choose a new password of at least 12 characters.

If you do not receive the email, check spam, then contact support. Password resets
never require contacting support unless your email itself is inaccessible.

## Security

Acme Cloud encrypts all data at rest with AES-256 and in transit with TLS 1.2+.
Two-factor authentication (2FA) is available on all plans and is strongly recommended.
API keys can be rotated at any time from the dashboard; rotating a key immediately
invalidates the previous one.
