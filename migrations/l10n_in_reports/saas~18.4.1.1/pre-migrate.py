from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_in_reports.balance.sheet.report.handler")
