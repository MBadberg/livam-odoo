# ADR-0007: Multi-SaaS-Instanz, Platzierung, Move

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Aktuell gibt es eine SaaS-Instanz. Künftig mehrere; Tenants sollen nach
Auslastung automatisch platziert und später zwischen Instanzen verschoben
werden können.

## Entscheidung

- LiVaM bekommt eine **`saas_instances`-Registry** (Name, `base_url`,
  mTLS-Identität, Kapazität/Auslastung, Status `active|draining|offline`).
- `SaaSProvisioner` wird zum **Pool** (eine `RealSaaSProvisioner`-Instanz pro
  SaaS-Instanz); **Platzierungs-Policy** wählt die Instanz nach Auslastung
  (erst Round-Robin, dann auslastungsbasiert).
- **Move**: `POST /licenses/:id/move { targetInstanceId }` → LiVaM kommandiert
  Quell-/Ziel-Laufzeit und aktualisiert `licenses.saas_instance_ref`.
- Operator-Endpoints `GET/POST /saas-instances`; Move ist in LiVaM **und** Odoo
  (`livam_management`) ausführbar.

## Konsequenzen

- Neue Tabelle + Provisioner-Refactoring; Move ist ein mehrstufiger Vorgang
  (Zustandsmaschine, Idempotenz, Rollback).
- Die SaaS-Laufzeit braucht eine Move-/Migrate-API.
