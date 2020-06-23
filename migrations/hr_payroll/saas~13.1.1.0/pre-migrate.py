# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_payslip", "sum_worked_hours", "float8")
    util.create_column(cr, "hr_payslip", "normal_wage", "integer")  # computed via ORM in end-

    cr.execute(
        """
        WITH sum_wh AS (
            SELECT payslip_id, SUM(number_of_hours) as swh
              FROM hr_payslip_worked_days
          GROUP BY payslip_id
        )
        UPDATE hr_payslip p
           SET sum_worked_hours = w.swh
          FROM sum_wh w
         WHERE p.id = w.payslip_id
    """
    )

    util.create_column(cr, "hr_payslip_worked_days", "is_paid", "boolean")
    cr.execute(
        """
        WITH unpaid AS (
            SELECT hr_payroll_structure_id, array_agg(hr_work_entry_type_id) wet_ids
              FROM hr_payroll_structure_hr_work_entry_type_rel
          GROUP BY hr_payroll_structure_id
        )

        UPDATE hr_payslip_worked_days w
           SET is_paid = NOT(u.wet_ids @> ARRAY[w.work_entry_type_id])
          FROM hr_payslip s, unpaid u
         WHERE s.id = w.payslip_id
           AND u.hr_payroll_structure_id = s.struct_id
           AND w.is_paid IS NULL
    """
    )
    cr.execute("UPDATE hr_payslip_worked_days SET is_paid = false WHERE is_paid IS NULL")

    util.create_column(cr, "hr_payroll_structure_type", "default_struct_id", "int4")
    cr.execute(
        """
        WITH def_struct AS (
            SELECT type_id, (array_agg(id ORDER BY regular_pay DESC))[1] as struct_id
              FROM hr_payroll_structure
          GROUP BY type_id
        )
        UPDATE hr_payroll_structure_type t
           SET default_struct_id = d.struct_id
          FROM def_struct d
         WHERE d.type_id = t.id
    """
    )

    util.remove_field(cr, "hr.payroll.structure", "regular_pay")
