# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key='product.volume_in_cubic_feet'")
    value = cr.fetchone()
    if value != "1":
        cr.execute(
            """
            UPDATE stock_package_type p
               SET height = p.height * 1000,
                   width = p.width * 1000,
                   packaging_length = p.packaging_length * 1000
            """
        )

    util.remove_menus(cr, [util.ref(cr, "delivery.menu_delivery"), util.ref(cr, "delivery.menu_delivery_packagings")])
    util.remove_record(cr, "delivery.action_delivery_packaging_view")
    util.remove_view(cr, "delivery.product_packaging_delivery_form")
    util.remove_view(cr, "delivery.product_packaging_delivery_tree")
    util.remove_view(cr, "delivery.view_quant_package_packaging_tree")
    util.rename_field(cr, "choose.delivery.package", "delivery_packaging_id", "delivery_package_type_id")
