from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "stock.stock_package_comp_rule", fields=["name"])
