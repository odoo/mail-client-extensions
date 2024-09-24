from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "l10n_nl_reports_sbr_password")
    util.remove_field(cr, "l10n_nl_reports_sbr.tax.report.wizard", "password")
