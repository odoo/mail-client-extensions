from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ec_edi.report_invoice_with_payments")
