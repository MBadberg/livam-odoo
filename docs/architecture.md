# Architektur

## Zuständigkeiten

| Komponente | Rolle |
| --- | --- |
| **Odoo (diese Addons)** | Shop, Kundenkommunikation, Rechnungsstellung, Backend-UI |
| **LiVaM** | Lizenz-/Provisioning-Autorität (speichert nur Metadaten) |
| **SaaS-Laufzeit(en)** | hosten die Kundentenants (Lingavena-Runtime) |

Grundsatz: LiVaM bleibt die einzige Provisioning-/Lizenz-Autorität. Odoo vertraut
keiner Kundenangabe zur Autorisierung und ruft LiVaM über die Operator-API bzw.
den signierten Order-Webhook auf.

## Datenfluss (Kauf)

1. Kunde (B2B) legt im Shop einen `sale.order` an: Tenant-Wunschname **oder**
   eigene Domain, Zyklus (monatlich/jährlich), Features.
2. Beim Bestellabschluss ruft Odoo LiVaM `POST /webhooks/orders` auf (HMAC-signiert).
3. LiVaM prüft die Signatur, legt eine `unpaid`-Lizenz an (`tenant_ref` = Slug),
   prüft die Verfügbarkeit, wählt die SaaS-Instanz nach Auslastung und kommandiert
   die SaaS-Laufzeit (Tenant + Domain).
4. LiVaM antwortet mit `licenseId`, `tenantUrl`, initialen Zugangsdaten und
   DNS-Infos; Odoo speichert die Lizenz-ID am Auftrag und verschickt die
   Welcome-Mail (Zugangsdaten bzw. DNS-Eintrag).
5. Rechnung bezahlt (`account.move`) → Odoo ruft `mark-paid` (erste Rechnung) bzw.
   `renew` (Folgeperioden) auf.

## Datenfluss (Verwaltung)

`livam_management` spiegelt die LiVaM-Operator-API:

- Lizenzen: Liste/Detail, anlegen, mark-paid, renew, suspend/activate, Features
- Installationen: Liste, Online-Status, Zertifikat widerrufen
- Releases: Liste, activate/deactivate
- SaaS-Instanzen: Liste, Auslastung, Tenant verschieben

Jede Lizenz wird einem `res.partner` zugeordnet (Kundenbezug).

## Module & Abhängigkeiten

```
livam_connector
   ├── livam_sale              (→ sale, contract)
   │      └── website_sale_livam   (→ website_sale)
   ├── livam_management
   └── livam_mail              (→ livam_sale)
```

Siehe [integration.md](integration.md) für den exakten API-Vertrag.
