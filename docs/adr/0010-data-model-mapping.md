# ADR-0010: Datenmodell-Mapping Odoo ↔ LiVaM

- Status: Accepted
- Datum: 2026-10-28

## Kontext

LiVaM-Ressourcen (Lizenzen, Installationen, Releases, SaaS-Instanzen) sollen im
Odoo-Backend abgebildet und einem Kunden zugeordnet werden.

## Entscheidung

- `sale.order` / `contract.contract` tragen `livam_license_id`, `tenant_slug`,
  `domain`, `billing_cycle` (monatlich/jährlich).
- Neue Modelle in `livam_management`: `livam.license`, `livam.installation`,
  `livam.release`, `livam.saas.instance` — gespiegelt aus der LiVaM-Operator-API.
- `livam.license` verweist auf `res.partner` (Kundenbezug).
- Odoo hält nur LiVaM-Metadaten, keine Tenant-Geschäftsdaten.

## Konsequenzen

- Eindeutige Zuordnung Rechnung → Lizenz → Kunde.
- Spiegelung ist read-durchgängig; Schreibaktionen rufen die LiVaM-API auf
  (keine zweite Datenhaltung mit eigener Wahrheit).
