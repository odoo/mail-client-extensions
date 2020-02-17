# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "sale.order.line", "product_template_id", "sale_product_configurator", "sale")

    util.create_column(cr, "account_move", "team_id", "int4")
    util.create_column(cr, "account_move", "partner_shipping_id", "int4")
    cr.execute(
        """
        UPDATE account_move m
           SET team_id = i.team_id,
               partner_shipping_id = i.partner_shipping_id
          FROM account_invoice i
         WHERE i.move_id = m.id
    """
    )
