# Beitragen zu livam-odoo

Dieses Repo folgt den
[OCA Contribution Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
sowie den Regeln des LiVaM-Workspaces (`AGENTS.md` im Schwester-Repo `livam`).

## Branch-Workflow

- Entwicklung läuft auf `beta`. `main` ist die stabile Linie und erhält nur
  Merges aus `beta` (oder `release/*`/`hotfix/*`).
- Jeder Merge nach `main` erfordert vorher einen SemVer-Bump
  (`chore(release): bump version to X.Y.Z`) auf `beta`.
- Arbeit nie uncommitted lassen; pro logischem Schritt committen.

## Modul-Konventionen (OCA)

- Module: Kleinbuchstaben, snake_case; `__manifest__.py` mit
  `"version": "19.0.x.y.z"`, `"license": "AGPL-3"`, `summary`, `author`, `website`.
- Standard-Ordner: `models/`, `views/`, `controllers/`, `data/`, `security/`,
  `tests/`, `wizards/`, `static/`, `i18n/`.
- `README.rst` pro Modul via `oca-gen-addon-readme` (Fragmente in `readme/`).
- xml_id-Namenskonvention `<modul>.<modell>`; Views `<modell>_view_<name>`.
- Kein SQL-Injection, kein `cr.commit`, kein ORM-Bypass.
- Tests mit minimalen Rechten, ohne externe Service-Aufrufe, ohne dynamische Daten.

## Quality Gates

```bash
pre-commit run --all-files
```

Vollständige Odoo-Test-CI (OCA MQT) kommt mit dem Modul-Scaffolding.

## Commit-Messages

OCA-Stil: `[IMP] livam_sale: ...`, `[FIX] ...`, `[ADD] ...`, `[MIG] ...`.
