from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_nl.vat.pay.wizard")
    util.remove_model(cr, "l10n_nl.tax.report.handler")
    util.remove_record(cr, "l10n_nl_reports.action_open_closing_entry")
