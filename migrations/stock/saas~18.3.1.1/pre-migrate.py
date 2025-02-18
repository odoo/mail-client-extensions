from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "stock.lot.report")
    util.remove_field(cr, "stock.lot", "last_delivery_partner_id")
    util.remove_field(cr, "res.partner", "picking_warn")
