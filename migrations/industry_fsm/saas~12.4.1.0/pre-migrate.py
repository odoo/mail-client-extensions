# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "fsm_state", "varchar")
    cr.execute(
        """
        UPDATE project_task t
           SET fsm_state = CASE WHEN t.fsm_is_done AND t.sale_line_id IS NOT NULL
                                     AND p.allow_billable AND p.timesheet_product_id IS NOT NULL
                                THEN 'sold'
                                WHEN t.fsm_is_done THEN 'validated'
                                ELSE 'draft'
                            END
          FROM project_project p
         WHERE p.id = t.project_id
    """
    )
    util.remove_field(cr, "project.task", "fsm_is_done")
    util.remove_field(cr, "project.task.create.sale.order", "material_line_ids")
    util.remove_field(cr, "project.task.create.sale.order", "product_template_ids")

    eb = util.expand_braces
    util.rename_xmlid(cr, "industry_fsm.group_product_task_map_user", "industry_fsm.group_fsm_user")
    util.rename_xmlid(cr, *eb("industry_fsm.project_task_view_form{_fsm,}"), noupdate=False)
    util.rename_xmlid(cr, *eb("industry_fsm.project_task_view_search{,_fsm}"), noupdate=False)

    util.remove_view(cr, "industry_fsm.view_form_project_inherit_quotation")
    util.remove_view(cr, "industry_fsm.view_form_fsm_inherit_quotation")
    util.remove_view(cr, "industry_fsm.project_task_create_sale_order_view_form_inherit")
    util.remove_view(cr, "industry_fsm.view_task_form2_inherit")
    util.remove_view(cr, "industry_fsm.project_view_form_simplified_inherit")
