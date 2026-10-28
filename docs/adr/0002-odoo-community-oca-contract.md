# ADR-0002: Odoo 19 Community, Abrechnung über OCA `contract`

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Monatliche/jährliche Abrechnung ist Kern des Produkts. Odoo Enterprise böte
`sale_subscription`; das Produkt soll aber auf Odoo **Community** laufen.

## Entscheidung

Odoo **19 Community**. Wiederkehrende Abrechnung über das OCA-Modul
**`contract`** (`contract`, `contract_sale`), als Abhängigkeit via
`oca_dependencies.txt`.

## Konsequenzen

- Keine Enterprise-Lizenz nötig; zusätzliche OCA-Repos müssen geklont werden.
- Recurring-Rechnungen kommen aus `contract.contract` (RRULE), nicht aus
  `sale.order` direkt.
- Zahlung/SEPA/etc. über Community-Payment-Provider (OCA).
