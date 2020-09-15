# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'sales_team.menu_sales', 'crm.crm_menu_pipeline')
    # The `menu_id` of `crm.planner_crm` gets changed in
    # odoo/odoo@ea66192276921be1bafe73255fa77c55f3e10ac7
    # The former menu `sales_team.menu_base_partner` is deleted in the same commit
    # As the field `menu_id` of `web.planner` is required,
    # it's important it gets setted with the new menu
    # before `sales_team.menu_base_partner` gets deleted
    util.force_noupdate(cr, 'crm.planner_crm', False)
