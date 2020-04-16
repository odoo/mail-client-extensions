# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("SELECT model FROM ir_model WHERE is_mail_thread = true")
    for model, in cr.fetchall():
        util.remove_field(cr, model, 'message_last_post')
    util.remove_field(cr, 'res.users', 'message_last_post', drop_column=False)
    util.update_field_references(cr, 'message_last_post', 'write_date')
