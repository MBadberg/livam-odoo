# ADR-0009: Modulaufteilung

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Funktionen reichen von Shop über Abrechnung bis zur Verwaltung; OCA bevorzugt
kleine, fokussierte Module.

## Entscheidung

Fünf Module:

- `livam_connector` — LiVaM-REST-Client, Settings, HMAC-Signierung (Basis).
- `livam_sale` — Order-Webhook, `contract`-Erzeugung, mark-paid/renew.
- `website_sale_livam` — Shop-Frontend.
- `livam_management` — Backend-Spiegelung + Kundenbezug.
- `livam_mail` — E-Mail-Vorlagen (Zugangsdaten, DNS).

## Konsequenzen

- Klare Abhängigkeitskette (`connector` als Fundament).
- Shop, Backend und Mail unabhängig installier-/testbar.
- Mehr Module = mehr `__manifest__.py`-Pflege, aber bessere Wiederverwendbarkeit.
