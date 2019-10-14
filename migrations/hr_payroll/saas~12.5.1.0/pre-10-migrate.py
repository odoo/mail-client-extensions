# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "hourly_wage", "numeric")
    util.create_column(cr, "hr_contract", "date_generated_from", "timestamp without time zone")
    util.create_column(cr, "hr_contract", "date_generated_to", "timestamp without time zone")

    def_date = datetime.utcnow().replace(hour=0, minute=0, second=0).isoformat()
    cr.execute(
        """
        UPDATE hr_contract
           SET hourly_wage=0,
               date_generated_from=%s,
               date_generated_to=%s
        """,
        [def_date, def_date],
    )

    util.create_column(cr, "hr_payslip", "warning_message", "varchar")
    util.create_column(cr, "hr_payroll_structure", "active", "boolean")

    cr.execute("UPDATE hr_payroll_structure SET active=TRUE")

    if util.table_exists(cr, "hr_payroll_structure_type"):
        util.create_column(cr, "hr_payroll_structure_type", "default_work_entry_type_id", "int4")
        util.create_column(cr, "hr_payroll_structure_type", "wage_type", "varchar")
        cr.execute(
            """
            UPDATE hr_payroll_structure_type
               SET default_work_entry_type_id=%s,
                   wage_type='monthly'
            """,
            [util.ref(cr, "hr_work_entry.work_entry_type_attendance")],
        )

    util.create_column(cr, "hr_work_entry_type", "round_days", "varchar")
    util.create_column(cr, "hr_work_entry_type", "round_days_type", "varchar")

    cr.execute("UPDATE hr_work_entry_type SET round_days_type='DOWN', round_days='NO'")

    util.create_column(cr, "hr_payslip_employees", "structure_id", "int4")

    util.delete_unused(cr, "hr_payroll_structure_type", ["hr_payroll.structure_type_employee"])
