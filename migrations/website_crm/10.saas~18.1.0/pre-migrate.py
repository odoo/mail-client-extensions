# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    view_id = util.rename_xmlid(cr, *eb('website_crm.conctactus_thanks{,_ir_ui_view}'))
    if view_id:
        cr.execute("""
            INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
                 SELECT 'website_crm', 'contactus_thanks', 'website.page', id, false
                   FROM website_page
                  WHERE view_id = %s
        """, [view_id])
