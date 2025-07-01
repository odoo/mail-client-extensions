from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, model="account.payment.register", fieldname="sdd_mandate_usable")
