from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "documents_hr_recruitment.documents_recruitment_new_tag")
    util.remove_record(cr, "documents_hr_recruitment.documents_applicant_rule")
