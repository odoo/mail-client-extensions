from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "point_of_sale_show_predefined_scenarios")
