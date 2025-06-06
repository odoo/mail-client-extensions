from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_us_reports.check_register_report")
    util.remove_model(cr, "l10n_us.report.handler")
