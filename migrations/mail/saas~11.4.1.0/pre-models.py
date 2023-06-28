# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mail_message", "moderation_status", "varchar")
    # moderation_status can be kept NULL.
    util.create_column(cr, "mail_message", "add_sign", "boolean")
    # cr.execute("UPDATE mail_message SET add_sign=true")

    util.create_column(cr, "mail_message_res_partner_needaction_rel", "failure_type", "varchar")
    util.create_column(cr, "mail_message_res_partner_needaction_rel", "failure_reason", "text")

    query = "UPDATE mail_message_res_partner_needaction_rel SET failure_type = %s WHERE email_status = %s AND failure_type != %s"

    util.parallel_execute(
        cr,
        [
            *util.explode_query_range(
                cr,
                cr.mogrify(query, ["UNKNOWN", "exception", "UNKNOWN"]).decode(),
                table="mail_message_res_partner_needaction_rel",
            ),
            *util.explode_query_range(
                cr,
                cr.mogrify(query, ["BOUNCE", "bounce", "BOUNCE"]).decode(),
                table="mail_message_res_partner_needaction_rel",
            ),
        ],
    )
