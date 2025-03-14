from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.salary.attachment", "deduction_type", drop_column=False)
    util.create_column(cr, "hr_salary_attachment", "no_end_date", "boolean")

    util.create_m2m(cr, "hr_employee_hr_salary_attachment_rel", "hr_employee", "hr_salary_attachment")
    cr.execute(
        """
        INSERT INTO hr_employee_hr_salary_attachment_rel(hr_employee_id, hr_salary_attachment_id)
             SELECT employee_id, id
               FROM hr_salary_attachment
              WHERE employee_id is NOT NULL
    """
    )
    util.update_field_usage(cr, "hr.salary.attachment", "employee_id", "employee_ids")
    util.remove_field(cr, "hr.salary.attachment", "employee_id")

    util.remove_field(cr, "hr.payslip.line", "note")
    util.remove_field(cr, "hr.payroll.edit.payslip.line", "note")

    util.convert_field_to_translatable(cr, "hr.salary.rule", "note")
