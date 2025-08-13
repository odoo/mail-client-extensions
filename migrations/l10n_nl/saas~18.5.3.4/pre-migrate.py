from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_nl.tax_report_balance")
    for btw in ["1", "1a", "1b", "1c", "1d", "1e", "2", "2a", "4", "4a", "4b"]:
        util.remove_record(cr, f"l10n_nl.tax_report_rub_btw_{btw}")
