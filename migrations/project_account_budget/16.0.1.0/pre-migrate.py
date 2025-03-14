from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_account_budget.project_project_form_view_inherited")
