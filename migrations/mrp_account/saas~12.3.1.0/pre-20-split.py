# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.move_model(cr, 'report.mrp_account.mrp_cost_structure', 'mrp_account', 'mrp_account_enterprise')
    util.move_model(cr, 'report.mrp_account.product_template_cost_structure', 'mrp_account', 'mrp_account_enterprise')
    util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.mrp_cost_structure"))
    util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.product_template_cost_structure"))
    util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.mrp_workcenter_view_inherit"))
    util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.action_cost_struct_mrp_production"))
    util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.mrp_production_form_inherit_view6"))
    util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.action_cost_struct_product_template"))
    util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.product_product_inherit_form_view_cost_structure"))
