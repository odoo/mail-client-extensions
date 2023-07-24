from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_cl.report_invoice_with_payments")
