from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "payment_demo.payment_method_demo", keep_xmlids=False)
