# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xids = {
        'view_order_product_graph': 'view_order_product_pivot',
        'crm_case_section_salesteams_view_form': 'crm_team_salesteams_view_form',
        'crm_case_section_salesteams_view_kanban': 'crm_team_salesteams_view_kanban',
    }
    for f, t in xids.items():
        util.rename_xmlid(cr, 'sale.' + f, 'sale.' + t)

    if util.module_installed(cr, 'sale_crm'):
        util.rename_xmlid(cr, 'sale.res_partner_address_type', 'sale_crm.res_partner_address_type')
    else:
        util.remove_view(cr, 'sale.res_partner_address_type')
