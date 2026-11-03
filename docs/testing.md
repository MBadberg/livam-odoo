# Testing & End-to-End

## Quality gates

| Gate | Befehl |
| --- | --- |
| Pre-commit (ruff, ruff-format, XML/JSON/YAML) | `pre-commit run --all-files` |
| Odoo-Tests | `oca_run_tests` (CI `.github/workflows/ci.yml`, OCA oca-ci image) |
| LiVaM | `corepack pnpm lint && corepack pnpm test && corepack pnpm build` |

Alle drei laufen im CI-Workflow bzw. im Schwester-Repo `../livam`.

## End-to-End gegen den Odoo-Produktivserver (192.168.120.6)

Voraussetzungen:

- SSH-Zugang als `odoo` auf `192.168.120.6` (M0, noch offen).
- LiVaM-Produktivinstanz erreichbar (Base URL, Operator-Token, Webhook-Secret).
- Module `livam_connector`, `livam_sale`, `website_sale_livam` und
  `livam_management` installiert.

Kritischer Pfad (manuell, idempotent wiederholbar):

1. **Verbindung**: Unter *Einstellungen → LiVaM* Base URL, Operator-Token und
   Webhook-Secret setzen.
2. **Spiegelung**: `livam_management` → *Synchronisieren*; Lizenzen,
   Installationen, Releases und SaaS-Instanzen erscheinen aus LiVaM.
3. **Kauf**: Im Shop eine Bestellung mit Tenant-Wunschname/Zyklus abschließen →
   Lizenz wird in LiVaM angelegt und der Tenant provisioniert.
4. **Zahlung**: Rechnung als bezahlt markieren → `mark-paid`/`renew` greift;
   die Lizenz wird in LiVaM „paid" bzw. verlängert.
5. **Verwaltung**: In `livam_management` Lizenz verschieben, Features ändern,
   Zertifikat widerrufen → jede Aktion ist anschließend in LiVaM sichtbar.

Abnahmekriterium: Jeder Schritt ist wiederholbar und in LiVaM verifizierbar;
keine Secrets im Log.
