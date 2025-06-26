from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "mrp_account_enterprise.action_cost_struct_mrp_production")
    util.remove_record(cr, "mrp_account_enterprise.action_cost_struct_product_template")
    util.remove_view(cr, "mrp_account_enterprise.product_template_inherit_form_view_cost_structure")
    util.remove_view(cr, "mrp_account_enterprise.product_product_inherit_form_view_cost_structure")
    util.remove_view(cr, "mrp_account_enterprise.mrp_cost_structure")
    util.remove_model(cr, "report.mrp_account_enterprise.mrp_cost_structure")
    util.remove_model(cr, "report.mrp_account_enterprise.product_template_cost_structure")
