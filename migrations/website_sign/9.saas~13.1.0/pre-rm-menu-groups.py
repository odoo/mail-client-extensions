# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("DELETE FROM ir_ui_menu_group_rel WHERE menu_id IN %s",
               [(util.ref(cr, 'website_sign.signature_request_template_menu'),
                 util.ref(cr, 'website_sign.signature_request_menu'),
                 )])
