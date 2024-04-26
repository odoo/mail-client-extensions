from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_product", "service_upsell_warning", "boolean", default=False)
    util.create_column(cr, "product_product", "service_upsell_threshold", "float8")

    util.create_column(cr, "account_analytic_line", "is_so_line_edited", "boolean")
    util.remove_field(cr, "account.analytic.line", "non_allow_billable")
    # 'non_billable_timesheet' is no more a valid timesheet_invoice_type value as it is
    # related to non_allow_billable field value, which is removed.
    cr.execute(
        """
        UPDATE account_analytic_line
           SET timesheet_invoice_type = 'non_billable'
         WHERE timesheet_invoice_type = 'non_billable_timesheet'
        """
    )
    cr.execute(
        """
        DELETE
          FROM ir_model_fields_selection
         WHERE value = 'non_billable_timesheet'
           AND field_id = (
              SELECT id
              FROM ir_model_fields
             WHERE name = 'timesheet_invoice_type' AND model = 'account.analytic.line'
           )
        """
    )

    cr.execute(
        """
        UPDATE project_project
           SET pricing_type = 'task_rate'
         WHERE bill_type = 'customer_task'
        """
    )
    util.remove_field(cr, "project.project", "bill_type")

    util.remove_field(cr, "project.task", "bill_type")
    util.remove_field(cr, "project.task", "display_create_order")
    util.remove_field(cr, "project.task", "non_allow_billable")
    util.remove_column(cr, "project_task", "timesheet_product_id")  # This field will be a related field

    util.create_column(cr, "sale_order_line", "has_displayed_warning_upsell", "boolean", default=False)
    util.create_column(cr, "sale_order_line", "remaining_hours", "float8", default=0)

    product_uom_hour_id = util.ref(cr, "uom.product_uom_hour")
    if product_uom_hour_id:
        # UPDATE the remaining hours for SOLs containing a prepaid service product
        cr.execute(
            """
            WITH time_uom AS (
                SELECT u.id,
                       u.category_id,
                       u.factor,
                       u_hours.factor AS hours_factor,
                       u_hours.rounding
                  FROM uom_uom u
                  JOIN uom_uom u_hours ON u.category_id = u_hours.category_id
                 WHERE u_hours.id = %s
            ),
            prepaid_service_sols AS (
                SELECT sol.id,
                       (sol.product_uom_qty - sol.qty_delivered) AS qty_left,
                       tu.factor,
                       tu.hours_factor,
                       tu.rounding
                  FROM sale_order_line sol
                  JOIN product_product pp ON sol.product_id = pp.id
                  JOIN product_template pt ON pp.product_tmpl_id = pt.id
                  JOIN time_uom tu ON tu.id = sol.product_uom
                 WHERE pt.invoice_policy = 'order'
                   AND (pt.service_type = 'timesheet' OR pt.type = 'service')
                   AND sol.product_uom_qty <> sol.qty_delivered
            )
            UPDATE sale_order_line sol
               SET remaining_hours = (CEIL(pss.qty_left / pss.factor * pss.hours_factor / pss.rounding) * pss.rounding)::float8
              FROM prepaid_service_sols pss
             WHERE sol.id = pss.id
            """,
            [product_uom_hour_id],
        )

    util.remove_view(cr, "sale_timesheet.timesheet_view_tree_sale")
    util.remove_view(cr, "sale_timesheet.sale_order_portal_template_inherit")
    util.remove_view(cr, "sale_timesheet.portal_invoice_page_inherit_timesheet")
    util.remove_view(cr, "sale_timesheet.report_invoice_document")
    util.remove_view(cr, "sale_timesheet.quick_create_task_form_sale_timesheet")

    # Remove view from sale_timesheet_edit (module merged with sale_timesheet)
    util.remove_view(cr, "sale_timesheet.project_task_view_form_inherit_sale_timesheet_edit")

    util.remove_model(cr, "project.task.create.sale.order")

    util.remove_constraint(cr, "project_project", "project_project_timesheet_product_required_if_billable_and_time")
