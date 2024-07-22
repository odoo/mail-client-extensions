from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_recruitment_skills.hr_applicant_skill_interviewer_rule")
    util.update_record_from_xml(cr, "hr_recruitment_skills.hr_applicant_skill_officer_rule")
