# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "event_registration", "is_paid", "boolean")
    cr.execute(
        """
        UPDATE event_registration r
           SET is_paid = (o.state = 'paid')
          FROM sale_order o
         WHERE o.id = r.sale_order_id
    """
    )

    util.remove_view(cr, "event_sale.view_event_registration_ticket_search")
    util.remove_view(cr, "event_sale.event_type_view_form_inherit_sale")
