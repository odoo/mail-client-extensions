# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'mail.message', 'path')
    # odoo/odoo@33ebc538ca240599b2f4af1f8455904d577f4186
    # all the below models `_inherit` with a different `_name` from mail.message,
    util.remove_field(cr, 'mail.mail', 'path')
    util.remove_field(cr, 'mail.compose.message', 'path')
    util.remove_field(cr, 'survey.mail.compose.message', 'path')
