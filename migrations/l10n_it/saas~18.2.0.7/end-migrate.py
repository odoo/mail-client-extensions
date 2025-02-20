from odoo.upgrade import util


def migrate(cr, version):
    # l10n_it.tax_report_vat is used in a local upgrade script in l10n_it
    util.remove_record(cr, "l10n_it.tax_report_vat")
