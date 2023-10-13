# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "registration.editor.line", "mobile")
    util.rename_field(cr, "event.registration", "payment_status", "sale_status")
    util.change_field_selection_values(cr, "event.registration", "sale_status", {"paid": "sold"})
    util.create_column(cr, "event_registration", "sale_status", "varchar")
    cr.execute(
        """
            UPDATE event_registration reg
               SET sale_status = CASE
                    WHEN reg.sale_order_id IS NULL OR so_l.price_total = 0 THEN 'free'
                    WHEN is_paid = false AND reg.state = 'open' THEN 'free'
                    WHEN is_paid = true THEN 'sold'
                    ELSE 'to_pay'
                    END
              FROM sale_order_line so_l
             WHERE so_l.id = reg.sale_order_line_id or reg.sale_order_id IS NULL
        """
    )
    util.remove_field(cr, "event.registration", "is_paid")
    util.remove_field(cr, "event.sale.report", "is_paid")
    util.rename_field(cr, "event.sale.report", "payment_status", "sale_status")
    util.change_field_selection_values(cr, "event.sale.report", "sale_status", {"paid": "sold"})
    util.remove_field(cr, "registration.editor", "seats_available_insufficient")
