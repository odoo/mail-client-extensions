# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "base_automation", "is_sale_order_alert", "boolean")
    cr.execute(
        """
            WITH soa AS (
                 SELECT automation_id
                   FROM sale_order_alert
                  WHERE automation_id IS NOT NULL
               GROUP BY automation_id
            )
            UPDATE base_automation a
               SET is_sale_order_alert = true
              FROM soa
             WHERE a.id = soa.automation_id
        """
    )

    util.create_column(cr, "sale_order_alert", "action_id", "integer")
    cr.execute(
        """
            WITH actions AS (
                SELECT ias.id,
                       ias.base_automation_id
                  FROM ir_act_server AS ias
                       INNER JOIN base_automation AS ba
                       ON ba.id = ias.base_automation_id
                 WHERE ba.is_sale_order_alert = true
            )
            UPDATE sale_order_alert
               SET action_id = act.id
              FROM actions AS act
             WHERE automation_id = act.base_automation_id
        """
    )

    util.remove_field(cr, "sale.order.log.report", "recurring_yearly_graph")
    util.remove_field(cr, "sale.order.log.report", "recurring_monthly_graph")
    util.remove_field(cr, "sale.order.log.report", "amount_signed_graph")
