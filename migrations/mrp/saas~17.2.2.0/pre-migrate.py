from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.bom.line", "manual_consumption_readonly")
    util.remove_field(cr, "mrp.production", "use_auto_consume_components_lots")
    util.remove_field(cr, "stock.picking.type", "use_auto_consume_components_lots")
