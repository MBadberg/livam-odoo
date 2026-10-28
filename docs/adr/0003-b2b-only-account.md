# ADR-0003: B2B-only, verpflichtendes Kundenkonto

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Zielgruppe sind Logopädie-Praxen, Selbstständige/Freiberufler — also
Unternehmer (B2B). Ein Kundenkonto ist für SaaS-Zugang und wiederkehrende
Abrechnung sachlich erforderlich.

## Entscheidung

Nur B2B; **verpflichtendes Kundenkonto**, keine Gastbestellung. Verbraucher-
spezifische Pflichten (Widerrufsrecht, Kündigungsbutton, Button-Lösung) entfallen.

## Konsequenzen

- Einfachere Rechtslage; Fokus auf USt-korrekte Rechnungen (Reverse-Charge,
  § 13b UStG) und Impressum/DSGVO/AGB.
- Kein Gast-Checkout nötig; Account = Shop-Login + Tenant-Login-Ziel.
