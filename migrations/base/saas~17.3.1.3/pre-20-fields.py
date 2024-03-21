from odoo.upgrade import util

SMTP_MESSAGE = """\
The following Outgoing Mail Servers (`ir.mail_server`) were configured \
to share certificates on an insecure connection. The system behavior \
in that case was to ignore the certificates and to connect using an \
empty password scheme. To reflect what the system was actually doing, \
the following changes have been applied on those records:
* smtp_authentication='login'
* smtp_user=None
* smtp_pass=None
Impacted records:
- {}
Please review those records to make sure the configuration is valid."""


def migrate(cr, version):
    cr.execute("UPDATE ir_cron SET active = false WHERE numbercall = 0 AND active")
    util.remove_field(cr, "ir.cron", "doall")
    util.remove_field(cr, "ir.cron", "numbercall")

    cr.execute(
        """
           UPDATE ir_mail_server
              SET smtp_authentication = 'login',
                  smtp_user = null,
                  smtp_pass = null
            WHERE smtp_authentication = 'certificate'
              AND smtp_encryption = 'none'
        RETURNING id, name
    """
    )
    rows = cr.dictfetchall()
    if rows:
        util.add_to_migration_reports(
            SMTP_MESSAGE.format(
                "\n- ".join(util.get_anchor_link_to_record("ir.mail_server", row["id"], row["name"]) for row in rows)
            ),
            format="md",
        )
