from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_au.report_payment_receipt_document")
