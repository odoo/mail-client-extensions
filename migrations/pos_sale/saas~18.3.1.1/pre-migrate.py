from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_sale.res_partner_view_buttons_pos_sale")
