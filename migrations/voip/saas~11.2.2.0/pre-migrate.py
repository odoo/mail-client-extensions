# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE mail_activity_type SET category='phonecall' WHERE create_voip_phonecall=true")

    util.remove_field(cr, 'mail.activity.type', 'create_voip_phonecall')
    util.remove_field(cr, 'mail.activity', 'is_call_type')

    util.remove_view(cr, 'voip.mail_activity_type_view_form_inherit')
