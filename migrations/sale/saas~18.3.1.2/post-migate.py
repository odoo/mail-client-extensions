from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "sale.sale_order_rule_portal")
    util.update_record_from_xml(cr, "sale.sale_order_line_rule_portal")
