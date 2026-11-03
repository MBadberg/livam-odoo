Use the *LiVaM* menu:

* *Synchronisieren* mirrors the complete LiVaM operator view (licenses,
  installations, releases and SaaS instances).
* *Lizenzen*, *Installationen*, *Releases* and *SaaS-Instanzen* list the
  mirrored records; each form offers the matching write action.
* *SaaS-Instanz registrieren* creates a new SaaS instance in LiVaM.

Mirroring is read-through: Odoo stores only LiVaM metadata; every write action
calls the LiVaM operator API and then re-syncs the record.
