# ADR-0005: Zuständigkeiten & Authentifizierung

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Zwei Systeme müssen zusammenarbeiten, ohne dass Kundeneingaben zur
Autorisierung werden.

## Entscheidung

- **LiVaM** bleibt Lizenz-/Provisioning-Autorität (Metadaten only).
- **Odoo** ist Shop, Kundenkommunikation, Rechnungsstellung und Management-UI.
- Kommunikation Odoo → LiVaM:
  - Order-Webhook `POST /webhooks/orders` mit **HMAC-SHA256** (`X-Webhook-Signature`).
  - Operator-API mit **Bearer** `LIVAM_OPERATOR_TOKEN`.
- Nie eine kundenseitige Tenant-/Lizenz-ID als Autorisierung verwenden.

## Konsequenzen

- Fail-closed bei leerem/falschem Token, konstantzeitige Vergleiche.
- Der Shop braucht nur das Webhook-Secret; die Operator-API nur das Backend.
- LiVaM bleibt die einzige Stelle, die Provisionierung anstößt.
