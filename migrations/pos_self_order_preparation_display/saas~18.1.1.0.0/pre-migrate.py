from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos_preparation_display.order", "pos_takeaway")
