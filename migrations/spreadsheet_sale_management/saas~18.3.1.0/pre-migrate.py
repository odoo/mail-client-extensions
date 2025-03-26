from odoo.upgrade import util


def migrate(cr, version):
    query = "UPDATE ir_rule SET perm_read = true WHERE id=%s"
    for xmlid in [
        "spreadsheet_sale_management.sale_order_spreadsheet_rule_salesman",
        "spreadsheet_sale_management.sale_order_spreadsheet_rule_salesman_all_leads",
    ]:
        util.if_unchanged(cr, xmlid, lambda cr, xmlid: cr.execute(query, [util.ref(cr, xmlid)]))
