from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE hr_salary_attachment a
        SET
            deduction_type_id = CASE deduction_type
                WHEN 'attachment' THEN %s
                WHEN 'assignment' THEN %s
                WHEN 'child_support' THEN %s
                END,
            no_end_date = (deduction_type = 'child_support')
        WHERE deduction_type_id IS NULL
    """
    query = cr.mogrify(
        query,
        [
            util.ref(cr, "hr_payroll.hr_salary_attachment_type_attachment"),
            util.ref(cr, "hr_payroll.hr_salary_attachment_type_assignment"),
            util.ref(cr, "hr_payroll.hr_salary_attachment_type_child_support"),
        ],
    ).decode()
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="hr_salary_attachment", alias="a"))
    util.remove_column(cr, "hr_salary_attachment", "deduction_type")

    util.update_record_from_xml(cr, "hr_payroll.mail_template_new_payslip")
