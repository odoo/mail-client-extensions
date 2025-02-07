from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_cz_reports.view_company_form")
