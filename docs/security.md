# Sicherheit

- **Keine Secrets im Code/Logs.** Operator-Token und Webhook-Secret liegen in
  Odoo-`ir.config_parameter` (nicht exportiert) bzw. als Umgebungsvariablen;
  niemals loggen.
- **Webhook-Signatur**: HMAC-SHA256 über den rohen Request-Body, konstantzeitiger
  Vergleich; ungültige Signatur → Abbruch (fail closed).
- **Operator-API**: Bearer-Token, konstantzeitiger Vergleich, leeres Token → fail closed.
- **Keine Kundenautorität**: Ein kundenseitig übergebener Tenant-/Lizenz-Identifier
  wird nie zur Autorisierung verwendet (LiVaM leitet Identität aus der
  Installation bzw. dem signierten Webhook ab).
- **TLS**: Odoo → LiVaM ausschließlich über HTTPS (gültige Zertifikate, keine
  Verifikation deaktivieren).
- **Datenminimierung**: Odoo hält nur das Minimum an LiVaM-Metadaten
  (Lizenz-ID, `tenant_ref`, `saas_instance_ref`, URL). Tenant-Geschäftsdaten
  bleiben in der SaaS-Laufzeit.
- **Zugangsdaten**: Das initiale Passwort wird nur einmalig (in der
  Willkommens-Mail) übertragen und nirgends persistiert; der Kunde setzt es beim
  ersten Login zurück.
