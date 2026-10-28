# ADR-0001: Eigenes öffentliches Repo `livam-odoo`

- Status: Accepted
- Datum: 2026-10-28

## Kontext

Das Odoo-Addon ist funktional getrennt vom LiVaM-Backend (TypeScript/Node).
Beide Komponenten haben eigene Build-/Test-/Release-Zyklen und eigene
Zielsysteme (Odoo vs. Node).

## Entscheidung

Die Odoo-Addons leben in einem **eigenen öffentlichen GitHub-Repo
`livam-odoo`** (AGPL-3.0, OCA-konform) — nicht im LiVaM-Monorepo. Im Workspace
wird es als Schwester-Ordner `/config/workspace/livam-odoo` integriert.

## Konsequenzen

- Klare Trennung von Zuständigkeiten und CI.
- OCA-fähige Struktur (Module, `oca_dependencies.txt`, Pre-Commit) möglich.
- Zwei Repos müssen versioniert und release-mäßig koordiniert werden.
