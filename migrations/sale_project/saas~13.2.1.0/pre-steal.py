# -*- coding: utf-8 -*-
from typing import NamedTuple
from odoo.upgrade import util


class Field(NamedTuple):
    model: str
    name: str
    type: str = None
    init_sql: str = None


def migrate(cr, version):
    fields = [
        Field("product.template", "service_tracking", "varchar", "UPDATE product_template SET service_tracking = 'no'"),
        Field("product.template", "project_id"),
        Field("product.template", "project_template_id"),
        Field("project.project", "sale_line_id", "integer"),
        Field("project.project", "sale_order_id", "integer"),
        Field("project.task", "sale_order_id", "integer"),
        Field(
            "project.task",
            "sale_line_id",
            "integer",
            """
                WITH sli AS (
                    SELECT t.id, COALESCE(p.sale_order_id, j.sale_line_id) as sol_id,
                           r.commercial_partner_id as cp_id
                      FROM project_task t
                      JOIN project_project j ON j.id = t.project_id
                      JOIN res_partner r ON r.id = t.partner_id
                 LEFT JOIN project_task p ON p.id = t.parent_id
                ),
                slip AS (
                   SELECT sli.id, sli.sol_id
                     FROM sli
                     JOIN sale_order_line sol ON sol.id = sli.sol_id
                     JOIN res_partner p ON p.id = sol.order_partner_id
                    WHERE sli.cp_id = p.commercial_partner_id
                )
                UPDATE project_task t
                   SET sale_line_id = slip.sol_id
                  FROM slip
                 WHERE slip.id = t.id
        """,
        ),
        Field("project.task", "project_sale_order_id"),
        Field("sale.order", "tasks_ids"),
        Field("sale.order", "tasks_count"),
        Field("sale.order", "visible_project"),
        Field("sale.order", "project_id", "integer"),
        Field("sale.order", "project_ids"),
        Field("sale.order.line", "project_id", "integer"),
        Field("sale.order.line", "task_id", "integer"),
        Field(
            "sale.order.line",
            "is_service",
            "boolean",
            """
            UPDATE sale_order_line l
               SET is_service = (t.type = 'service')
              FROM product_product p
              JOIN product_template t ON t.id = p.product_tmpl_id
             WHERE p.id = l.product_id
        """,
        ),
    ]

    for field in fields:
        util.move_field_to_module(cr, field.model, field.name, "sale_timesheet", "sale_project")
        if field.type:
            table = util.table_of_model(cr, field.model)
            if util.create_column(cr, table, field.name, field.type) and field.init_sql:
                cr.execute(field.init_sql)

    moved = """
        access_sale_order_line_project_manager
        access_sale_order_project_manager
        sale_order_line_rule_project_manager
        project_task_view_form_inherit_sale_line_editable
        project_task_view_search
    """
    for move in util.splitlines(moved):
        util.rename_xmlid(cr, f"sale_timesheet.{move}", f"sale_project.{move}")

    util.rename_xmlid(
        cr,
        "sale_timesheet.project_project_view_tree_inherit_sale_timesheet",
        "sale_project.project_project_view_tree_inherit_sale_project",
    )
