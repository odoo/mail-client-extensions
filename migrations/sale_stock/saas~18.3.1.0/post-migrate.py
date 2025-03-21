from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale_stock.stock_picking_rule_portal", util.update_record_from_xml)
