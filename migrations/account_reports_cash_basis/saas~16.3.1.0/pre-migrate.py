from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports_cash_basis.search_template_extra_options")
    util.remove_view(cr, "account_reports_cash_basis.filter_cash_basis_template")
