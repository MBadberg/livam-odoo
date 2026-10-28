# LiVaM Odoo-Addons

Odoo-Integration für [LiVaM](../livam) — die Lizenz- und Update-Verwaltungsebene
für [Lingavena](https://github.com/MBadberg/lingavena). Diese Addon-Suite

- verkauft die **Lingavena Lizenz SaaS** über den Odoo-Webshop,
- provisioniert bei Kauf über LiVaM einen neuen Tenant auf einer SaaS-Instanz,
- verschickt die Zugangsdaten (bzw. DNS-Anweisungen) per E-Mail über Odoo,
- bildet monatliche/jährliche Abrechnung über OCA `contract` ab und
- spiegelt die komplette LiVaM-Verwaltung (Lizenzen, Installationen, Releases,
  SaaS-Instanzen) inkl. Kundenzuordnung ins Odoo-Backend.

## Rahmen

- **Odoo 19 Community** (kein Enterprise; Abonnements via OCA `contract`)
- **B2B-only** (Logopädie-Praxen, Selbstständige/Freiberufler)
- **AGPL-3.0**, OCA-konform

## Module

| Modul | Zweck |
| --- | --- |
| `livam_connector` | LiVaM-REST-Client, Konfiguration, HMAC-Signierung |
| `livam_sale` | Verkauf + Vertrag, Order-Webhook, `mark-paid`/`renew` |
| `website_sale_livam` | Shop-Frontend (Tenant-Name / eigene Domain, Zyklus-Auswahl) |
| `livam_management` | Backend-Spiegelung der LiVaM-Verwaltung mit Kundenbezug |
| `livam_mail` | E-Mail-Vorlagen (Zugangsdaten, DNS-Eintrag) |

## Dokumentation

- [Roadmap](docs/roadmap.md)
- [Architektur](docs/architecture.md)
- [Integration (API-Vertrag)](docs/integration.md)
- [Sicherheit](docs/security.md)
- [Rechtliches (B2B)](docs/legal.md)
- [Architecture Decision Records](docs/adr/index.md)

## Entwicklung

```bash
pre-commit install
```

Voraussetzungen: Odoo 19 Community + OCA-`contract` (siehe `oca_dependencies.txt`).

## Lizenz

AGPL-3.0 — siehe [LICENSE](LICENSE).
