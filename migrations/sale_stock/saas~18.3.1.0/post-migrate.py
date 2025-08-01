from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "sale_stock.stock_picking_rule_portal")
