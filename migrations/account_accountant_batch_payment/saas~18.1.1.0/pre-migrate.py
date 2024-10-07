from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account.batch.payment.rejection")
