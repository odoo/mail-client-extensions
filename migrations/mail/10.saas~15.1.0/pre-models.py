# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.module_installed(cr, 'web_studio'):
        util.move_field_to_module(cr, 'ir.model', 'mail_thread', 'web_studio', 'mail')
        util.rename_field(cr, 'ir.model', 'mail_thread', 'is_mail_thread')
        util.move_field_to_module(cr, 'ir.model.fields', 'track_visibility', 'web_studio', 'mail')

    util.create_column(cr, 'res_users', 'notification_type', 'varchar')
    cr.execute("""
        UPDATE res_users u
           SET notification_type = CASE WHEN p.notify_email = 'none' THEN 'inbox' ELSE 'email' END
          FROM res_partner p
         WHERE p.id = u.partner_id
    """)
    util.remove_field(cr, 'res.partner', 'notify_email')
