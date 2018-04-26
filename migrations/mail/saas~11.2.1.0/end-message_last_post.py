# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("SELECT model FROM ir_model WHERE is_mail_thread = true")
    for model, in cr.fetchall():
        util.remove_field(cr, model, 'message_last_post')
