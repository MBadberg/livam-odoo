Mirror LiVaM licenses, installations, releases and SaaS instances into the
Odoo backend and link each license to a customer (``res.partner``). Write
actions (mark-paid, renew, suspend/activate, feature changes, tenant move,
certificate revocation, release activation) call the LiVaM operator API and
then re-sync the record.
