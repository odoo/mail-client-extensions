from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_mrp_account.mrp_production_form_view_inherit_project_mrp_account")
