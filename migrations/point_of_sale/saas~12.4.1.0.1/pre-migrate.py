# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "point_of_sale.picking_type_posout", noupdate=True)
    util.force_noupdate(cr, "point_of_sale.seq_picking_type_posout", noupdate=True)
    util.remove_field(cr, "pos.config", "stock_location_id")
    util.remove_field(cr, "pos.config", "iface_start_categ_domain_ids")
    util.remove_field(cr, "pos.order", "invoice_id")
    if not util.column_exists(cr, "pos_order", "currency_rate"):
        # module `pos_sale` already add this column, but as `numeric`
        util.create_column(cr, "pos_order", "currency_rate", "float8")
    cr.execute(
        """
        UPDATE pos_order o
           SET currency_rate=1.0
          FROM res_company cmpy,
               product_pricelist pp
         WHERE cmpy.id=o.company_id
           AND pp.id=o.pricelist_id
           AND pp.currency_id=cmpy.currency_id
           AND o.currency_rate IS NULL
        """
    )
    cr.execute(
        """
        UPDATE pos_order o
           SET location_id=p.location_id
          FROM stock_picking p
         WHERE p.id=o.picking_id
        """
    )
    cr.execute(
        """
        UPDATE pos_order_line l
           SET company_id=o.company_id
          FROM pos_order o
         WHERE l.order_id=o.id
        """
    )
    util.create_column(cr, "stock_warehouse", "pos_type_id", "int4")
    util.remove_record(cr, "point_of_sale.access_product_price_history_pos_manager")
