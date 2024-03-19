from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment.pay_meth_link")

    util.rename_xmlid(cr, "payment.transaction_status", "payment.state_header")
