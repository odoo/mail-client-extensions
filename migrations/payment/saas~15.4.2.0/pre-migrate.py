from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "payment.acquirer", "support_authorization", "support_manual_capture")
    util.rename_field(cr, "payment.acquirer", "support_fees_computation", "support_fees")

    util.remove_column(cr, "payment_acquirer", "support_manual_capture")
    util.remove_column(cr, "payment_acquirer", "support_fees")
    util.remove_column(cr, "payment_acquirer", "support_tokenization")
    util.remove_column(cr, "payment_acquirer", "support_refund")
