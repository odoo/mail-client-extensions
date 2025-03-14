from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.applicant", "response_state")
    util.create_column(cr, "survey_user_input", "applicant_id", "int4")

    cr.execute(
        """
        UPDATE survey_user_input i
           SET applicant_id = a.id
          FROM hr_applicant a
         WHERE a.response_id = i.id
        """
    )
    util.remove_field(cr, "hr.applicant", "response_id")
