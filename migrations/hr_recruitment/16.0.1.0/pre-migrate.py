from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "hr_applicant_res_users_interviewers_rel", "hr_applicant", "res_users")

    if util.column_exists(cr, "hr_applicant", "interviewer_id"):
        cr.execute(
            """
                INSERT INTO hr_applicant_res_users_interviewers_rel
                     SELECT id, interviewer_id
                       FROM hr_applicant
                      WHERE interviewer_id IS NOT NULL
            """
        )

    util.remove_column(cr, "hr_applicant", "interviewer_id")
    util.rename_field(cr, "hr.applicant", "interviewer_id", "interviewer_ids")
