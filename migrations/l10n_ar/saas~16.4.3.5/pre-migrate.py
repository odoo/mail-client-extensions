from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ar.report_invoice_with_payments")
    util.remove_view(cr, "l10n_ar.report_invoice")
