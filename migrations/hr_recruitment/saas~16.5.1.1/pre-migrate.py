from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_recruitment.hr_employee_view_search")
    util.remove_record(cr, "hr_recruitment.hr_employee_action_from_department")
    util.create_column(cr, "hr_applicant", "email_normalized", "varchar")

    util.explode_execute(
        cr,
        """
        UPDATE hr_applicant
           SET email_normalized=lower(substring(email_from, '([^ ,;<@]+@[^> ,;]+)'))
         WHERE email_from IS NOT NULL
        """,
        table="hr_applicant",
    )
    util.create_column(cr, "hr_applicant", "partner_phone_sanitized", "varchar")
    util.create_column(cr, "hr_applicant", "partner_mobile_sanitized", "varchar")
    util.remove_field(cr, "hr.job", "hr_responsible_id")
