# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xids = {
        'view_order_product_graph': 'view_order_product_pivot',
        'crm_case_section_salesteams_view_form': 'crm_team_salesteams_view_form',
        'crm_case_section_salesteams_view_kanban': 'crm_team_salesteams_view_kanban',
    }
    for f, t in xids.items():
        res_id = util.rename_xmlid(cr, 'sale.' + f, 'sale.' + t)

        if res_id and t == 'view_order_product_pivot':
            cr.execute("UPDATE ir_ui_view SET type = %s WHERE id = %s",
                       ('pivot', res_id))

    if util.module_installed(cr, 'sale_crm'):
        util.rename_xmlid(cr, 'sale.res_partner_address_type', 'sale_crm.res_partner_address_type')
    else:
        util.remove_view(cr, 'sale.res_partner_address_type')
