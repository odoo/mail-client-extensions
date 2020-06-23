# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.ticket", "is_overdue")
    util.rename_field(
        cr, "helpdesk.ticket", "is_so_button_visible", "display_create_so_button_primary", update_references=True
    )
    util.create_column(cr, "helpdesk_ticket", "sale_order_id", "int4")
    cr.execute(
        """
            UPDATE helpdesk_ticket t
               SET sale_order_id = p.sale_order_id
              FROM project_project p
             WHERE t.project_id = p.id
               AND t.sale_order_id IS NULL
        """
    )
    cr.execute(
        """
            UPDATE helpdesk_ticket t
               SET sale_order_id = pt.sale_order_id
              FROM project_task pt
             WHERE t.task_id = pt.id
               AND t.sale_order_id IS NULL
        """
    )
    cr.execute(
        """
            UPDATE helpdesk_ticket t
               SET partner_id = s.partner_id
              FROM sale_order s
             WHERE t.sale_order_id = s.id
               AND t.partner_id IS NULL
        """
    )
