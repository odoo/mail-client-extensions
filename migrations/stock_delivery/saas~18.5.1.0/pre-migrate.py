from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "stock_delivery.view_quant_package_weight_form", "stock_delivery.stock_package_view_form")
