from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_it.tax_report_vat")
