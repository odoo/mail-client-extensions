from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.location", "posx")
    util.remove_field(cr, "stock.location", "posy")
    util.remove_field(cr, "stock.location", "posz")
