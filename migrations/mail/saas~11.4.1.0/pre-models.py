# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mail_message", "moderation_status", "varchar")
    # moderation_status can be kept NULL.
    util.create_column(cr, "mail_message", "add_sign", "boolean")
    # cr.execute("UPDATE mail_message SET add_sign=true")

    util.create_column(cr, "mail_message_res_partner_needaction_rel", "failure_type", "varchar")
    util.create_column(cr, "mail_message_res_partner_needaction_rel", "failure_reason", "text")

    cr.execute("UPDATE mail_message_res_partner_needaction_rel SET failure_type='UNKNOWN' WHERE email_status = 'exception'")
    cr.execute("UPDATE mail_message_res_partner_needaction_rel SET failure_type='BOUNCE' WHERE email_status = 'bounce'")
