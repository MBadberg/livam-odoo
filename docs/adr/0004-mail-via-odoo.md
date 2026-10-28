# ADR-0004: E-Mail-Kommunikation über Odoo

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Nach dem Provisionieren braucht der Kunde Zugangsdaten bzw. eine DNS-Anweisung.
LiVaM hat keine Mail-Infrastruktur und kennt keine Kundendaten.

## Entscheidung

**Odoo verschickt** alle Kunden-Mails (Willkommen/Zugangsdaten, DNS-Eintrag).
LiVaM liefert im Order-Webhook-Response nur `tenantUrl`, initiale Zugangsdaten
und DNS-Infos zurück.

## Konsequenzen

- Odoo hält Mail-Templates + Kundendaten an einer Stelle.
- LiVaM muss Zugangsdaten/DNS im Provisioning-Ergebnis durchreichen
  (Erweiterung `SaaSProvisioner`).
- Passwort wird nicht persistiert und nur einmalig übertragen.
