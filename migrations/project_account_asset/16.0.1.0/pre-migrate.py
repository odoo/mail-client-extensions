from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_account_asset.project_project_view_form")
