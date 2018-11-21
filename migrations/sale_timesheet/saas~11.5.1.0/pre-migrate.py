# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.analytic.line", "timesheet_revenue")

    util.create_column(cr, "project_project", "sale_order_id", "int4")
    util.create_column(cr, "project_project", "billable_type", "varchar")
    cr.execute("""
        UPDATE project_project
           SET billable_type = CASE WHEN sale_line_id IS NOT NULL THEN 'task_rate' ELSE 'no' END
    """)
    cr.execute(
        """
        UPDATE project_project p
           SET sale_order_id=s.order_id
          FROM sale_order_line s
         WHERE p.sale_line_id=s.id
    """
    )

    util.create_column(cr, "project_task", "billable_type", "varchar")
    cr.execute(
        """
        UPDATE project_task
           SET billable_type = CASE WHEN sale_line_id IS NOT NULL THEN 'task_rate' ELSE 'no' END
    """
    )

    util.remove_view(cr, "sale_timesheet.product_template_search_view_sale_timesheet")
