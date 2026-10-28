# ADR-0008: Rechnung → Lizenz-Sync

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Sobald die Odoo-Rechnung bezahlt ist, muss die Lizenz in LiVaM auf „bezahlt"
(erste Periode) bzw. verlängert (Folgeperioden) gesetzt werden.

## Entscheidung

- Beim Bestellabschluss speichert Odoo die LiVaM-**Lizenz-ID** am `sale.order`.
- Erste bezahlte Rechnung → `POST /licenses/:id/mark-paid`.
- Jede weitere bezahlte Rechnung → `POST /licenses/:id/renew` (`days` = 30/365).
- LiVaM läuft mit `autoRenew: false`; **Odoo/`contract` ist Verlängerungs-Autorität**.

## Konsequenzen

- LiVaMs eigener Auto-Renew-Scheduler wird für Shop-Lizenzen nicht aktiv.
- Trigger idempotent umsetzen (Rechnungsstatus-Übergang, Cron-Nachzügler).
- Klare Zuordnung `account.move` ↔ Lizenz über den Vertrag/Auftrag.
