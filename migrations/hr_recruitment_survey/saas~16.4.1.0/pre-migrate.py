from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr, "hr_recruitment.group_hr_recruitment_interviewer", from_module="hr_recruitment_survey"
    )
