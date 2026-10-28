# Integration (API-Vertrag Odoo ↔ LiVaM)

Alle Aufrufe erfolgen von Odoo zu LiVaM. Authentifizierung:

- **Order-Webhook**: HMAC-SHA256 (`X-Webhook-Signature: sha256=<hex>`) über den
  rohen Body, Secret `LIVAM_ORDER_WEBHOOK_SECRET`.
- **Operator-API**: `Authorization: Bearer <LIVAM_OPERATOR_TOKEN>`.

## Order-Webhook (Kauf)

`POST /webhooks/orders` (erweitert gegenüber heutigem Stand):

```json
{
  "orderId": "SO00042",
  "licenseType": "subscription",
  "features": ["WEBSITE_BUILDER", "BILLING"],
  "maxInstances": 1,
  "autoRenew": false,
  "tenantSlug": "hans",
  "domain": null,
  "customerEmail": "hans@praxis.de",
  "customerName": "Hans Praxis",
  "billingCycle": "monthly",
  "endsAt": "2026-11-28T00:00:00Z"
}
```

`tenantSlug` (Wunschname) und `domain` (eigene Domain) schließen sich gegenseitig
aus; genau eines ist Pflicht.

Antwort `201`:

```json
{
  "license": {
    "id": "lic_...",
    "tenantRef": "hans",
    "saasInstanceRef": "inst_1",
    "provisioningStatus": "running"
  },
  "tenantUrl": "https://hans.lingavena.de",
  "credentials": { "username": "admin", "password": "..." },
  "dnsRecords": [
    { "type": "CNAME", "name": "praxis-muster.de", "value": "cname.lingavena.de" }
  ]
}
```

## Verfügbarkeitsprüfung

`POST /tenants/check-availability` (Operator- oder Webhook-Auth):

```json
{ "tenantSlug": "hans" }
```

→ `{ "available": true }` / `{ "available": false, "reason": "taken" }`

## Operator-API (Verwaltung, wird von `livam_management` genutzt)

| Endpoint | Aktion |
| --- | --- |
| `GET /licenses` / `POST /licenses` | Liste / anlegen |
| `GET /licenses/:id` | Detail |
| `POST /licenses/:id/mark-paid` | Zahlung bestätigen |
| `POST /licenses/:id/renew` | Laufzeit verlängern (`days`) |
| `POST /licenses/:id/suspend` / `activate` | Statuswechsel |
| `POST /licenses/:id/features` | Features ersetzen |
| `GET /installations` / `GET /installations/:id` | Installationen |
| `POST /installations/:id/revoke-certificate` | Zertifikat widerrufen |
| `GET /releases`, `POST /releases/:id/activate|deactivate` | Releases |
| `GET/POST /saas-instances` | SaaS-Instanzen (neu, M2) |
| `POST /licenses/:id/move` | Tenant verschieben (neu, M2) |

## Zuordnung Rechnung → Lizenz

| Ereignis | Aufruf |
| --- | --- |
| Erste Rechnung bezahlt | `POST /licenses/:id/mark-paid` |
| Jede weitere Rechnung bezahlt | `POST /licenses/:id/renew` (`days` = 30 bzw. 365) |

LiVaM läuft mit `autoRenew: false`; Odoo/`contract` ist die Verlängerungs-Autorität.
