# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO product_pricing (currency_id,duration,price,unit,product_template_id)
             SELECT currency_id,duration,price,unit,product_template_id
               FROM rental_pricing
        """
    )
    util.remove_model(cr, "rental.pricing")
    util.remove_field(cr, "sale.order.line", "rental_updatable")
    util.remove_view(cr, "sale_renting.product_template_rental_tree_view")
    util.remove_view(cr, "sale_renting.product_template_rental_kanban_view")
