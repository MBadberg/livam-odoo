# Roadmap — Lingavena-Lizenz-SaaS (Odoo ↔ LiVaM)

Legende: ☐ offen · ◐ in Arbeit · ☑ erledigt

## M0 — Setup & Dokumentation

- ☑ ADR-Set, Roadmap, Architektur-, Integrations-, Sicherheits- und Rechts-Doku
- ◐ Öffentliches GitHub-Repo `livam-odoo` (AGPL-3.0) + CI (pre-commit)
- ◐ SSH-Zugang zum Odoo-Server (Key für den `odoo`-Benutzer)

## M1 — LiVaM: Tenant-/Domain-Konzept

- ☑ Order-Webhook-Payload erweitern (`tenantSlug`, `domain`, `customerEmail`,
  `customerName`, `billingCycle`)
- ☑ Slug-/Domain-Registry + Verfügbarkeits-Endpoint `POST /tenants/check-availability`
- ☑ `SaaSProvisioner` um Slug/Domain erweitern; Rückgabe `tenantUrl`/Zugangsdaten/DNS
- ☑ Unit- + Negativtests

## M2 — LiVaM: Multi-SaaS-Instanz

- ☐ `saas_instances`-Registry (mTLS-Identität, Kapazität/Auslastung, Status)
- ☐ Automatische Platzierung nach Auslastung
- ☐ Tenant-Verschieben `POST /licenses/:id/move`
- ☐ Operator-Endpoints `GET/POST /saas-instances`

## M3 — Odoo: `livam_connector`

- ☐ REST-Client, Settings, HMAC-Signierung, Fehlerbehandlung, Tests

## M4 — Odoo: `livam_sale`

- ☐ Order-Webhook bei Bestellabschluss, Lizenz-ID am `sale.order`
- ☐ OCA-`contract`-Erzeugung (monatlich/jährlich)
- ☐ `mark-paid` (erste Rechnung) / `renew` (Folgeperioden)
- ☐ Tenant-/Domain-Felder + Verfügbarkeits-Check

## M5 — Odoo: `website_sale_livam`

- ☐ Shop-Frontend: Tenant-Wunschname oder eigene Domain, Zyklus-Auswahl, Bestätigung

## M6 — Odoo: `livam_management`

- ☐ Backend-Spiegelung: Lizenzen, Installationen, Releases, SaaS-Instanzen
- ☐ Tenant-Verschieben + direkte Kunden-/Partner-Zuordnung

## M7 — Härtung & Integrationstest

- ☐ Quality Gates (pre-commit, Odoo-Tests, LiVaM `pnpm lint/test/build`)
- ☐ End-to-End gegen den Odoo-Produktivserver (192.168.120.6)
