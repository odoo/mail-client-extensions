from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_management_renting.sale_order_form_view")
