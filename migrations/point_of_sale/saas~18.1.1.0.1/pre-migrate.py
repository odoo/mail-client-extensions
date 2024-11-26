from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.session", "login_number")
    util.remove_field(cr, "pos.session", "sequence_number")
    util.rename_field(cr, "pos.order", "general_note", "general_customer_note")
    util.delete_unused(cr, "point_of_sale.product_category_pos")
    util.remove_field(cr, "res.config.settings", "module_pos_paytm")
