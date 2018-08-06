# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "point_of_sale.res_users_form_view", "point_of_sale.res_users_view_form")

    util.rename_field(cr, "pos.config", "iface_invoicing", "module_account_invoicing")
    util.remove_field(cr, "pos.config", "group_sale_pricelist")
    util.remove_field(cr, "pos.config", "group_pricelist_item")

    env = util.env(cr)
    sales_price = env.user.has_group("product.group_sale_pricelist")
    if not sales_price:
        setting = False
    else:
        setting = "percentage" if env.user.has_group("product.group_product_pricelist") else "formula"

    ICP = env["ir.config_parameter"]
    ICP.set_param("point_of_sale.pos_sales_price", str(sales_price))
    ICP.set_param("point_of_sale.pos_pricelist_setting", setting)
