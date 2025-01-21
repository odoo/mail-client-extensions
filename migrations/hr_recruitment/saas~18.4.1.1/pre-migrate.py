from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_recruitment.ir_actions_server_refuse_applicant")
    util.remove_field(cr, "applicant.get.refuse.reason", "applicant_emails")
    util.remove_field(cr, "applicant.get.refuse.reason", "single_applicant_email")
    if not util.module_installed(cr, "hr_recruitment_integration_base"):
        util.remove_field(cr, "hr.job", "date_from")
        util.remove_field(cr, "hr.job", "date_to")
    else:
        util.move_field_to_module(cr, "hr.job", "date_from", "hr_recruitment", "hr_recruitment_integration_base")
        util.move_field_to_module(cr, "hr.job", "date_to", "hr_recruitment", "hr_recruitment_integration_base")
    util.remove_field(cr, "res.config.settings", "group_applicant_cv_display")
