from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_sale.product_template_form_view")
