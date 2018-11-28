# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for model in {"hr.leave", "hr.leave.allocation"}:
        table = util.table_of_model(cr, model)
        if not util.table_exists(cr, table):
            continue
        util.rename_field(cr, model, "number_of_days", "number_of_days_display")
        util.rename_field(cr, model, "number_of_days_temp", "number_of_days")
        util.rename_field(cr, model, "number_of_hours", "number_of_hours_display")
        util.remove_column(cr, table, "number_of_days_display")

        util.create_column(cr, table, "mode_company_id", "int4")

    util.create_column(cr, "hr_leave", "request_unit_half", "boolean")
    if util.column_exists(cr, "hr_leave", "request_unit_all"):
        cr.execute("UPDATE hr_leave SET request_unit_half = (request_unit_all = 'half')")

    util.remove_field(cr, "hr.leave", "request_date_to_period")
    util.remove_field(cr, "hr.leave", "request_unit_all")
    util.remove_field(cr, "hr.leave", "request_unit_day")

    util.create_column(cr, "hr_leave_type", "allocation_type", "varchar")
    cr.execute("""
        UPDATE hr_leave_type
           SET allocation_type = CASE WHEN "limit" = true
                                        THEN 'no'
                                      WHEN employee_applicability IN ('both', 'allocation')
                                        THEN 'fixed_allocation'
                                      ELSE 'fixed'
                                      END
    """)
    if util.column_exists(cr, "hr_leave_type", "request_unit"):
        cr.execute("""
            UPDATE hr_leave_type
               SET request_unit='day'
             WHERE request_unit='half'
        """)

    for field in {"limit", "employee_applicability", "accrual", "negative", "balance_limit"}:
        util.remove_field(cr, "hr.leave.type", field)
