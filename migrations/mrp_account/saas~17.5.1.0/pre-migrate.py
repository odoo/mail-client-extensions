from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_account.view_production_tree_view_inherit")
    util.remove_view(cr, "mrp_account.mrp_bom_form_view_inherited")

    util.remove_field(cr, "mrp.production", "analytic_precision")
    util.remove_field(cr, "mrp.production", "analytic_account_ids")
    util.remove_field(cr, "mrp.production", "distribution_analytic_account_ids")

    util.remove_field(cr, "mrp.bom", "analytic_precision")
    util.remove_field(cr, "mrp.bom", "analytic_account_ids")
    util.remove_field(cr, "mrp.bom", "distribution_analytic_account_ids")
    util.remove_field(cr, "mrp.bom", "analytic_distribution")
