# ADR-0006: Tenant-/Domain-Konzept in LiVaM

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Der Kunde gibt entweder einen **Wunschnamen** (→ Subdomain `hans.lingavena.de`)
oder eine **eigene Domain** an. Beides muss eindeutig und prüfbar sein.

## Entscheidung

- LiVaM bekommt ein Tenant-/Domain-Konzept: Order-Webhook nimmt `tenantSlug`
  **oder** `domain` entgegen (genau eines Pflicht).
- Zentrale **Slug-/Domain-Registry** (additive Migration) erzwingt Eindeutigkeit.
- Neuer Endpoint `POST /tenants/check-availability` für den Shop-Check.
- `SaaSProvisioner.provision()` erhält Slug/Domain und liefert `tenantUrl`,
  Zugangsdaten und DNS-Infos zurück.

## Konsequenzen

- LiVaM braucht eine neue Tabelle + Migration (additiv, reversibel).
- Verfügbarkeits-Check läuft zentral in LiVaM (nicht in Odoo).
- Eigene Domain → DNS-Anweisung; Wunschname → Subdomain-Automatik.
