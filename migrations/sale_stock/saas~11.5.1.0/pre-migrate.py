# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_field(cr, "res.config.settings", "module_sale_order_dates")

    util.move_field_to_module(cr, "sale.order", "effective_date", "sale", "sale_stock")

    util.rename_xmlid(cr, *eb("sale_stock.access_{procurement,stock}_rule_salemanager"))
    util.rename_xmlid(cr, *eb("sale_stock.access_{procurement,stock}_rule"))

    util.remove_view(cr, "sale_stock.product_template_view_form_view_inherit_invoice_policy")

    if util.create_column(cr, "sale_order", "effective_date", "date"):
        util.parallel_execute(
            cr,
            util.explode_query(
                cr,
                """
            UPDATE sale_order
            SET effective_date=p.thedate
            FROM (select min(s.date_done) as thedate, s.sale_id
                   from stock_picking s inner join stock_location l on s.location_dest_id=l.id
                  where s.date_done IS NOT NULL
                    and s.state='done'
                    and l.usage='customer'
                  group by sale_id) as p
            WHERE sale_order.id=p.sale_id
                """,
                prefix="sale_order.",
            ),
        )
