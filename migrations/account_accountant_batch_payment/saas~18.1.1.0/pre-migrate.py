from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account.batch.payment.rejection")
    util.remove_field(cr, "bank.rec.widget.line", "batch_pay_content")
