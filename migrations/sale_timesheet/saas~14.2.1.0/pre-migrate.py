# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.timesheet_view_tree_sale")
    util.remove_field(cr, "account.analytic.line", "non_allow_billable")
    util.remove_field(cr, "project.task", "display_create_order")
    util.remove_field(cr, "project.task", "non_allow_billable")
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
