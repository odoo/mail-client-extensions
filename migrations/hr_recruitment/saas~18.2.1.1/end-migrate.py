from odoo.upgrade import util


def migrate(cr, version):
    # We remove the candidate model in the end script as we want to be able to
    # migrate the data from it into other models and this model is used by many modules.
    util.remove_model(cr, "hr.candidate")
    util.update_record_from_xml(cr, "hr_recruitment.stage_job1")
    util.delete_unused(cr, "hr_recruitment.hr_candidate_comp_rule")
    util.delete_unused(cr, "hr_recruitment.hr_candidate_interviewer_rule")
    util.recompute_fields(cr, "hr.applicant", ["partner_phone_sanitized", "email_from", "partner_phone"])
    util.remove_column(cr, "hr_applicant", "_upg_orig_candidate_id")
    util.remove_column(cr, "hr_applicant", "candidate_id")
