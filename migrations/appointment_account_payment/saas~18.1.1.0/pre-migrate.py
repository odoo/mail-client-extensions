from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "appointment_account_payment.product_category_appointment")
